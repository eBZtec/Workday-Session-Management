using SessionService.Model;
using System.Runtime.InteropServices;

namespace SessionService.Service
{
    internal class SessionManager
    {
        private const int WTS_CURRENT_SERVER_HANDLE = 0;
        private const int WTS_USER_NAME = 5;

        [StructLayout(LayoutKind.Sequential)]
        public struct WTS_SESSION_INFO
        {
            public int SessionId;
            public string pWinStationName;
            public WTS_CONNECTSTATE_CLASS State;
        }

        [DllImport("wtsapi32.dll", SetLastError = true)]
        private static extern bool WTSEnumerateSessions(IntPtr hServer, int Reserved, int Version, ref IntPtr ppSessionInfo, ref int pCount);

        [DllImport("wtsapi32.dll")]
        private static extern void WTSFreeMemory(IntPtr pMemory);

        [DllImport("wtsapi32.dll", SetLastError = true)]
        private static extern bool WTSQuerySessionInformation(IntPtr hServer, int sessionId, int wtsInfoClass, out IntPtr ppBuffer, out int pBytesReturned);

        [DllImport("wtsapi32.dll", SetLastError = true)]
        private static extern bool WTSLogoffSession(IntPtr hServer, int sessionId, bool bWait);

        [DllImport("wtsapi32.dll", SetLastError = true)]
        private static extern bool WTSDisconnectSession(IntPtr hServer, int sessionId, bool bWait);

        [DllImport("wtsapi32.dll", SetLastError = true)]
        private static extern IntPtr WTSOpenServer(string pServerName);

        [DllImport("wtsapi32.dll", SetLastError = true)]
        private static extern void WTSCloseServer(IntPtr hServer);

        // --------------

        public static List<UserSession> EnumerateSessions()
        {
            List<UserSession> sessions = new List<UserSession>();
            UserSession user;

            IntPtr pSessionInfo = IntPtr.Zero;
            int sessionCount = 0;

            if (WTSEnumerateSessions((IntPtr)WTS_CURRENT_SERVER_HANDLE, 0, 1, ref pSessionInfo, ref sessionCount))
            {
                int dataSize = Marshal.SizeOf(typeof(WTS_SESSION_INFO));
                IntPtr currentSession = pSessionInfo;

                for (int i = 0; i < sessionCount; i++)
                {
                    WTS_SESSION_INFO sessionInfo = (WTS_SESSION_INFO)Marshal.PtrToStructure(currentSession, typeof(WTS_SESSION_INFO));
                    string userName = GetSessionUserName(sessionInfo.SessionId);

                    if (!userName.Equals("Unknown"))
                    {
                        user = new UserSession(userName, sessionInfo.SessionId, sessionInfo.pWinStationName, sessionInfo.State);
                        sessions.Add(user);
                    }

                    currentSession += dataSize;
                }

                WTSFreeMemory(pSessionInfo);
                return sessions;
            }
            else
            {
                int errorCode = Marshal.GetLastWin32Error();
                Console.WriteLine($"Failed to enumerate sessions. Error code: {errorCode}");
                return new List<UserSession>();
            }
        }

        private static string GetSessionUserName(int sessionId)
        {
            IntPtr buffer = IntPtr.Zero;
            int bytesReturned = 0;

            if (WTSQuerySessionInformation((IntPtr)WTS_CURRENT_SERVER_HANDLE, sessionId, WTS_USER_NAME, out buffer, out bytesReturned) && bytesReturned > 1)
            {
                string userName = Marshal.PtrToStringAnsi(buffer);
                WTSFreeMemory(buffer);
                return userName;
            }

            WTSFreeMemory(buffer);
            return "Unknown";
        }

        public static void Lock(int sessionId)
        {
            string remoteMachine = System.Net.Dns.GetHostName();

            try
            {
                LockRemoteSession(remoteMachine, sessionId);
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error: {ex.Message}");
            }
        }

        private static void LockRemoteSession(string remoteMachine, int sessionId)
        {
            IntPtr serverHandle = WTSOpenServer(remoteMachine);
            if (serverHandle == IntPtr.Zero)
            {
                LogManager.Log($"SessionManager -> Failed to connect to the remote server");
                throw new Exception("Failed to connect to the remote server.");
            }

            try
            {
                bool result = WTSDisconnectSession(serverHandle, sessionId, false);
                if (!result)
                {
                    LogManager.Log($"SessionManager -> Failed to lock the remote session {sessionId}");
                    throw new Exception("Failed to lock the remote session.");
                }
                Console.WriteLine("Successfully locked the remote session.");
                LogManager.Log($"SessionManager -> Successfully locked the remote session {sessionId}");
            }
            finally
            {
                WTSCloseServer(serverHandle);
            }
        }

        public static void LogoffSession(int sessionId)
        {
            bool result = WTSLogoffSession((IntPtr)WTS_CURRENT_SERVER_HANDLE, sessionId, false);
            if (result)
            {
                Console.WriteLine($"Successfully logged off session {sessionId}");
                LogManager.Log($"SessionManager -> Successfully logged off session {sessionId}");
            }
            else
            {
                int errorCode = Marshal.GetLastWin32Error();
                Console.WriteLine($"Failed to log off session {sessionId}. Error code: {errorCode}");
                LogManager.Log($"SessionManager -> Failed to log off session {sessionId}. Error code: {errorCode}");
            }
        }

        public static void DescribeUsers(List<UserSession> users)
        {
            foreach (UserSession user in users)
            {
                Console.WriteLine(user);
            }
        }

        public static List<int> GetSessionIDs(string user_id, List<UserSession> sessions)
        {
            List<int> ids = new List<int>();
            foreach (UserSession user in sessions)
            {
                if (user.username.Equals(user_id))
                {
                    ids.Add(user.sessionID);
                }
            }
            return ids;
        }
    }
}
