using Newtonsoft.Json;
using SessionService.Service;
using System.Net;

namespace SessionService.Model
{
    public class ServerResponse
    {
        public string action { get; set; }
        public string hostname { get; set; }
        public string user { get; set; }
        public string timezone { get; set; }
        public AllowedSchedule allowed_schedule { get; set; }
        public DateTimeOffset timestamp { get; set; }
        public string message { get; set; }
        public string title { get; set; }
        public string options { get; set; }
        public bool unrestricted { get; set; }
        public bool enable { get; set; }
        public int? grace_login { get; set; }
    }

    public class AllowedSchedule
    {
        public List<Schedule> sunday { get; set; }
        public List<Schedule> monday { get; set; }
        public List<Schedule> tuesday { get; set; }
        public List<Schedule> wednesday { get; set; }
        public List<Schedule> thursday { get; set; }
        public List<Schedule> friday { get; set; }
        public List<Schedule> saturday { get; set; }
    }

    public class Schedule
    {
        public int start { get; set; }
        public int end { get; set; }
    }

    internal class Command
    {
        public string action { get; set; }
        public string title { get; set; }
        public string description { get; set; }
        public string options { get; set; }

        public Command(string? action, string? title, string? description, string? options)
        {
            this.action = action ?? "Unknown";
            this.title = title ?? "Unknown";
            this.description = description ?? "Unknown";
            this.options = options ?? "Unknown";
        }

        public static Command ResponseToCommand(ServerResponse response)
        {
            Command cmd;
            try
            {
                cmd = new Command(response.action, response.title, response.message, response.options);
            }
            catch (Exception ex)
            {
                LogManager.Log($"Response to Command -> Error: {ex.Message}");
                cmd = new Command(null, null, null, null);
            }

            return cmd;
        }
    }

    internal class EventInfoHandler
    {
        public string hostname { get; set; }
        public string status { get; set; }
        public string user { get; set; }
        public DateTimeOffset? logonTime { get; set; }
        public DateTimeOffset? logoffTime { get; set; }
        public DateTimeOffset timestamp { get; set; }

        public EventInfoHandler(string status, string user)
        {
            this.status = status;
            this.user = user;
            this.hostname = StartupManager.getFqdn() ?? "Unknown";
            this.timestamp = DateTimeOffset.UtcNow;

            switch (status)
            {
                case "connected":
                    this.logonTime = DateTimeOffset.UtcNow;
                    break;

                case "disconnected":
                    this.logoffTime = DateTimeOffset.UtcNow;
                    break;
            }

        }
    }

    // ----- crypt -----
    public class Response
    {
        public required string Status { get; set; }
    }
    public class ErrorResponse : Response
    {
        public required string Message { get; set; }
    }
    public class SuccessResponse : Response
    {
        public required string Data { get; set; }
    }
}
