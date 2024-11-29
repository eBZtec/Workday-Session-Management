using DirectoryEntry = System.DirectoryServices.DirectoryEntry;

namespace WsmConnectorAdService
{
    public class AdConnectionTester
    {
        private readonly ILogger<Worker> _logger;

        public AdConnectionTester(ILogger<Worker> logger)
        {
            _logger = logger;
        }

        /// <summary>
        /// Tests the connection to an Active Directory server.
        /// </summary>
        /// <param name="ldapPath">The LDAP path (e.g., LDAP://yourdomain.com).</param>
        /// <param name="username">The username to authenticate with (e.g., DOMAIN\username).</param>
        /// <param name="password">The password for the username.</param>
        /// <returns>True if the connection is successful, false otherwise.</returns>
        public bool TestAdConnection(string ldapPath, string username, string password)
        {
            try
            {
                using (var entry = new DirectoryEntry(ldapPath, username, password))
                {
                    // Force the bind to check credentials and connection
                    var obj = entry.NativeObject;

                    _logger.LogInformation("Successfully connected to AD at {LdapPath} with user {Username}.", ldapPath, username);
                    return true;
                }
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to connect to AD at {LdapPath} with user {Username}.", ldapPath, username);
                return false;
            }
        }
    }
}
