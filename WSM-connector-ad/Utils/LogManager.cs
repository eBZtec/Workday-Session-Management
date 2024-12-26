using System.Diagnostics;
using WsmConnectorAdService.Controller;

namespace WsmConnectorAdService.Utils
{
    internal static class LogManager
    {
        private static readonly string ebzDirectory = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData), "eBZ Tecnologia");
        private static readonly string logDirectory = Path.Combine(ebzDirectory, "Workday Session Management");
        private static readonly string logFilePath = Path.Combine(logDirectory, "WsmConnectorAdService.log");

        public static void Log(string message)
        {
            try
            {
                if (!Directory.Exists(ebzDirectory))
                {
                    Directory.CreateDirectory(ebzDirectory);
                }

                if (!Directory.Exists(logDirectory))
                {
                    Directory.CreateDirectory(logDirectory);
                }

                using (StreamWriter writer = new StreamWriter(logFilePath, true))
                {
                    writer.WriteLine($"[{DateTime.Now:G}] {message}");
                }
            }
            catch (Exception ex)
            {
                Setup.LogToEventViewer($"Logging failed: {ex.Message}", EventLogEntryType.Error);
            }
        }
    }
}
