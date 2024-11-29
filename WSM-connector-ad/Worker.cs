using NetMQ;
using NetMQ.Sockets;
using System.Diagnostics;
using System.Security.Cryptography;
using System.Security.Cryptography.X509Certificates;
using static WsmConnectorAdService.Setup;
using System.Text;
using Newtonsoft.Json;
using WsmConnectorAd;

namespace WsmConnectorAdService
{
    public class Worker : BackgroundService
    {
        private X509Certificate2? connectorAdCertificate;
        private X509Certificate2? machineCertificate;
        private readonly ILogger<Worker> _logger;

        public Worker(ILogger<Worker> logger)
        {
            _logger = logger;
        }

        protected override async Task ExecuteAsync(CancellationToken stoppingToken)
        {
            AdManager adManager = new AdManager();
            Setup setup = new Setup();
            setup.Start();

            loadWsmCertificate();
            loadLocalCertificate();

            string response;
            string serverAddress = "tcp://*:44900";
            
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
                            if (responseSocket.TryReceiveFrameString(TimeSpan.FromSeconds(10), out string? frameString) && frameString.Length > 0)
                            {
                                try
                                {
                                    string request = Cryptography.processRequest(frameString);

                                    adManager.updateADLogonHours(request);

                                    if (IsJsonFormatable(request))
                                    {
                                        response = Cryptography.processResponse();
                                    }
                                    else
                                    {
                                        response = CreateErrorResponse("Invalid message format.");
                                        LogManager.Log("Invalid or incorrectly decrypted message format.");
                                    }
                                }
                                catch (Exception ex)
                                {
                                    response = CreateErrorResponse("Decryption failed.");
                                    LogManager.Log($"Decryption failed: {ex.Message}");
                                }
                            }
                            else
                            {
                                response = CreateErrorResponse("Received an empty message.");
                                //LogManager.Log("Received an empty message.");
                            }

                            if (responseSocket.HasOut)
                            {
                                response = Cryptography.processResponse();
                                if (!responseSocket.TrySendFrame(TimeSpan.FromSeconds(2), response))
                                {
                                    LogManager.Log("Failed to send response: sender may have disconnected.");
                                }
                            }
                            else
                            {
                                LogManager.Log("Sender disconnected before response could be sent.");
                            }

                            if (Setup.IsCertificateAboutToExpire(machineCertificate))
                            {
                                var keys = Setup.GetMyKeys();
                                if (keys.Public != null && keys.Private != null)
                                {
                                    Setup.CreateMyCertificate(keys.Public, keys.Private);
                                    loadLocalCertificate();
                                }
                            }
                        }
                        catch (Exception ex)
                        {
                            LogManager.Log($"Unexpected error: {ex.Message}");
                        }
                        await Task.Delay(200, stoppingToken);
                    }
                }
            }
            catch (Exception ex)
            {
                LogManager.Log($"Critical error in worker: {ex.Message}");
            }
        }


        private void TestAdConnection()
        {
            var tester = new AdConnectionTester(_logger);

            _logger.LogInformation("In worker...");

            string ldapPath = "LDAP://dc1.smb.tribanco.lab";
            string username = "nikolas";
            string password = "Smartway 123";

            bool isConnected = tester.TestAdConnection(ldapPath, username, password);

            if (isConnected)
            {
                _logger.LogInformation("AD connection test succeeded.");
            }
            else
            {
                _logger.LogWarning("AD connection test failed.");
            }
        }

        public void loadWsmCertificate()
        {
            try
            {
                connectorAdCertificate = Setup.GetCertFromStore(StoreName.My, "WSM");
            }
            catch (Exception ex)
            {
                LogManager.Log($"Certificate store exception - Load wsm certificate: {ex.Message}");
            }
        }

        public void loadLocalCertificate()
        {
            try
            {
                machineCertificate = Setup.GetCertFromStore(StoreName.My, Setup.MyMachineName);
            }
            catch (Exception ex)
            {
                LogManager.Log($"Certificate store exception - Load machine certificate: {ex.Message}");
            }
        }
    }
}
