using NetMQ;
using NetMQ.Sockets;
using System.Diagnostics;
using System.Security.Cryptography.X509Certificates;
using static WsmConnectorAdService.Controller.Setup;
using WsmConnectorAdService.Utils;
using WsmConnectorAdService.ActiveDirectory;

namespace WsmConnectorAdService.Controller
{
    public class Worker : BackgroundService
    {
        private Setup _setup;
        private AdManager _adManager;
        private X509Certificate2? localCertificate;
        private X509Certificate2? serverCertificate;

        private readonly ILogger<Worker> _logger;
        
        public Worker(ILogger<Worker> logger)
        {
            _logger = logger;
            _setup = new Setup();
            _adManager = new AdManager();
            localCertificate = LoadLocalCertificate();
            serverCertificate = LoadServerCertificate();
        }

        public class ActiveDirectoryResponse
        {
            public string? Status { get; set; }
            public string? Message { get; set; }
        }

        protected override async Task ExecuteAsync(CancellationToken stoppingToken)
        {
            string serverAddress = "tcp://*:44901";

            try
            {
                using (var responseSocket = new ResponseSocket())
                {
                    responseSocket.Options.HeartbeatInterval = TimeSpan.FromSeconds(2);
                    responseSocket.Options.HeartbeatTimeout = TimeSpan.FromSeconds(5);

                    responseSocket.Bind(serverAddress);
                    _logger.LogInformation($"Server listening on {serverAddress}");

                    while (!stoppingToken.IsCancellationRequested)
                    {
                        try
                        {
                            // Recebe a mensagem com um timeout configurado
                            if (responseSocket.TryReceiveFrameString(TimeSpan.FromSeconds(10), out string? frameString) && !string.IsNullOrWhiteSpace(frameString))
                            {
                                string response;

                                try
                                {
                                    string request = Cryptography.ProcessRequest(frameString);
                                    
                                    if (IsJsonFormatable(request))
                                    {
                                        try
                                        {
                                            String result = _adManager.UpdateAdUser(request);
                                            response = Cryptography.processResponse(new ActiveDirectoryResponse { Status = "Success", Message = result });
                                        }
                                        catch (InvalidOperationException ex)
                                        {
                                            response = Cryptography.processResponse(new ActiveDirectoryResponse { Status = "Error", Message = ex.Message });
                                        }
                                        catch (Exception)
                                        {
                                            response = Cryptography.processResponse(new ActiveDirectoryResponse { Status = "Error", Message = "An unexpected error occurred while updating AD user." });
                                        }
                                    }
                                    else
                                    {
                                        response = Cryptography.processResponse(new ActiveDirectoryResponse { Status = "Error", Message = "Invalid message format." });
                                        LogToEventViewer("Invalid or incorrectly decrypted message format.", EventLogEntryType.Warning);
                                    }
                                }
                                catch (Exception ex)
                                {
                                    response = Cryptography.processResponse(new ActiveDirectoryResponse { Status = "Error", Message = "Decryption failed. Check certificates and keys used for encryption and decryption." });
                                    LogToEventViewer($"Decryption failed: {ex.Message}", EventLogEntryType.Warning);
                                }

                                if (!responseSocket.TrySendFrame(TimeSpan.FromSeconds(2), response))
                                {
                                    LogToEventViewer("Failed to send response: sender may have disconnected.", EventLogEntryType.Warning);
                                }
                            }
                        }
                        catch (Exception ex)
                        {
                            LogToEventViewer($"Unexpected error in message processing: {ex.Message}", EventLogEntryType.Error);
                        }
                        await Task.Delay(200, stoppingToken);

                        if(localCertificate != null && IsCertificateAboutToExpire(localCertificate))
                        {
                            try
                            {
                                var keys = GetMyKeys();
                                if (keys.Public != null && keys.Private != null)
                                {
                                    CreateMyCertificate(keys.Public, keys.Private);
                                    LoadLocalCertificate();
                                }
                            }
                            catch (Exception ex)
                            {
                                LogToEventViewer($"Failed to renew certificate: {ex.Message}", EventLogEntryType.Error);
                            }
                        }
                    }
                }
            }
            catch (Exception ex)
            {
                LogToEventViewer($"Critical error in worker: {ex.Message}", EventLogEntryType.Error);
            }
        }

        public X509Certificate2? LoadServerCertificate()
        {
            try
            {
                return GetCertFromStore(StoreName.My, "WSM");
            }
            catch (Exception ex)
            {
                LogToEventViewer($"Certificate store exception - Load WSM certificate: {ex.Message}", EventLogEntryType.Error);
                throw new InvalidOperationException("Failed to load the WSM server certificate.", ex);
            }
        }

        public X509Certificate2? LoadLocalCertificate()
        {
            try
            {
                return GetCertFromStore(StoreName.My, MyMachineName);
            }
            catch (Exception ex)
            {
                LogToEventViewer($"Certificate store exception - Load machine certificate: {ex.Message}", EventLogEntryType.Error);
                throw new InvalidOperationException("Failed to load the local machine certificate.", ex);
            }
        }
    }
}
