using Microsoft.Win32;
using NetMQ;
using NetMQ.Sockets;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using Org.BouncyCastle.Asn1;
using Org.BouncyCastle.Asn1.X509;
using Org.BouncyCastle.Crypto;
using Org.BouncyCastle.Crypto.Generators;
using Org.BouncyCastle.Crypto.Parameters;
using Org.BouncyCastle.OpenSsl;
using Org.BouncyCastle.Pkcs;
using Org.BouncyCastle.Security;
using Org.BouncyCastle.X509;
using System.Diagnostics;
using System.Net;
using System.Security.AccessControl;
using System.Security.Cryptography;
using System.Security.Cryptography.X509Certificates;
using System.Security.Principal;
using System.Text;

namespace SessionService.Service.Cryptography
{
    public class Setup
    {
        public static string MyMachineName = GetMachineFQDN();
        public static List<string> hosts = StringParser.ParseStringToList("wsm.safra.lab");

        public void Start()
        {
            LogManager.Log("Starting setup configuration before service starts.");

            if (GetCertFromStore(StoreName.My, "WSM-CA") == null)
            {
                LogManager.Log("CA certificate requested.");
                RequestCertificate("WSM-CA");
            }
            else
            {
                LogManager.Log("CA certificate already in Certificate Store.");
            }
            if (GetCertFromStore(StoreName.My, "WSM") == null)
            {
                LogManager.Log("Server certificate requested.");
                RequestCertificate("WSM");
            }
            else
            {
                LogManager.Log("Server certificate already in Certificate Store.");
            }
            if (GetCertFromStore(StoreName.My, MyMachineName) == null)
            {
                var (publicKey, privateKey) = GenerateRsaKeyPair();
                CreateMyCertificate(publicKey, privateKey);
                LogManager.Log($"Creating {MyMachineName} CSR and requesting local machine certificate.");
            }
            else
            {
                LogManager.Log($"{MyMachineName} certificate already in Certificate Store.");
            }
        }

        private static string CreateJson(string key, string value)
        {
            JObject jsonObject = new JObject
            {
                {key,value}
            };
            return jsonObject.ToString();
        }

        public static void SaveInRegistry(string valueName, string encryptedPassword)
        {
            string keyPath = @"Software\eBZ Tecnologia\WsmAgent";
            using (RegistryKey key = Registry.LocalMachine.CreateSubKey(keyPath))
            {
                key.SetValue(valueName, encryptedPassword);
                key.Close();
            }
        }
        public static string GetFromRegistry(string valueName)
        {
            string keyPath = @"Software\eBZ Tecnologia\WsmAgent";
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

            return null; // CN not found
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

        public void RequestCertificate(string certificate_name)
        {
            var request_string = "REQUEST_" + certificate_name;
            using (var requester = new RequestSocket())
            {
                bool connected = false;
                foreach (var host in hosts)
                {
                    LogManager.Log($"Trying to connect to host {host}");

                    try
                    {
                        requester.Connect($"tcp://wsm.safra.lab:44900");
                        connected = true;
                        break;
                    }
                    catch (Exception ex)
                    {
                        LogManager.Log($"Failed to connect to host {host}: {ex.Message}");
                    }
                }
                if (!connected)
                {
                    LogManager.Log($"Could not connect to any host defined in CA_HOST.");
                    throw new Exception("Could not connect to any host defined in CA_HOST.");
                }
                try
                {
                    var requestData = new Dictionary<string, string>
                    {
                        { "action", request_string }
                    };
                    string jsonRequest = Newtonsoft.Json.JsonConvert.SerializeObject(requestData);

                    requester.SendFrame(jsonRequest);
                    var jsonResponse = requester.ReceiveFrameString();

                    var response = JsonConvert.DeserializeObject<Response>(jsonResponse);
                    if (response?.Status == "error")
                    {
                        var errorResponse = JsonConvert.DeserializeObject<ErrorResponse>(jsonResponse);
                    }
                    else if (response?.Status == "success")
                    {
                        var successResponse = JsonConvert.DeserializeObject<SuccessResponse>(jsonResponse);
                        if (successResponse?.Data != null)
                        {
                            StoreCertificate(ConvertPemToX509(successResponse.Data), StoreName.My, StoreLocation.LocalMachine);
                        }
                    }
                    else
                    {
                        LogManager.Log(response.ToString());

                        LogManager.Log("Unknown response status");
                    }
                }
                catch (NetMQException ex)
                {
                    LogManager.Log("Failed to connect to the server: " + ex.Message);
                }
                catch (Exception ex)
                {
                    LogManager.Log("An unexpected error occurred: " + ex.Message);
                }
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
                    LogManager.Log($"Cert setup -> {commonName} already in store... Updating it");
                    store.Remove(existingCert);
                }
                store.Add(certificate);
                store.Close();
            }
        }

        public static string ConvertX509ToPem(X509Certificate2 certificate)
        {
            // Convert the .NET X509Certificate2 to BouncyCastle X509Certificate
            var bcCert = DotNetUtilities.FromX509Certificate(certificate);

            using (var stringWriter = new StringWriter())
            {
                var pemWriter = new PemWriter(stringWriter);
                pemWriter.WriteObject(bcCert);
                pemWriter.Writer.Flush();
                return stringWriter.ToString();
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
            X509Certificate2 signedCert = SendCSRSigningRequest(csr);
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
                $"C={"BR"}, " +
                $"ST={"RS"}, " +
                $"L={"Encruzilhada do Sul"}, " +
                $"O={"eBZ Tecnologia"}, " +
                $"OU={"SafraWSM"}, " +
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

        public static X509Certificate2 SendCSRSigningRequest(string csr)
        {
            // Send the JSON request
            // Receive the signed certificate
            // Parse the common part of the response
            var requestData = new Dictionary<string, string>
            {
                { "action", "REQUEST_SIGNED_CERTIFICATE" },
                { "csr", csr }
            };
            string jsonRequest = JsonConvert.SerializeObject(requestData);

            bool connected = false;
            string jsonResponse = null;

            using (var requester = new RequestSocket())
            {
                foreach (var host in hosts)
                {
                    try
                    {
                        string requestUrl = $"tcp://wsm.safra.lab:44900";
                        requester.Connect(requestUrl);
                        connected = true;

                        LogManager.Log($"Connected to {requestUrl}. Sending CSR to CA...");
                        requester.SendFrame(jsonRequest);
                        jsonResponse = requester.ReceiveFrameString();
                        break;
                    }
                    catch (Exception ex)
                    {
                        LogManager.Log($"Failed to send certificate signing request (CSR) to host {host}: {ex.Message}");
                    }
                }
            }
            if (!connected || string.IsNullOrEmpty(jsonResponse))
            {
                throw new Exception("Could not connect to any host or receive response.");
            }

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
        public static string CreateErrorResponse(string errorMessage)
        {
            var errorData = new Dictionary<string, string> { { "error", errorMessage } };
            return JsonConvert.SerializeObject(errorData);
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
                    JToken.Parse(input);
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
        public static String GetMachineFQDN()
        {
            string hostname = Dns.GetHostName();
            IPHostEntry hostEntry = Dns.GetHostEntry(hostname);
            return "wsm:" + hostEntry.HostName.ToLower();
        }
    }
}