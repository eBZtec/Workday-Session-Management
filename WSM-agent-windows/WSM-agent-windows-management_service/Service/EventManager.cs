using NetMQ;
using NetMQ.Sockets;
using SessionService.Model;
using System.Diagnostics;
using System.Text.Json;

namespace SessionService.Service
{
    public class EventManager
    {
        public static void HandleLogonEvent(EventLogEntry entry, DealerSocket dealer)
        {
            LogManager.Log($"EventMananger -> Logon event detected by USER: {entry.ReplacementStrings[5]}");
            Console.WriteLine($"Logon event detected at {entry.TimeGenerated} by USER: {entry.ReplacementStrings[5]}");

            EventInfoHandler info = new("connected", entry.ReplacementStrings[5]);

            var encapsulatedJson = new Dictionary<string, string> { { "LogonRequest", JsonSerializer.Serialize<EventInfoHandler>(info) } };
            var result = JsonSerializer.Serialize(encapsulatedJson);

            dealer.SendFrame(result);
        }

        public static void HandleLockEvent(EventLogEntry entry, DealerSocket dealer)
        {
            LogManager.Log($"EventMananger -> Lock event detected by USER: {entry.ReplacementStrings[1]}");
            Console.WriteLine($"Lock event detected at {entry.TimeGenerated} by user: {entry.ReplacementStrings[1]}");

            EventInfoHandler info = new("locked", entry.ReplacementStrings[1]);

            var encapsulatedJson = new Dictionary<string, EventInfoHandler> { { "LockUnlock", info } };
            var result = JsonSerializer.Serialize(encapsulatedJson);
            //dealer.SendFrame(result);
        }

        public static void HandleUnlockEvent(EventLogEntry entry, DealerSocket dealer)
        {
            LogManager.Log($"EventMananger -> Unlock event detected by USER: {entry.ReplacementStrings[1]}");
            Console.WriteLine($"Unlock event at {entry.TimeGenerated} User: {entry.ReplacementStrings[1]}");

            EventInfoHandler info = new("active", entry.ReplacementStrings[1]);

            var encapsulatedJson = new Dictionary<string, EventInfoHandler> { { "LockUnlock", info } };
            var result = JsonSerializer.Serialize(encapsulatedJson);
            // dealer.SendFrame(result);
        }

        public static void HandleLogoffEvent(EventLogEntry entry, DealerSocket dealer)
        {
            LogManager.Log($"EventMananger -> Logoff event detected by USER: {entry.ReplacementStrings[1]}");
            Console.WriteLine($"Logoff event detected right now at {entry.TimeGenerated} User: {entry.ReplacementStrings[1]}");

            EventInfoHandler info = new("disconnected", entry.ReplacementStrings[1]);

            var encapsulatedJson = new Dictionary<string, EventInfoHandler> { { "SessionDisconnected", info } };
            var result = JsonSerializer.Serialize(encapsulatedJson);
            dealer.SendFrame(result);
        }
    }
}
