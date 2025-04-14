using Org.BouncyCastle.Crypto.Digests;
using Org.BouncyCastle.Crypto.Encodings;
using Org.BouncyCastle.Crypto.Engines;
using Org.BouncyCastle.Crypto.Parameters;
using Org.BouncyCastle.Crypto;
using Org.BouncyCastle.Security;
using System.Text;

using JsonSerializer = System.Text.Json.JsonSerializer;
using System.Security.Cryptography.X509Certificates;
using WsmConnectorAdService.Controller;
using System.Diagnostics;
using Newtonsoft.Json;
using System.Text.Encodings.Web;

namespace WsmConnectorAdService.Utils
{
    internal class Cryptography
    {
        public class ResponsePackage
        {
            public string? EncryptedAESKey { get; set; }
            public string? EncryptedAESIV { get; set; }
            public string? EncryptedMessage { get; set; }
        }

        public class WorkHours
        {
            public int Start { get; set; }
            public int End { get; set; }
        }

        public static string ProcessRequest(string message)
        {
            if (string.IsNullOrWhiteSpace(message))
            {
                throw new ArgumentException("Incoming message cannot be null or empty.");
            }

            ResponsePackage? receivedObject;
            try
            {
                receivedObject = JsonSerializer.Deserialize<ResponsePackage>(message);
                if (receivedObject == null)
                {
                    throw new InvalidOperationException("Failed to parse JSON message into ResponsePackage.");
                }
            }
            catch (JsonException ex)
            {
                throw new InvalidOperationException("Invalid JSON format.", ex);
            }

            try
            {
                // Validate and decode Base64-encoded values
                byte[] encryptedMessage = DecodeBase64OrThrow(receivedObject.EncryptedMessage, nameof(receivedObject.EncryptedMessage));
                byte[] encryptedAesKey = DecodeBase64OrThrow(receivedObject.EncryptedAESKey, nameof(receivedObject.EncryptedAESKey));
                byte[] encryptedAesIv = DecodeBase64OrThrow(receivedObject.EncryptedAESIV, nameof(receivedObject.EncryptedAESIV));

                // Decrypt AES key and IV using RSA private key
                byte[] aesKey = DecryptWithPrivateKey(encryptedAesKey);
                byte[] aesIV = DecryptWithPrivateKey(encryptedAesIv);

                // Decrypt the message using AES key and IV
                byte[] decryptedMessageBytes = DecryptMessage(encryptedMessage, aesKey, aesIV);
                string decryptedMessage = Encoding.UTF8.GetString(decryptedMessageBytes);

                return decryptedMessage;
            }
            catch (Exception ex)
            {
                Setup.LogToEventViewer($"Decryption failed: {ex.Message}", EventLogEntryType.Error);
                throw new InvalidOperationException("Failed to process or decrypt the message.", ex);
            }
        }

        private static byte[] DecodeBase64OrThrow(string? base64, string fieldName)
        {
            if (string.IsNullOrWhiteSpace(base64))
            {
                throw new InvalidOperationException($"Field '{fieldName}' is missing or empty.");
            }

            try
            {
                return Convert.FromBase64String(base64.Trim());
            }
            catch (FormatException ex)
            {
                throw new InvalidOperationException($"Field '{fieldName}' is not a valid Base64 string.", ex);
            }
        }


        public static string processResponse(Worker.ActiveDirectoryResponse response)
        {
            var options = new System.Text.Json.JsonSerializerOptions
            {
                Encoder = JavaScriptEncoder.UnsafeRelaxedJsonEscaping
            };

            // Serialize the object to JSON
            string jsonString = JsonSerializer.Serialize(response, options);

            byte[] aesKey = GenerateAesKey();
            byte[] aesIV = GenerateAesIV();

            byte[] encryptedMessage = EncryptMessage(jsonString, aesKey, aesIV);
            byte[] encryptedAesKey = EncryptWithPublicKey(aesKey);
            byte[] encryptedAesIv = EncryptWithPublicKey(aesIV);

            ResponsePackage jsonObject = new ResponsePackage
            {
                EncryptedMessage = Convert.ToBase64String(encryptedMessage),
                EncryptedAESKey = Convert.ToBase64String(encryptedAesKey),
                EncryptedAESIV = Convert.ToBase64String(encryptedAesIv)
            };

            string jsonMessage = JsonSerializer.Serialize(jsonObject);
            return jsonMessage;
        }

        static byte[] GenerateAesKey()
        {
            const int keySize = 256;
            int keySizeBytes = keySize / 8;
            SecureRandom random = new SecureRandom();
            byte[] key = new byte[keySizeBytes];
            random.NextBytes(key);

            return key;
        }

        static byte[] GenerateAesIV()
        {
            const int ivSizeBytes = 16;
            SecureRandom random = new SecureRandom();
            byte[] iv = new byte[ivSizeBytes];
            random.NextBytes(iv);

            return iv;
        }

        static byte[] EncryptWithPublicKey(byte[] plaintextBytes)
        {
            X509Certificate2? certificate = Setup.GetCertFromStore(StoreName.My, Setup.session_server_cn);
            var rsaKey = certificate?.GetRSAPublicKey();
            AsymmetricKeyParameter rsaKeyParams = DotNetUtilities.GetRsaPublicKey(rsaKey);

            var rsaEngine = new OaepEncoding(
                new RsaEngine(),
                new Sha256Digest(),
                new Sha256Digest(),
                null                
            );

            rsaEngine.Init(true, rsaKeyParams);
            return rsaEngine.ProcessBlock(plaintextBytes, 0, plaintextBytes.Length);
        }

        static byte[] DecryptWithPrivateKey(byte[] ciphertextBytes)
        {
            X509Certificate2? certificate = Setup.GetCertFromStore(StoreName.My, Setup.MyMachineName);
            var rsaKey = certificate?.GetRSAPrivateKey();
            var rsaKeyParams = DotNetUtilities.GetRsaKeyPair(rsaKey).Private as RsaPrivateCrtKeyParameters;

            var rsaEngine = new OaepEncoding(
                new RsaEngine(),
                new Sha256Digest(),
                new Sha256Digest(),
                null              
            );

            rsaEngine.Init(false, rsaKeyParams);
            return rsaEngine.ProcessBlock(ciphertextBytes, 0, ciphertextBytes.Length);
        }

        public static byte[] EncryptMessage(string message, byte[] key, byte[] iv)
        {
            byte[] messageBytes = Encoding.UTF8.GetBytes(message);
            var cipher = CipherUtilities.GetCipher("AES/CBC/PKCS7Padding");
            var keyParam = new KeyParameter(key);
            var ivParam = new ParametersWithIV(keyParam, iv);
            cipher.Init(true, ivParam);

            return cipher.DoFinal(messageBytes);
        }

        static byte[] DecryptMessage(byte[] encryptedMessage, byte[] key, byte[] iv)
        {
            var cipher = CipherUtilities.GetCipher("AES/CBC/PKCS7Padding");
            var keyParam = new KeyParameter(key);
            var ivParam = new ParametersWithIV(keyParam, iv);
            cipher.Init(false, ivParam);

            return cipher.DoFinal(encryptedMessage);
        }

    }
}
