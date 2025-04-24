using System.Security.AccessControl;
using System.Security.Cryptography.X509Certificates;
using System.Security.Cryptography;
using System.Security.Principal;
using System.Text;
using NetMQ.Sockets;
using Org.BouncyCastle.Asn1.X509;
using Org.BouncyCastle.Asn1;
using Org.BouncyCastle.Crypto.Generators;
using Org.BouncyCastle.Crypto.Parameters;
using Org.BouncyCastle.Crypto;
using Org.BouncyCastle.Pkcs;
using Org.BouncyCastle.Security;
using Org.BouncyCastle.X509;
using NetMQ;
using Org.BouncyCastle.OpenSsl;
using System.Diagnostics;
using Microsoft.Win32;
using System.Net;
using System.Xml;

using Newtonsoft.Json;

namespace WsmConnectorAdService.Controller
{
    public class Setup
    {
        public static string session_server_CA_cn = "WSM-CA";
        public static string session_server_cn = "WSM-SESSION-SERVER";
        public static string session_server_host = "tcp://" + GetFromRegistry("SESSION_SERVER_HOST");

        public static string MyMachineName = GetMachineFQDN();
        
        public Setup() {
            Init();
        }

        public static string SendRequestToRouter(string routerAddress, string identity, string message)
        {
            // Cria o contexto e o socket Dealer
            // Define a identidade do cliente
            // Conecta ao router
            // Envia a mensagem (identity já está associado ao socket Dealer)
            // Aguarda a resposta multipart
            using (var dealer = new DealerSocket())
            {
                try
                {
                    dealer.Options.Identity = Encoding.UTF8.GetBytes(identity);

                    dealer.Connect(routerAddress);
                    Console.WriteLine($"Connected to router: {routerAddress}");

                    dealer.SendFrame(message);
                    Console.WriteLine($"Message sent to router: {message}");

                    var messageParts = dealer.ReceiveMultipartMessage();

                    string jsonString = Encoding.UTF8.GetString(messageParts[1].Buffer);

                    Console.WriteLine($"JSON String: {jsonString}");

                    return jsonString;
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"Error communicating with the router: {ex.Message}");
                    throw;
                }
            }
        }

        public static void GetCertificate(string routerAddress, string request, string identity)
        {
            // Cria a mensagem JSON, serializa e envia para o router
            // Desserializa a resposta para a classe Response
            // Armazena na certificate store em caso de sucesso

            var message = new Dictionary<string, string>
            {
                { "CARequest", "true" },
                { "action", $"{request}" }
            };
            string jsonMessage = System.Text.Json.JsonSerializer.Serialize(message);
            string jsonResponse = SendRequestToRouter(routerAddress, identity, jsonMessage);

            try
            {
                var response = JsonConvert.DeserializeObject<Response>(jsonResponse);
                if (response?.Status == "error")
                {
                    var errorResponse = JsonConvert.DeserializeObject<ErrorResponse>(jsonResponse);
                    throw new Exception(errorResponse?.Message);
                }
                else if (response?.Status == "success")
                {
                    var successResponse = JsonConvert.DeserializeObject<SuccessResponse>(jsonResponse);
                    if (successResponse?.Data != null)
                    {
                        StoreCertificate(ConvertPemToX509(successResponse.Data), StoreName.My, StoreLocation.LocalMachine);
                    }
                    else
                    {
                        throw new Exception("Response contained no certificate data.");
                    }
                }
                else
                {
                    Console.WriteLine("Unknown response status");
                    throw new Exception("Unknown response status");
                }
            }
            catch (JsonSerializationException ex)
            {
                Console.WriteLine($"JSON deserialization error: {ex.Message}");
                throw;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"An unexpected error occurred: {ex.Message}");
                throw;
            }
        }

        public static void Init()
        {
            LogToEventViewer("Starting setup configuration before service starts.", EventLogEntryType.Information);

            try {
                X509Certificate2? certificate = GetCertFromStore(StoreName.My, session_server_cn);
                if(certificate == null)
                {
                    LogToEventViewer("Server certificate requested.", EventLogEntryType.Information);
                    GetCertificate(session_server_host, "REQUEST_SERVER_CERTIFICATE", MyMachineName);
                }
            } 
            catch (Exception ex)
            {
                LogToEventViewer($"Server certificate not found or invalid: {ex.Message}", EventLogEntryType.Warning);
            }
            try
            {
                X509Certificate2? certificate = GetCertFromStore(StoreName.My, session_server_CA_cn);
                if (certificate == null)
                {
                    LogToEventViewer("CA certificate requested.", EventLogEntryType.Information);
                    GetCertificate(session_server_host, "REQUEST_CA_CERTIFICATE", MyMachineName);
                }
            }
            catch (Exception ex)
            {
                LogToEventViewer($"CA certificate not found or invalid: {ex.Message}", EventLogEntryType.Warning);
            }
            try
            {
                var (publicKey, privateKey) = GenerateRsaKeyPair();
                CreateMyCertificate(publicKey, privateKey);
                LogToEventViewer($"Creating {MyMachineName} CSR and requesting local machine certificate.", EventLogEntryType.Information);
            
            }
            catch (Exception ex)
            {
                LogToEventViewer($"Machine certificate not found or invalid: {ex.Message}", EventLogEntryType.Warning);
            }
        }

        public static string GetFromRegistry(string valueName)
        {
            string keyPath = @"Software\eBZ Tecnologia\WsmConnectorAdService";
            using (RegistryKey? key = Registry.LocalMachine.OpenSubKey(keyPath))
            {
                if (key != null)
                {
                    object? value = key.GetValue(valueName);
                    return value as string ?? "Value not found";
                }
                else
                {
                    return "Registry key not found";
                }
            }
        }
        public static (RsaKeyParameters? Public, RsaPrivateCrtKeyParameters? Private) GetMyKeys()
        {
            X509Certificate2? certificate = GetCertFromStore(StoreName.My, MyMachineName);

            using var pubkey = certificate?.GetRSAPublicKey();
            using var prvkey = certificate?.GetRSAPrivateKey();

            if (pubkey != null && prvkey != null)
            {
                try
                {
                    RsaKeyParameters? publicKey = ReadKeyFromPem<RsaKeyParameters>(pubkey.ExportRSAPublicKeyPem());
                    AsymmetricCipherKeyPair? privateKey = ReadKeyFromPem<AsymmetricCipherKeyPair>(prvkey.ExportRSAPrivateKeyPem());
                    
                    if (privateKey == null || privateKey.Private is not RsaPrivateCrtKeyParameters privateCrtKey)
                    {
                        throw new InvalidOperationException("Failed to parse private key from PEM.");
                    }
                    return (publicKey, (RsaPrivateCrtKeyParameters)privateKey.Private);
                }
                catch (Exception ex)
                {
                    Setup.LogToEventViewer($"Key parsing error: {ex.Message}", EventLogEntryType.Error);
                    throw new InvalidOperationException("Failed to parse RSA key(s) from certificate.", ex);
                }
            }
            throw new InvalidOperationException("Certificate does not contain both public and private RSA keys.");
        }

        private static T? ReadKeyFromPem<T>(string pemKey) where T : class
        {
            using (var reader = new StringReader(pemKey))
            {
                var pemReader = new PemReader(reader);
                return pemReader.ReadObject() as T;
            }
        }

        public static bool IsCertificateAboutToExpire(X509Certificate2 certificate)
        {
            int days = 10;
            DateTime now = DateTime.UtcNow;
            TimeSpan timeUntilExpiry = certificate.NotAfter - now;
            return timeUntilExpiry.TotalDays <= days;
        }

        private static string GetCnFromDistinguishedName(string distinguishedName)
        {
            // Extracts the CN= portion from a DN string
            var parts = distinguishedName.Split(',');
            foreach (var part in parts)
            {
                var trimmed = part.Trim();
                if (trimmed.StartsWith("CN=", StringComparison.OrdinalIgnoreCase))
                {
                    return trimmed.Substring(3);
                }
            }
            return string.Empty;
        }

        public static X509Certificate2? GetCertFromStore(StoreName storeName, string commonName)
        {
            if (string.IsNullOrWhiteSpace(commonName))
                throw new ArgumentException("Common name cannot be null or empty.", nameof(commonName));

            if (string.IsNullOrWhiteSpace(session_server_CA_cn))
                throw new InvalidOperationException("Expected issuer CN (session_server_CA_cn) is not set.");

            using X509Store store = new(storeName, StoreLocation.LocalMachine);
            store.Open(OpenFlags.ReadOnly);

            foreach (X509Certificate2 cert in store.Certificates)
            {
                string cn = GetCnFromDistinguishedName(cert.Subject);
                string issuer = GetCnFromDistinguishedName(cert.Issuer);

                if (cn.Equals(commonName, StringComparison.OrdinalIgnoreCase) &&
                    issuer.Equals(session_server_CA_cn, StringComparison.OrdinalIgnoreCase))
                {
                    return cert;
                }
            }
            //LogToEventViewer($"Certificate with CN '{commonName}' issued by '{session_server_CA_cn}' was not found in store '{storeName}'.", EventLogEntryType.Information);
            return null;
        }


        public static void LogToEventViewer(string message, EventLogEntryType type)
        {
            string source = "WsmConnectorAdService";
            string logName = "Application";

            if (!EventLog.SourceExists(source))
            {
                EventLog.CreateEventSource(source, logName);
            }

            using (EventLog eventLog = new EventLog(logName))
            {
                eventLog.Source = source;
                eventLog.WriteEntry(message, type);
            }
        }
        public static void StoreCertificate(X509Certificate2 certificate, StoreName storeName, StoreLocation storeLocation)
        {
            string commonName = GetCertCommonName(certificate);

            using (var store = new X509Store(storeName, storeLocation))
            {
                store.Open(OpenFlags.ReadWrite);
                X509Certificate2? existingCert = GetCertFromStore(storeName, commonName);

                if (existingCert != null)
                {
                    LogToEventViewer($"{commonName} already in store... Updating it", EventLogEntryType.Information);
                    store.Remove(existingCert);
                }
                store.Add(certificate);
                store.Close();
            }
        }

        public static X509Certificate2 ConvertPemToX509(string pemCertificate)
        {
            // Remove the PEM headers
            // Convert the Base64 string to a byte array
            // Create an X509Certificate2 object from the byte array
            string pem = pemCertificate.Replace("-----BEGIN CERTIFICATE-----", "")
                                       .Replace("-----END CERTIFICATE-----", "")
                                       .Replace("\r", "")
                                       .Replace("\n", "");
            byte[] certificateBytes = Convert.FromBase64String(pem);
            return new X509Certificate2(certificateBytes);
        }

        static (RsaKeyParameters Public, RsaPrivateCrtKeyParameters Private) GenerateRsaKeyPair(int keySize = 2048)
        {
            // Initialize the key generation parameters, create the key pair generator and initialize it
            // Generate the key pair
            var keyGenerationParameters = new KeyGenerationParameters(new SecureRandom(), keySize);
            var keyPairGenerator = new RsaKeyPairGenerator();
            keyPairGenerator.Init(keyGenerationParameters);

            var keyPair = keyPairGenerator.GenerateKeyPair();
            return ((RsaKeyParameters)keyPair.Public, (RsaPrivateCrtKeyParameters)keyPair.Private);
        }


        public static void CreateMyCertificate(RsaKeyParameters publicKey, RsaPrivateCrtKeyParameters privateKey)
        {
            // Generate CSR request
            // Send CSR request to get signed certificate
            // Put private key
            // Get the key container name
            // Set permissions on the private key file
            // Store signed certificate in Store

            var csr = GenerateCSR(publicKey, privateKey);

            X509Certificate2 signedCert = SendCSR(session_server_host, "REQUEST_SIGNED_CERTIFICATE", MyMachineName, csr); 
            
            var privateKeyInfo = PrivateKeyInfoFactory.CreatePrivateKeyInfo(privateKey);
            var RSAPrivateKey = DotNetUtilities.ToRSA((RsaPrivateCrtKeyParameters)PrivateKeyFactory.CreateKey(privateKeyInfo));
            
            X509Certificate2 certificateWithPrivateKey = signedCert.CopyWithPrivateKey(RSAPrivateKey);
            var keyContainerName = GetKeyContainerName(certificateWithPrivateKey);
            if (!string.IsNullOrEmpty(keyContainerName))
            {
                SetPrivateKeyPermissions(keyContainerName);
            }
            StoreCertificate(certificateWithPrivateKey, StoreName.My, StoreLocation.LocalMachine);

        }

        public static string GenerateCSR(RsaKeyParameters publicKey, RsaPrivateCrtKeyParameters privateKey)
        {          
            // Create the subject public key info
            // Define the CSR attributes
            // Create the CSR
            // Convert BouncyCastle CSR to PEM format
            var subject = new X509Name(
                $"OU={"Workday Session Management Connector AD Certificate"}, " +
                $"CN={MyMachineName}");

            var publicKeyInfo = SubjectPublicKeyInfoFactory.CreateSubjectPublicKeyInfo(publicKey);
            var attributes = new DerSet();

            var csr = new Pkcs10CertificationRequest(
                "SHA256WITHRSA",
                subject,
                publicKey,
                attributes,
                privateKey
            );

            StringBuilder csrPem = new StringBuilder();
            var csrPemWriter = new PemWriter(new StringWriter(csrPem));
            csrPemWriter.WriteObject(csr);
            csrPemWriter.Writer.Flush();
            return csrPem.ToString();
        }
        public static X509Certificate2 SendCSR(string routerAddress, string request, string identity, string csr)
        {
            var message = new Dictionary<string, string>
            {
                { "CARequest", "true" },
                { "action", $"{request}" },
                { "csr", csr }
            };
            
            string jsonMessage = System.Text.Json.JsonSerializer.Serialize(message);
            string jsonResponse = SendRequestToRouter(routerAddress, identity, jsonMessage);

            try
            {
                // Desserializa a resposta para a classe ApiResponse
                var response = JsonConvert.DeserializeObject<Response>(jsonResponse);
                if (response?.Status == "error")
                {
                    var errorResponse = JsonConvert.DeserializeObject<ErrorResponse>(jsonResponse);
                    throw new Exception(errorResponse?.Message);
                }
                else if (response?.Status == "success")
                {
                    var successResponse = JsonConvert.DeserializeObject<SuccessResponse>(jsonResponse);
                    if (successResponse?.Data != null)
                    {
                        return ConvertPemToX509(successResponse.Data);
                        //StoreCertificate(ConvertPemToX509(successResponse.Data), StoreName.My, StoreLocation.LocalMachine);
                    }
                    else
                    {
                        throw new Exception("Response contained no certificate data.");
                    }
                }
                else
                {
                    throw new Exception("Unknown response status");
                }
            }
            catch (JsonSerializationException ex)
            {
                Console.WriteLine($"JSON deserialization error: {ex.Message}");
                throw;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"An unexpected error occurred: {ex.Message}");
                throw;
            }
            throw new InvalidOperationException("No valid response was processed.");
        }
        

        private static string? GetKeyContainerName(X509Certificate2 certificate)
        {
            try
            {
                using (var rsa = certificate.GetRSAPrivateKey() as RSACryptoServiceProvider)
                {
                    if (rsa != null)
                        return rsa.CspKeyContainerInfo.UniqueKeyContainerName;
                }
            }
            catch (Exception ex)
            {
                throw new InvalidOperationException("Failed to get the key container name.", ex);
            }
            return null;
        }

        private static void SetPrivateKeyPermissions(string keyContainerName)
        {
            var machineKeyPath = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.CommonApplicationData), @"Microsoft\Crypto\RSA\MachineKeys");
            var keyFilePath = Path.Combine(machineKeyPath, keyContainerName);

            var fileInfo = new FileInfo(keyFilePath);
            var fileSecurity = fileInfo.GetAccessControl();

            var everyone = new SecurityIdentifier(WellKnownSidType.WorldSid, null);
            var accessRule = new FileSystemAccessRule(everyone, FileSystemRights.FullControl, AccessControlType.Allow);

            fileSecurity.AddAccessRule(accessRule);
            fileInfo.SetAccessControl(fileSecurity);
        }

        // Get the subject of the certificate
        // Split the subject by commas to extract different parts
        // Find and display the Common Name (CN)
        public static string GetCertCommonName(X509Certificate2 certificate)
        {
            try
            {
                string subject = certificate.Subject;
                string[] subjectParts = subject.Split(',');
                
                foreach (string part in subjectParts)
                {
                    if (part.Trim().StartsWith("CN="))
                    {
                        return part.Trim().Substring(3);
                    }
                }
                throw new InvalidOperationException("Common Name (CN) not found in certificate subject.");
            }
            catch (Exception ex)
            {
                throw new InvalidOperationException("Failed to extract Common Name (CN) from certificate.", ex);
            }
        }

        public class Response
        {
            public required string Status { get; set; }
        }
        public class ErrorResponse : Response
        {
            public required string Message { get; set; }
        }
        public class SuccessResponse : Response
        {
            public required string Data { get; set; }
        }
        
        public static bool IsJsonFormatable(string input)
        {
            if (string.IsNullOrWhiteSpace(input))
                return false;

            input = input.Trim();
            if (input.StartsWith("{") && input.EndsWith("}") || // For object
                input.StartsWith("[") && input.EndsWith("]"))   // For array
            {
                try
                {
                    Newtonsoft.Json.Linq.JToken.Parse(input);
                    return true;
                }
                catch (JsonReaderException)
                {
                    return false;
                }
                catch (Exception)
                {
                    return false;
                }
            }
            return false;
        }
        public static string GetMachineFQDN()
        {
            string hostname = Dns.GetHostName();
            IPHostEntry hostEntry = Dns.GetHostEntry(hostname);
            return hostEntry.HostName.ToLower();
        }
    }
}