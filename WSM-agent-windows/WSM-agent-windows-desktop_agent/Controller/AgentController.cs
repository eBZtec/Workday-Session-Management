using DesktopAgent.Model;
using DesktopAgent.Service;
using NetMQ;
using NetMQ.Sockets;
using System.Text.Json;

class AgentController
{
    public static async Task Main()
    {
        StartupManager.Init();

        using (var subscriber = new SubscriberSocket())
        {
            try
            {
                subscriber.Options.CurveServerKey = StartupManager.LoadServiceKey();
                subscriber.Options.CurveCertificate = new NetMQCertificate(StartupManager.LoadCurveKeys(true), StartupManager.LoadCurveKeys(false));
                subscriber.Connect("tcp://localhost:12345");

                subscriber.Subscribe(Environment.UserName);

                Console.WriteLine("Subscriber connected and waiting for messages...");
            }
            catch (Exception ex)
            {
                Console.WriteLine(ex);
                LogManager.Log($"FirstInit on AgentController -> ex: {ex.Message}");
            }

            while (true)
            {
                try
                {
                    var messageParts = subscriber.ReceiveMultipartStrings();
                    ServiceCommand command = JsonSerializer.Deserialize<ServiceCommand>(messageParts[1]) ?? new ServiceCommand();

                    switch (command.action)
                    {
                        case "lock":
                            NotificationManager.SendBasicNotification("Lock", "A sessão será trancada");
                            break;

                        case "logoff":
                            NotificationManager.SendBasicNotification("Encerrando", "A sessão encerrará em poucos segundos");
                            break;

                        case "interact":
                            _ = Task.Run(() => NotificationManager.UserInteraction(command.title, command.description, command.options));
                            break;

                        case "notify":
                            NotificationManager.SendBasicNotification(command.title, command.description);
                            break;

                        default:
                            LogManager.Log($"AgentController -> unknown action received: {command.action}");
                            break;
                    }
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"Catch: {ex}");
                    LogManager.Log($"AgentController -> An unexpected error occurred: {ex.Message}");
                }
                await Task.Delay(TimeSpan.FromSeconds(1));
            }
        }
    }
}
