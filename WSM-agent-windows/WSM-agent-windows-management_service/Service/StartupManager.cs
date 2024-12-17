using DnsClient;
using NetMQ;
using NetMQ.Sockets;
using SessionService.Model;
using Sodium;
using System.Management;
using System.Security.AccessControl;
using System.Security.Principal;
using System.Text.Json;

namespace SessionService.Service
{
    internal class StartupManager
    {
        public static readonly string ebzDir = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.ProgramFilesX86), "eBZ Tecnologia");
        public static readonly string wsmDir = Path.Combine(ebzDir, "Workday Session Management");

        public static void Init()
        {
            CheckDirectory();
            CheckKeys();
            LogManager.LogClientInfo("");
            SetAdminOnlyAccess(new FileInfo(LogManager.logFilePath));
        }

        public static void CheckDirectory()
        {
            if (!Directory.Exists(ebzDir))
            {
                var dirInfo = Directory.CreateDirectory(ebzDir);
                DirectorySecurity security = new DirectorySecurity();

                security.AddAccessRule(new FileSystemAccessRule(
                    "Administrators",
                    FileSystemRights.FullControl,
                    InheritanceFlags.ContainerInherit | InheritanceFlags.ObjectInherit,
                    PropagationFlags.None,
                    AccessControlType.Allow));

                security.AddAccessRule(new FileSystemAccessRule(
                    "SYSTEM",
                    FileSystemRights.FullControl,
                    InheritanceFlags.ContainerInherit | InheritanceFlags.ObjectInherit,
                    PropagationFlags.None,
                    AccessControlType.Allow));

                dirInfo.SetAccessControl(security);
            }

            if (!Directory.Exists(wsmDir))
            {
                DirectoryInfo dirInfo = Directory.CreateDirectory(wsmDir);
                DirectorySecurity security = new DirectorySecurity();

                security.AddAccessRule(new FileSystemAccessRule(
                    "Administrators",
                    FileSystemRights.FullControl,
                    InheritanceFlags.ContainerInherit | InheritanceFlags.ObjectInherit,
                    PropagationFlags.None,
                    AccessControlType.Allow));

                security.AddAccessRule(new FileSystemAccessRule(
                    "SYSTEM",
                    FileSystemRights.FullControl,
                    InheritanceFlags.ContainerInherit | InheritanceFlags.ObjectInherit,
                    PropagationFlags.None,
                    AccessControlType.Allow));

                dirInfo.SetAccessControl(security);
            }
        }

        public static void CheckKeys()
        {
            if (!File.Exists(Path.Combine(wsmDir, "publisher_communication.key")) || !File.Exists(Path.Combine(wsmDir, "publisher_secret.key")))
            {
                LogManager.Log("Could not find the Curve key-pair, generating new pair...");
                StoreCurveKeys();
            }
        }

        public static void StoreCurveKeys()
        {
            var keyPair = PublicKeyBox.GenerateKeyPair();

            string publicKey = Convert.ToBase64String(keyPair.PublicKey);
            string privateKey = Convert.ToBase64String(keyPair.PrivateKey);

            string publicKeyPath = Path.Combine(wsmDir, "publisher_communication.key");
            string privateKeyPath = Path.Combine(wsmDir, "publisher_secret.key");

            File.WriteAllText(publicKeyPath, publicKey);
            File.WriteAllText(privateKeyPath, privateKey);

            LogManager.Log("Keys successfully generated and saved");

            SetAdminOnlyAccess(new FileInfo(privateKeyPath));
        }

        public static byte[] LoadCurveKeys(bool is_priv)
        {
            try
            {
                string key;
                if (is_priv)
                {
                    key = File.ReadAllText(Path.Combine(wsmDir, "publisher_secret.key"));
                }
                else
                {
                    key = File.ReadAllText(Path.Combine(wsmDir, "publisher_communication.key"));
                }

                byte[] byteKey = Convert.FromBase64String(key);
                return byteKey;
            }
            catch (Exception ex)
            {
                LogManager.Log($"An error occurred while loading the keys: {ex.Message}");
                return null;
            }
        }

        public static void SetAdminOnlyAccess(FileInfo fileInfo)
        {
            FileSecurity fileSecurity = fileInfo.GetAccessControl();
            SecurityIdentifier adminSid = new SecurityIdentifier(WellKnownSidType.BuiltinAdministratorsSid, null);
            FileSystemAccessRule adminAccessRule = new FileSystemAccessRule(adminSid, FileSystemRights.FullControl, AccessControlType.Allow);

            fileSecurity.AddAccessRule(adminAccessRule);
            fileSecurity.SetAccessRuleProtection(isProtected: true, preserveInheritance: false);

            fileInfo.SetAccessControl(fileSecurity);
        }

        public static void HeartBeat(ClientInfo clientInfo, DealerSocket dealer)
        {
            while (true)
            {
                clientInfo = new ClientInfo();

                var msg = new Dictionary<string, string>();
                msg.Add("Heartbeat", JsonSerializer.Serialize(clientInfo));

                var jsonMsg = JsonSerializer.Serialize(msg);

                dealer.SendFrame(jsonMsg);

                LogManager.Log($"Heartbeat sent, uptime: {clientInfo.uptime} minutes");
                Thread.Sleep(TimeSpan.FromMinutes(30));
            }
        }

        public static string getServerURL()
        {
            string domainName = "";

            try
            {
                using (var searcher = new ManagementObjectSearcher("SELECT Domain FROM Win32_ComputerSystem"))
                {
                    foreach (ManagementObject domain in searcher.Get())
                    {
                        domainName = domain["Domain"].ToString();
                    }
                }
            }
            catch (Exception ex)
            {
                LogManager.Log($"ServerURL -> Error retrieving information: {ex.Message}");
            }

            try
            {
                var lookup = new LookupClient();
                var result = lookup.Query(domainName, QueryType.TXT);

                foreach (var txtRecord in result.Answers.TxtRecords())
                {
                    foreach (var text in txtRecord.Text)
                    {
                        if (text.StartsWith("wsm_session_servers=", StringComparison.OrdinalIgnoreCase))
                        {
                            return text.Split('=')[1].Trim();
                        }
                    }
                }
            }
            catch (Exception ex)
            {
                LogManager.Log($"ServerURL -> Error retrieving TXT record info: {ex.Message}");
            }

            LogManager.Log("ServerURL -> Could not retrieve the server URL. Dealer not properly bound (localhost:5555)");
            return "localhost:5555";
        }
    }
}
