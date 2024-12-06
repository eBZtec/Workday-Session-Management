using Org.BouncyCastle.Crypto;
using Org.BouncyCastle.Crypto.Digests;
using Org.BouncyCastle.Crypto.Encodings;
using Org.BouncyCastle.Crypto.Engines;
using Org.BouncyCastle.Crypto.Parameters;
using Org.BouncyCastle.OpenSsl;
using Org.BouncyCastle.Security;
using System.Security.Cryptography.X509Certificates;
using System.Text;
using JsonSerializer = System.Text.Json.JsonSerializer;

namespace SessionService.Service.Cryptography
{
    internal class Cryptography
    {
        public class ResponsePackage
        {
            public string? EncryptedAESKey { get; set; }
            public string? EncryptedAESIV { get; set; }
            public string? EncryptedMessage { get; set; }
        }

        public static string processRequest(string message)
        {
            // Parse the received JSON
            var receivedObject = JsonSerializer.Deserialize<ResponsePackage>(message);
            if (message == null)
            {
                throw new Exception("Failed to parse JSON message.");
            }

            // Decode Base64-encoded values
            byte[] encryptedMessage = Convert.FromBase64String(receivedObject.EncryptedMessage);
            byte[] encryptedAesKey = Convert.FromBase64String(receivedObject.EncryptedAESKey);
            byte[] encryptedAesIv = Convert.FromBase64String(receivedObject.EncryptedAESIV);

            // Decrypt AES key and IV using RSA private key
            byte[] aesKey = DecryptWithPrivateKey(encryptedAesKey);
            byte[] aesIV = DecryptWithPrivateKey(encryptedAesIv);

            // Decrypt the message using AES key and IV
            byte[] decryptedMessageBytes = DecryptMessage(encryptedMessage, aesKey, aesIV);
            string decryptedMessage = Encoding.UTF8.GetString(decryptedMessageBytes);

            LogManager.Log("Decrypted message from client: " + decryptedMessage);

            return decryptedMessage;
        }

        public static string processResponse()
        {
            var messageToSend = new
            {
                Status = "sucess",
                Message = "AD sucessfully updated"
            };

            // Serialize the object to JSON
            string jsonString = JsonSerializer.Serialize(messageToSend);

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

            LogManager.Log("Sending JSON response to server: " + jsonString);

            return jsonMessage;
        }

        static AsymmetricKeyParameter LoadRsaKeyFromPem(string filePath)
        {
            using (var reader = File.OpenText(filePath))
            {
                PemReader pemReader = new PemReader(reader);
                object keyObject = pemReader.ReadObject();

                if (keyObject is AsymmetricCipherKeyPair keyPair)
                {
                    return keyPair.Private;

                }
                else if (keyObject is AsymmetricKeyParameter privateKey)
                {
                    return privateKey;
                }
                else if (keyObject is AsymmetricKeyParameter publicKey)
                {
                    return publicKey;
                }
                else if (keyObject is AsymmetricKeyParameter keyParameter)
                {
                    return keyParameter;
                }
                else
                {
                    throw new InvalidOperationException("Invalid RSA key format.");
                }
            }
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
            X509Certificate2 certificate = Setup.GetCertFromStore(StoreName.My, "WSM");
            var rsaKey = certificate.GetRSAPublicKey();
            AsymmetricKeyParameter rsaKeyParams = DotNetUtilities.GetRsaPublicKey(rsaKey);

            var rsaEngine = new OaepEncoding(
                new RsaEngine(),
                new Sha256Digest(),
                new Sha256Digest(), // Optional: specify MGF1 digest
                null                // Optional: use default OAEP parameters
            );

            rsaEngine.Init(true, rsaKeyParams);
            return rsaEngine.ProcessBlock(plaintextBytes, 0, plaintextBytes.Length);
        }

        static byte[] DecryptWithPrivateKey(byte[] ciphertextBytes)
        {
            X509Certificate2 certificate = Setup.GetCertFromStore(StoreName.My, Setup.MyMachineName);
            var rsaKey = certificate.GetRSAPrivateKey();
            var rsaKeyParams = DotNetUtilities.GetRsaKeyPair(rsaKey).Private as RsaPrivateCrtKeyParameters;

            var rsaEngine = new OaepEncoding(
                new RsaEngine(),
                new Sha256Digest(),
                new Sha256Digest(), // Optional: specify MGF1 digest
                null                // Optional: use default OAEP parameters
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