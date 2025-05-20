namespace DesktopAgent.Service
{
    internal static class LogManager
    {
        private static readonly string ebzDirectory = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData), "eBZ Tecnologia");
        private static readonly string logDirectory = Path.Combine(ebzDirectory, "Workday Session Management");
        private static readonly string logFilePath = Path.Combine(logDirectory, "LocalAgent.log");
        private const long MaxLogSizeBytes = 100 * 2048;

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

                RotateLogIfNeeded();
                using (StreamWriter writer = new StreamWriter(logFilePath, true))
                {
                    writer.WriteLine($"[{DateTime.Now:G}] {message}");
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
