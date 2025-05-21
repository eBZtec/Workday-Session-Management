using Microsoft.Win32;
using NetMQ;
using NetMQ.Sockets;
using SessionService.Model;
using SessionService.Service;
using System.Diagnostics;
using System.Security.Cryptography.X509Certificates;
using System.Text.Json;

public class Worker : BackgroundService
{
    private readonly EventLog _eventLog;
    private List<UserAllowed> usersAllowed;
    private List<UserSession> userSessions;
    private PublisherSocket publisher;
    private ClientInfo clientInfo;
    private DealerSocket dealer;
    private string lastUsrLogon = "";
    public static bool inAuditMode = true;

    public Worker(IHostApplicationLifetime appLifetime)
    {
        userSessions = new List<UserSession>();
        usersAllowed = new List<UserAllowed>();

        appLifetime.ApplicationStopping.Register(() =>
        {
            LogManager.Log("O serviço está sendo finalizado (ApplicationStopping).");
            publisher?.Close();
            dealer?.Close();
        });

        clientInfo = new ClientInfo();

        StartupManager.Init();

        _eventLog = new EventLog("Security")
        {
            Log = "Security"
        };
        _eventLog.EntryWritten += OnEntryWritten;
        _eventLog.EnableRaisingEvents = true;
        LogManager.LogClientInfo(clientInfo.ToString());
    }

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        while (!stoppingToken.IsCancellationRequested)
        {
            try
            {
                Console.WriteLine(clientInfo);
                await InitializeSocketsAndRun(stoppingToken);
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Worker encountered an exception: {ex.Message}. Retrying...");
                LogManager.Log($"Worker -> Exception: {ex.Message}");

                dealer?.Close();
                publisher?.Close();

                Console.WriteLine("encerrando sockets");
                LogManager.Log($"Worker -> Closing sockets...");

                await Task.Delay(TimeSpan.FromSeconds(50), stoppingToken);
            }
        }
    }

    private async Task InitializeSocketsAndRun(CancellationToken stoppingToken)
    {
        using (publisher = new PublisherSocket())
        using (dealer = new DealerSocket())
        {
            string pubUrl = "tcp://localhost:12345";
            string dealerUrl = "tcp://" + StartupManager.getServerURL();

            inAuditMode = StartupManager.getMode();

            try
            {
                InitializePublisher(publisher, pubUrl);
                InitializeDealer(dealer, dealerUrl);

                _ = Task.Run(() => WorkdayManager.Vigilance(userSessions, usersAllowed, publisher, stoppingToken));
                _ = Task.Run(() => StartupManager.HeartBeat(clientInfo, dealer, stoppingToken));
                _ = Task.Run(() => RefreshMode(stoppingToken));

                while (!stoppingToken.IsCancellationRequested)
                {
                    await HandleMessages(stoppingToken);
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Socket exception: {ex.Message}");
                LogManager.Log($"Worker -> Socket exception: {ex.Message}");

                publisher?.Close();
                dealer?.Close();
                throw;
            }
        }
    }

    private void InitializePublisher(PublisherSocket publisher, string pubUrl)
    {
        publisher.Options.CurveServer = true;
        publisher.Options.CurveCertificate = new NetMQCertificate(StartupManager.LoadCurveKeys(true), StartupManager.LoadCurveKeys(false));
        publisher.Bind(pubUrl);
        LogManager.Log($"Worker -> Publisher bound to: {pubUrl}");
    }

    private void InitializeDealer(DealerSocket dealer, string dealerUrl)
    {
        string fqdn = StartupManager.getFqdn();

        dealer.Options.Identity = System.Text.Encoding.UTF8.GetBytes(fqdn);
        dealer.Connect(dealerUrl);
        LogManager.Log($"Worker -> Dealer connected to: {dealerUrl}");
    }

    private async Task HandleMessages(CancellationToken stoppingToken)
    {
        var messageParts = new List<string>();
        TimeSpan timeout = TimeSpan.FromSeconds(20);

        if (dealer.TryReceiveMultipartStrings(timeout, ref messageParts, 2))
        {
            try
            {
                LogManager.Log($"Worker -> Message received from router");


                var rawMessage = Cryptography.processRequest(messageParts[1]);

                var messageObject = JsonSerializer.Deserialize<ServerResponse>(rawMessage) ?? new ServerResponse();

                switch (messageObject.action)
                {
                    case "interact":
                        NetMQMessage interactmessage = new NetMQMessage(2);
                        interactmessage.Append(messageObject.user);
                        interactmessage.Append(JsonSerializer.Serialize(Command.ResponseToCommand(messageObject)));
                        publisher.SendMultipartMessage(interactmessage);
                        break;

                    case "lock":
                        NetMQMessage lockmessage = new NetMQMessage(2);
                        lockmessage.Append(messageObject.user);
                        lockmessage.Append(JsonSerializer.Serialize(Command.ResponseToCommand(messageObject)));
                        publisher.SendMultipartMessage(lockmessage);

                        _ = Task.Run(() => HandleLockCase(messageObject));
                        break;

                    case "logoff":
                        NetMQMessage logoffmessage = new NetMQMessage(2);
                        logoffmessage.Append(messageObject.user);
                        logoffmessage.Append(JsonSerializer.Serialize(Command.ResponseToCommand(messageObject)));
                        publisher.SendMultipartMessage(logoffmessage);

                        _ = Task.Run(() => HandleLogoffCase(messageObject));
                        break;

                    case "notify":
                        NetMQMessage notifymessage = new NetMQMessage(2);
                        notifymessage.Append(messageObject.user);
                        notifymessage.Append(JsonSerializer.Serialize(Command.ResponseToCommand(messageObject)));
                        publisher.SendMultipartMessage(notifymessage);
                        break;

                    case "ping":
                        dealer.SendFrame(JsonSerializer.Serialize<ClientInfo>(clientInfo));
                        break;

                    case "updateHours":
                        WorkdayManager.UpdateUserAllowed(messageObject, usersAllowed, publisher);
                        break;

                    default:
                        if (messageObject.action != null)
                        {
                            LogManager.Log($"Worker -> Unknown command received: {messageObject.action}");
                        }
                        LogManager.Log($"Worker -> No response needed");
                        break;
                }
            }
            catch (Exception ex)
            {
                LogManager.Log($"HandleMessages -> Error handling message: {ex.Message}");
            }
        }
        LogManager.Log($"HandleMessages -> timeout achieved, waiting for messages");
        await Task.Delay(1000, stoppingToken);
    }

    private void OnEntryWritten(object sender, EntryWrittenEventArgs e)
    {
        switch (e.Entry.InstanceId)
        {
            case 4624: // Logon
                if ((e.Entry.ReplacementStrings[8].Equals("2") || e.Entry.ReplacementStrings[8].Equals("10")
                || e.Entry.ReplacementStrings[8].Equals("11"))
                    && !e.Entry.ReplacementStrings[11].Equals("-")
                    && e.Entry.ReplacementStrings[9].Trim().Equals("User32")
                    && !e.Entry.ReplacementStrings[5].Equals(lastUsrLogon))
                {
                    EventManager.HandleLogonEvent(e.Entry, dealer);
                    lastUsrLogon = e.Entry.ReplacementStrings[5];
                }
                userSessions = SessionManager.EnumerateSessions();
                break;

            case 4800: // Lock
                EventManager.HandleLockEvent(e.Entry, dealer);
                userSessions = SessionManager.EnumerateSessions();
                break;

            case 4801: // Unlock
                EventManager.HandleUnlockEvent(e.Entry, dealer);
                userSessions = SessionManager.EnumerateSessions();
                break;

            case 4647: // Logoff
                EventManager.HandleLogoffEvent(e.Entry, dealer);
                userSessions = SessionManager.EnumerateSessions();
                if (e.Entry.ReplacementStrings[1].Equals(lastUsrLogon))
                {
                    lastUsrLogon = "";
                }
                break;

            default:
                break;
        }
    }

    private void HandleLogoffCase(ServerResponse messageObject)
    {
        if (inAuditMode) return;
        Thread.Sleep(TimeSpan.FromSeconds(10));

        List<int> ids = SessionManager.GetSessionIDs(messageObject.user ?? "Unknown", userSessions);
        foreach (int id in ids)
        {
            SessionManager.LogoffSession(id, messageObject.user);
        }
    }

    private void HandleLockCase(ServerResponse messageObject)
    {
        if (inAuditMode) return;
        Thread.Sleep(TimeSpan.FromSeconds(10));

        List<int> ids = SessionManager.GetSessionIDs(messageObject.user ?? "Unknown", userSessions);
        foreach (int id in ids)
        {
            SessionManager.Lock(id, messageObject.user);
        }
    }

    private async Task RefreshMode(CancellationToken stoppingToken)
    {
        while (!stoppingToken.IsCancellationRequested)
        {
            var currentMode = inAuditMode;
            inAuditMode = StartupManager.getMode();
            if (currentMode != inAuditMode)
            {
                LogManager.Log($"refreshMode -> Audit mode updated, new value: {inAuditMode}");
            }
            await Task.Delay(TimeSpan.FromMinutes(5));
        }
    }
}
