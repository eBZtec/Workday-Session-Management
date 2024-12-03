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
        using (publisher = new PublisherSocket())
        using (dealer = new DealerSocket())
        {
            try
            {
                string pubUrl = "tcp://localhost:12345";        // Publisher URL for users

                Console.Write("Informar a url do session_server: ");
                string dealerUrl = Console.ReadLine() ?? "tcp://127.0.0.1:5555";    // Router server URL for receiving-sending messages

                publisher.Options.CurveServer = true;
                publisher.Options.CurveCertificate = new NetMQCertificate(StartupManager.LoadCurveKeys(true), StartupManager.LoadCurveKeys(false));

                publisher.Bind(pubUrl);
                LogManager.Log($"Worker -> Publisher bound to: {pubUrl}");

                dealer.Connect(dealerUrl);
                LogManager.Log($"Worker -> Dealer connected to: {dealerUrl}");

                dealer.Options.Identity = System.Text.Encoding.UTF8.GetBytes(System.Net.Dns.GetHostName());

                //info da versão do agente
                Console.WriteLine(clientInfo);
                LogManager.LogClientInfo(clientInfo.ToString());

                //Print active users
                userSessions = SessionManager.EnumerateSessions();
                SessionManager.DescribeUsers(userSessions);

                //-------------------------------------------------
                _ = Task.Run(() => WorkdayManager.Vigilance(userSessions, usersAllowed, publisher));
                _ = Task.Run(() => StartupManager.HeartBeat(clientInfo, dealer));
                //-------------------------------------------------
                while (!stoppingToken.IsCancellationRequested)
                {
                    var messageParts = new List<string>();
                    TimeSpan timeout = new TimeSpan(0, 0, 5);

                    if (dealer.TryReceiveMultipartStrings(timeout, ref messageParts, 2))
                    {
                        try
                        {
                            LogManager.Log($"Worker -> Received message: {messageParts[1]}");

                            ServerResponse messageObject = JsonSerializer.Deserialize<ServerResponse>(messageParts[1]) ?? new ServerResponse();

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
                                    LogManager.Log($"Worker -> Unknown command received from router: {messageObject.action}");
                                    break;
                            }
                        }
                        catch (Exception ex)
                        {
                            Console.WriteLine("Could not deserialize Object");
                            LogManager.Log("messageObject -> Could not deserialize Object");
                        }
                    }

                    await Task.Delay(100, stoppingToken);
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Socket exception - ExecuteAsync Worker: {ex.Message}");
                LogManager.Log($"Worker -> Socket exception - ExecuteAsync Worker: {ex.Message}");
            }
        }
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
