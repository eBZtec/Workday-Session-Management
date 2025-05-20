namespace SessionService.Service
{
    internal static class LogManager
    {
        private const long MaxLogSizeBytes = 10 * 1024 * 1024;
        public static readonly string logFilePath = Path.Combine(StartupManager.wsmDir, "WSMservice.log");

        public static void Log(string message)
        {
            try
            {
                RotateLogIfNeeded();
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
                RotateLogIfNeeded();
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

        private static void RotateLogIfNeeded()
        {
            try
            {
                if (File.Exists(logFilePath))
                {
                    var fileInfo = new FileInfo(logFilePath);
                    if (fileInfo.Length >= MaxLogSizeBytes)
                    {
                        string timestamp = DateTime.Now.ToString("yyyyMMdd_HHmmss");
                        string archiveFile = Path.Combine(
                            StartupManager.wsmDir, $"WSMservice_{timestamp}.log"
                        );

                        File.Move(logFilePath, archiveFile);
                    }
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Log rotation failed: {ex.Message}");
            }
        }
    }
}
