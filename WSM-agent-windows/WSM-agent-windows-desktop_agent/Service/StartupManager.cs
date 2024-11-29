using Sodium;

namespace DesktopAgent.Service
{
    internal class StartupManager
    {
        private static readonly string ebzDir = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData), "eBZ Tecnologia");
        private static readonly string wsmDir = Path.Combine(ebzDir, "Workday Session Management");
        private static readonly string wsmServiceDir = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.ProgramFilesX86), "eBZ Tecnologia", "Workday Session Management");

        public static void Init()
        {
            LogManager.Log($"Local Agent initiated...");
            CheckDirectory();
            CheckKeys();
        }

        public static void CheckDirectory()
        {
            if (!Directory.Exists(ebzDir))
            {
                Directory.CreateDirectory(ebzDir);
            }

            if (!Directory.Exists(wsmDir))
            {
                Directory.CreateDirectory(wsmDir);
            }
        }

        public static void CheckKeys()
        {
            if (!File.Exists(Path.Combine(wsmDir, "subscriber_communication.key")) || !File.Exists(Path.Combine(wsmDir, "subscriber_secret.key")))
            {
                Console.WriteLine("Could not find the User's Curve key-pair, generating new pair...");
                LogManager.Log($"Startup -> Could not find the User's Curve key-pair, generating new pair");
                StoreCurveKeys();
            }

            if (!File.Exists(Path.Combine(wsmServiceDir, "publisher_communication.key")))
            {
                Console.WriteLine("Could not find the service public key, aborting...");
                LogManager.Log($"Startup Error -> Could not find the service public key, aborting...");
                return;
            }
        }

        public static void StoreCurveKeys()
        {
            // Generate a 32-byte CURVE25519 key pair
            var keyPair = PublicKeyBox.GenerateKeyPair();

            // Convert the keys to hexadecimal format
            string publicKey = Convert.ToBase64String(keyPair.PublicKey);
            string privateKey = Convert.ToBase64String(keyPair.PrivateKey);

            string publicKeyPath = Path.Combine(wsmDir, "subscriber_communication.key");
            string privateKeyPath = Path.Combine(wsmDir, "subscriber_secret.key");

            File.WriteAllText(publicKeyPath, publicKey);
            File.WriteAllText(privateKeyPath, privateKey);

            Console.WriteLine("Keys successfully generated and saved");
            LogManager.Log($"Startup -> Keys successfully generated and saved");
        }

        public static byte[] LoadCurveKeys(bool is_priv)
        {
            try
            {
                string key;
                if (is_priv)
                {
                    key = File.ReadAllText(Path.Combine(wsmDir, "subscriber_secret.key"));
                }
                else
                {
                    key = File.ReadAllText(Path.Combine(wsmDir, "subscriber_communication.key"));
                }

                byte[] byteKey = Convert.FromBase64String(key);
                return byteKey;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"An error occurred while loading the keys: {ex.Message}");
                LogManager.Log($"Startup Error -> An error occurred while loading the User's key-pair: {ex.Message}");
                return null;
            }
        }

        public static byte[] LoadServiceKey()
        {
            try
            {
                string key = File.ReadAllText(Path.Combine(wsmServiceDir, "publisher_communication.key"));
                byte[] byteKey = Convert.FromBase64String(key);
                return byteKey;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"An error occurred while loading the keys: {ex.Message}");
                LogManager.Log($"Startup Error -> An error occurred while loading the service key: {ex.Message}");
                return new byte[32];
            }
        }
    }
}
