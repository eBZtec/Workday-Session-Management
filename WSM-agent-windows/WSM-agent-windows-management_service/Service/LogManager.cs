namespace SessionService.Service
{
    internal static class LogManager
    {
        public static readonly string logFilePath = Path.Combine(StartupManager.wsmDir, "WSMservice.log");

        public static void Log(string message)
        {
            try
            {
                using (StreamWriter writer = new StreamWriter(logFilePath, true))
                {
                    writer.WriteLine($"{DateTime.UtcNow.ToLocalTime().ToString():G}: {message}");
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Logging failed: {ex.Message}");
            }
        }

        public static void LogClientInfo(string message)
        {
            try
            {
                using (StreamWriter writer = new StreamWriter(logFilePath, true))
                {
                    writer.WriteLine($"{message}");
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Logging failed: {ex.Message}");
            }
        }
    }
}
