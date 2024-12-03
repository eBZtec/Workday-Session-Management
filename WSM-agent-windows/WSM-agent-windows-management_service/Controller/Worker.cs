using NetMQ;
using NetMQ.Sockets;
using SessionService.Model;
using SessionService.Service;
using System.Diagnostics;
using System.Text.Json;

public class Worker : BackgroundService
{
    private readonly EventLog _eventLog;
    private List<UserSession> userSessions;
    private PublisherSocket publisher;
    private DealerSocket dealer;
    private ClientInfo clientInfo;
    private List<UserAllowed> usersAllowed;

    public Worker()
    {
        _eventLog = new EventLog("Security")
        {
            Log = "Security"
        };
        _eventLog.EntryWritten += OnEntryWritten;
        _eventLog.EnableRaisingEvents = true;

        userSessions = new List<UserSession>();
        clientInfo = new ClientInfo();
        usersAllowed = new List<UserAllowed>();
        StartupManager.Init();
    }

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        while (!stoppingToken.IsCancellationRequested)
        {
            try
            {
                LogManager.LogClientInfo(clientInfo.ToString());
                Console.WriteLine(clientInfo);

                await InitializeSocketsAndRun(stoppingToken);
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Worker encountered an exception: {ex.Message}. Retrying...");
                LogManager.Log($"Worker -> Exception: {ex.Message}");
                await Task.Delay(TimeSpan.FromSeconds(5), stoppingToken); // Backoff before retry
            }
        }
    }

    private async Task InitializeSocketsAndRun(CancellationToken stoppingToken)
    {
        using (publisher = new PublisherSocket())
        using (dealer = new DealerSocket())
        {
            string pubUrl = "tcp://localhost:12345";        // Publisher URL
            string dealerUrl = "tcp://localhost:5555";      // Dealer URL

            try
            {
                // Initialize sockets
                InitializePublisher(publisher, pubUrl);
                InitializeDealer(dealer, dealerUrl);

                _ = Task.Run(() => WorkdayManager.Vigilance(userSessions, usersAllowed, publisher));
                _ = Task.Run(() => StartupManager.HeartBeat(clientInfo, dealer));

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
        dealer.Options.Identity = System.Text.Encoding.UTF8.GetBytes(System.Net.Dns.GetHostName());
        dealer.Connect(dealerUrl);
        LogManager.Log($"Worker -> Dealer connected to: {dealerUrl}");
    }

    private async Task HandleMessages(CancellationToken stoppingToken)
    {
        var messageParts = new List<string>();
        TimeSpan timeout = TimeSpan.FromSeconds(60);

        if (dealer.TryReceiveMultipartStrings(timeout, ref messageParts, 2))
        {
            try
            {
                LogManager.Log($"Worker -> Received message: {messageParts[1]}");

                var messageObject = JsonSerializer.Deserialize<ServerResponse>(messageParts[1]) ?? new ServerResponse();

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
                        LogManager.Log($"Worker -> Unknown command received: {messageObject.action}");
                        break;
                }
            }
            catch (Exception ex)
            {
                LogManager.Log($"HandleMessages -> Error handling message: {ex.Message}");
            }
        }
        await Task.Delay(100, stoppingToken);
    }

    private void OnEntryWritten(object sender, EntryWrittenEventArgs e)
    {
        switch (e.Entry.InstanceId)
        {
            case 4624: // Logon
                userSessions = SessionManager.EnumerateSessions();
                if (e.Entry.ReplacementStrings[6].Equals(Environment.MachineName) && e.Entry.ReplacementStrings[0].Equals("S-1-0-0"))
                {
                    EventManager.HandleLogonEvent(e.Entry, dealer);
                    SessionManager.DescribeUsers(userSessions);
                }
                userSessions = SessionManager.EnumerateSessions();
                break;

            case 4800: // Lock
                userSessions = SessionManager.EnumerateSessions();
                EventManager.HandleLockEvent(e.Entry, dealer);
                userSessions = SessionManager.EnumerateSessions();
                break;

            case 4801: // Unlock
                userSessions = SessionManager.EnumerateSessions();
                EventManager.HandleUnlockEvent(e.Entry, dealer);
                userSessions = SessionManager.EnumerateSessions();
                break;

            case 4647: // Logoff
                userSessions = SessionManager.EnumerateSessions();
                EventManager.HandleLogoffEvent(e.Entry, dealer);
                userSessions = SessionManager.EnumerateSessions();
                SessionManager.DescribeUsers(userSessions);
                break;

            default:
                break;
        }
    }

    private void HandleLogoffCase(ServerResponse messageObject)
    {
        Thread.Sleep(TimeSpan.FromSeconds(5));

        List<int> ids = SessionManager.GetSessionIDs(messageObject.user ?? "Unknown", userSessions);
        foreach (int id in ids)
        {
            SessionManager.LogoffSession(id, messageObject.user);
        }
    }

    private void HandleLockCase(ServerResponse messageObject)
    {
        Thread.Sleep(TimeSpan.FromSeconds(5));

        List<int> ids = SessionManager.GetSessionIDs(messageObject.user ?? "Unknown", userSessions);
        foreach (int id in ids)
        {
            SessionManager.Lock(id, messageObject.user);
        }
    }
}
