using System.Diagnostics;
using System.Net;
using System.Reflection;
using System.Runtime.InteropServices;
using System.Text.RegularExpressions;
using SessionService.Service;

namespace SessionService.Model
{
    internal class ClientInfo
    {
        public string hostname { get; set; }
        public string ip_address { get; set; }
        public string client_version { get; set; }
        public string os_name { get; set; }
        public string os_version { get; set; }
        public string agent_info { get; set; }
        public int uptime { get; set; }
        public string timezone { get; set; }

        public ClientInfo()
        {
            hostname = StartupManager.getFqdn() ?? "Unknown"; //System.Net.Dns.GetHostName()
            ip_address = Get_ip();
            client_version = Assembly.GetExecutingAssembly().GetName().Version?.ToString() ?? "0.0.0.0";
            os_name = RuntimeInformation.OSDescription ?? "Unknown";
            os_version = Get_osVersion();
            agent_info = "Default WSM Service installation";
            uptime = GetUptime();
            timezone = TimeZoneInfo.Local.BaseUtcOffset.ToString();
        }

        public string Get_ip()
        {
            IPAddress[] addresses = Dns.GetHostAddresses(System.Net.Dns.GetHostName());

            foreach (IPAddress address in addresses)
            {
                if (address.AddressFamily == System.Net.Sockets.AddressFamily.InterNetwork)
                {
                    return address.ToString();
                }
            }
            return "No InterNetwork IPv4";
        }

        public string Get_osVersion()
        {
            var match = Regex.Match(os_name, @"\d+(\.\d+)+");
            string version = match.Success ? match.Value : "Version not found";
            return version;
        }

        public int GetUptime()
        {
            DateTime startTime = Process.GetCurrentProcess().StartTime;
            TimeSpan uptime = DateTime.UtcNow.ToLocalTime() - startTime;

            return (int)uptime.TotalMinutes;
        }

        public override string ToString()
        {
            return "-------------------------\n" + "hostname: " + hostname + " - ip: " + ip_address + " - clientVersion: " + client_version +
                "\nOS: " + os_name + " - Agent Info: " + agent_info +
                "\nUptime: " + uptime + "minutes - Timezone: " + timezone +
                "\n-------------------------";
        }
    }
}
