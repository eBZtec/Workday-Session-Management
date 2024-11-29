
namespace DesktopAgent.Model
{
    internal class ServiceCommand
    {
        public string action { get; set; }
        public string title { get; set; }
        public string description { get; set; }
        public string options { get; set; }

        public ServiceCommand()
        {
            this.action = "Unknown";
            this.title = "Unknown";
            this.description = "Unknown";
            this.options = "Unknown";
        }
        public ServiceCommand(string action, string title, string description, string options)
        {
            this.action = action ?? "Unknown";
            this.title = title ?? "Unknown"; ;
            this.description = description ?? "Unknown"; ;
            this.options = options ?? "Unknown"; ;
        }
    }
}
