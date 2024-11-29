using Microsoft.Toolkit.Uwp.Notifications;

namespace DesktopAgent.Service
{
    internal class NotificationManager
    {
        public static void SendBasicNotification(string title, string message)
        {
            try
            {
                var osVersion = Environment.OSVersion.Version;
                Version toastVersion = new Version("10.0.0.0");
                if (osVersion >= toastVersion)
                {
                    ShowToastNotification(title, message);
                }
                else
                {
                    ShowSysTrayNotification(title, message);
                }
                LogManager.Log($"Notification -> Title: {title} --- message: {message}");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"An unexpected error occurred: {ex.Message}");
                LogManager.Log($"SendBasicNotification -> An unexpected error occurred: {ex.Message}");
            }
        }
        public static void ShowSysTrayNotification(string title, string message)
        {
            using (NotifyIcon nIcon = new NotifyIcon())
            {
                nIcon.Icon = SystemIcons.Shield;
                nIcon.Visible = true;
                nIcon.ShowBalloonTip(10000, title, message, ToolTipIcon.Info);
            }
        }
        public static void ShowToastNotification(string title, string message)
        {
            new ToastContentBuilder()
                .AddArgument("action", "viewConversation")
                .AddText(title)
                .AddText(message)
                .Show();
        }

        public static void UserInteraction(string title, string message, string options)
        {
            DialogResult dialogResult;
            try
            {
                switch (options)
                {
                    case "abort_retry_ignore":
                        dialogResult = MessageBox.Show(message, title, MessageBoxButtons.AbortRetryIgnore, MessageBoxIcon.Information);
                        break;

                    case "cancel_try_continue":
                        dialogResult = MessageBox.Show(message, title, MessageBoxButtons.CancelTryContinue, MessageBoxIcon.Information);
                        break;

                    case "ok_cancel":
                        dialogResult = MessageBox.Show(message, title, MessageBoxButtons.OKCancel, MessageBoxIcon.Information);
                        break;

                    case "yes_no_cancel":
                        dialogResult = MessageBox.Show(message, title, MessageBoxButtons.YesNoCancel, MessageBoxIcon.Information);
                        break;

                    case "yes_no":
                        dialogResult = MessageBox.Show(message, title, MessageBoxButtons.YesNo, MessageBoxIcon.Information);
                        break;

                    default:
                        dialogResult = MessageBox.Show(message, title, MessageBoxButtons.OK, MessageBoxIcon.Information);
                        break;
                }

                Console.WriteLine($"User Response: {dialogResult}");

                LogManager.Log($"User interaction -> Message: {message} --- User response: {dialogResult}");
            }
            catch (Exception ex)
            {
                LogManager.Log($"UserInteraction -> An unexpected error occurred: {ex.Message}");
            }

        }
    }
}
