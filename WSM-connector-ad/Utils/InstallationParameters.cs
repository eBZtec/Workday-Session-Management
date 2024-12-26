using Microsoft.Win32;

namespace WsmConnectorAdService.Utils
{
    public class InstallationParameters
    {
        public string? SESSION_SERVER_HOST { get; set; }
        public string? ACTIVE_DIRECTORY_HOST { get; set; }

        public InstallationParameters()
        {
            string registryValue;
            string folder = "WsmConnectorAdService";
            string registryPath = @"Software\eBZ Tecnologia\" + folder;

            registryValue = (string)ReadFromRegistry(registryPath, SESSION_SERVER_HOST, nameof(SESSION_SERVER_HOST));
            SESSION_SERVER_HOST = !string.IsNullOrEmpty(registryValue) ? registryValue : "";

            registryValue = (string)ReadFromRegistry(registryPath, ACTIVE_DIRECTORY_HOST, nameof(ACTIVE_DIRECTORY_HOST));
            ACTIVE_DIRECTORY_HOST = !string.IsNullOrEmpty(registryValue) ? registryValue : "";
        }

        public Object ReadFromRegistry(string subKeyPath, Object att, string att_name)
        {
            RegistryKey key = Registry.LocalMachine.OpenSubKey(subKeyPath); //@"Software\MyApplication"
            if (key != null)
            {
                string value = key.GetValue(att_name) as string;
                att = value;

                key.Close();
            }

            return att;
        }

        
    }
}
