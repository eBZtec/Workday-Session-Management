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
using WsmConnectorAdService.Utils;
using System;
using System.Runtime.ConstrainedExecution;

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
            
            if (GetCertFromStore(StoreName.My, session_server_cn) == null)
            {
                GetCertificate(session_server_host, "REQUEST_SERVER_CERTIFICATE", MyMachineName);
                LogToEventViewer("Server certificate requested.", EventLogEntryType.Information);
            } 
            else
            {
                LogToEventViewer("Server certificate already in Certificate Store.", EventLogEntryType.Information);
            }
            if (GetCertFromStore(StoreName.My, session_server_CA_cn) == null)
            {
                GetCertificate(session_server_host, "REQUEST_CA_CERTIFICATE", MyMachineName);
                LogToEventViewer("CA certificate requested.", EventLogEntryType.Information);
            }
            else
            {
                LogToEventViewer("CA certificate already in Certificate Store.", EventLogEntryType.Information);
            }
            if (GetCertFromStore(StoreName.My, MyMachineName) == null)
            {
                var (publicKey, privateKey) = GenerateRsaKeyPair();
                CreateMyCertificate(publicKey, privateKey);
                LogToEventViewer($"Creating {MyMachineName} CSR and requesting local machine certificate.", EventLogEntryType.Information);
            }
            else
            {
                LogToEventViewer($"{MyMachineName} certificate already in Certificate Store.", EventLogEntryType.Information);
            }
        }

        public static string GetFromRegistry(string valueName)
        {
            string keyPath = @"Software\eBZ Tecnologia\WsmConnectorAdService";
            using (RegistryKey key = Registry.LocalMachine.OpenSubKey(keyPath))
            {
                if (key != null)
                {
                    object value = key.GetValue(valueName);
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
            X509Certificate2 certificate = GetCertFromStore(StoreName.My, MyMachineName);
            var (pubkey, prvkey) = (certificate.GetRSAPublicKey(), certificate.GetRSAPrivateKey());

            if (pubkey != null && prvkey != null)
            {
                RsaKeyParameters publicKey = ReadKeyFromPem<RsaKeyParameters>(pubkey.ExportRSAPublicKeyPem());
                AsymmetricCipherKeyPair privateKey = ReadKeyFromPem<AsymmetricCipherKeyPair>(prvkey.ExportRSAPrivateKeyPem());
                return (publicKey, (RsaPrivateCrtKeyParameters)privateKey.Private);
            }
            return (null, null);
        }

        private static T ReadKeyFromPem<T>(string pemKey) where T : class
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
        private static string GetCommonName(string subject)
        {
            if (string.IsNullOrEmpty(subject))
            {
                return null;
            }

            const string cnPrefix = "CN=";
            string[] parts = subject.Split(',');

            foreach (string part in parts)
            {
                string trimmedPart = part.Trim();
                if (trimmedPart.StartsWith(cnPrefix, StringComparison.OrdinalIgnoreCase))
                {
                    return trimmedPart.Substring(cnPrefix.Length).Trim();
                }
            }

            return null;
        }

        public static X509Certificate2 GetCertFromStore(StoreName storeName, string commonName)
        {
            X509Store store = new(storeName, StoreLocation.LocalMachine);
            store.Open(OpenFlags.ReadOnly);

            foreach (X509Certificate2 cert in store.Certificates)
            {
                string cn = GetCommonName(cert.Subject);
                if (!string.IsNullOrEmpty(commonName) && cn.Equals(commonName, StringComparison.OrdinalIgnoreCase))
                {
                    store.Close();
                    return cert;
                }
            }
            store.Close();
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
                X509Certificate2 existingCert = GetCertFromStore(storeName, commonName);

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
            X509Certificate2 signedCert = SendCSR(session_server_host, "REQUEST_SIGNED_CERTIFICATE",MyMachineName,csr); //SendCSRSigningRequest(csr);
            
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
                $"C={"Country"}, " +
                $"ST={"State"}, " +
                $"L={"Location"}, " +
                $"O={"Organization"}, " +
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
        

        private static string GetKeyContainerName(X509Certificate2 certificate)
        {
            using (var rsa = certificate.GetRSAPrivateKey() as RSACryptoServiceProvider)
            {
                if (rsa != null)
                {
                    return rsa.CspKeyContainerInfo.UniqueKeyContainerName;
                }
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

        public static string GetCertCommonName(X509Certificate2 certificate)
        {
            // Get the subject of the certificate
            // Split the subject by commas to extract different parts
            // Find and display the Common Name (CN)
            string subject = certificate.Subject;
            string[] subjectParts = subject.Split(',');
            foreach (string part in subjectParts)
            {
                if (part.Trim().StartsWith("CN="))
                {
                    return part.Trim().Substring(3);
                }
            }
            return null;
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
        private class StringParser
        {
            public static List<string> ParseStringToList(string input)
            {
                if (string.IsNullOrEmpty(input))
                {
                    return new List<string>();
                }
                var result = new List<string>(input.Split(';', StringSplitOptions.RemoveEmptyEntries));
                return result;
            }
        }

        public class ResultsWrapper<T>
        {
            public List<T>? results { get; set; }

            public string SerializeListToJson()
            {
                return JsonConvert.SerializeObject(this, Newtonsoft.Json.Formatting.Indented);
            }
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
            // return "wsm:" + hostEntry.HostName.ToLower();
            return hostEntry.HostName;
        }
    }
}
