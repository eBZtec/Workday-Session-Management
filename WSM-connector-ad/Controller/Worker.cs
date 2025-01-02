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
            localCertificate = loadLocalCertificate();
            serverCertificate = loadServerCertificate();
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
                                    // Processa a requisição
                                    string request = Cryptography.processRequest(frameString);

                                    if (IsJsonFormatable(request))
                                    {
                                        try
                                        {
                                            _adManager.updateADLogonHours(request);
                                            LogToEventViewer($"Parsed: {request}",EventLogEntryType.Information);
                                            response = Cryptography.processResponse(new ActiveDirectoryResponse { Status = "Success", Message = "Logon hours updated successfully." });
                                        }
                                        catch (InvalidOperationException ex)
                                        {
                                            response = Cryptography.processResponse(new ActiveDirectoryResponse { Status = "Error", Message = ex.Message });
                                        }
                                        catch (Exception ex)
                                        {
                                            response = Cryptography.processResponse(new ActiveDirectoryResponse { Status = "Error", Message = "An unexpected error occurred while updating AD logon hours." });
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

                                // Tenta enviar a resposta de volta
                                if (!responseSocket.TrySendFrame(TimeSpan.FromSeconds(2), response))
                                {
                                    LogToEventViewer("Failed to send response: sender may have disconnected.", EventLogEntryType.Warning);
                                }
                            }
                        }
                        catch (Exception ex)
                        {
                            // Captura erros inesperados no loop principal
                            LogToEventViewer($"Unexpected error in message processing: {ex.Message}", EventLogEntryType.Error);
                        }

                        // Delay antes de continuar o próximo ciclo
                        await Task.Delay(200, stoppingToken);

                        // Verifica se o certificado está prestes a expirar
                        if (IsCertificateAboutToExpire(localCertificate))
                        {
                            try
                            {
                                var keys = GetMyKeys();
                                if (keys.Public != null && keys.Private != null)
                                {
                                    CreateMyCertificate(keys.Public, keys.Private);
                                    loadLocalCertificate();
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
                // Captura erros críticos fora do loop principal
                LogToEventViewer($"Critical error in worker: {ex.Message}", EventLogEntryType.Error);
            }
        }

        public X509Certificate2 loadServerCertificate()
        {
            try
            {
                return GetCertFromStore(StoreName.My, "WSM");
            }
            catch (Exception ex)
            {
                LogToEventViewer($"Certificate store exception - Load wsm certificate: {ex.Message}", EventLogEntryType.Information);
            }
            return null;
        }

        public X509Certificate2 loadLocalCertificate()
        {
            try
            {
                return GetCertFromStore(StoreName.My, MyMachineName);
            }
            catch (Exception ex)
            {
                LogToEventViewer($"Certificate store exception - Load machine certificate: {ex.Message}", EventLogEntryType.Information);
            }
            return null;
        }
    }
}
