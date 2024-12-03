using NetMQ;
using NetMQ.Sockets;
using SessionService.Model;
using Sodium;
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
                Console.WriteLine("Could not find the Curve key-pair, generating new pair...");
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

            Console.WriteLine("Keys successfully generated and saved");

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
                Console.WriteLine($"An error occurred while loading the keys: {ex.Message}");
                return null;
            }
        }

        private static void SetAdminOnlyAccess(FileInfo fileInfo)
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

                LogManager.Log($"Heartbeat sent, uptime: {clientInfo.uptime}");
                Thread.Sleep(TimeSpan.FromMinutes(30));
            }
        }
    }
}
