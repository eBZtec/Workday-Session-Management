using Microsoft.Win32;

namespace WsmConnectorAdService.Utils
{
    public class InstallationParameters
    {
        public string? SESSION_SERVER_HOST { get; set; }
        public string? ACTIVE_DIRECTORY_HOST { get; set; }

        public InstallationParameters()
        {
            string? registryValue;
            string folder = "WsmConnectorAdService";
            string registryPath = @"Software\eBZ Tecnologia\" + folder;

            registryValue = ReadFromRegistry(registryPath, nameof(SESSION_SERVER_HOST));
            SESSION_SERVER_HOST = !string.IsNullOrEmpty(registryValue) ? registryValue : "";

            registryValue = ReadFromRegistry(registryPath, nameof(ACTIVE_DIRECTORY_HOST));
            ACTIVE_DIRECTORY_HOST = !string.IsNullOrEmpty(registryValue) ? registryValue : "";
        }

        public string? ReadFromRegistry(string subKeyPath, string att_name)
        {
            RegistryKey? key = Registry.LocalMachine.OpenSubKey(subKeyPath);
            if (key != null)
            {
                string? value = key.GetValue(att_name) as string;
                key.Close();
                return value;
            }
            return null;
        }
    }
}
