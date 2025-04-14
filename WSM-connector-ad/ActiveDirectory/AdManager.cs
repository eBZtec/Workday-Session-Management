using System.DirectoryServices;
using System.Text.Json.Serialization;
using System.Globalization;
using Newtonsoft.Json.Linq;
using System.Diagnostics;
using WsmConnectorAdService.Controller;
using Newtonsoft.Json;
using System.DirectoryServices.AccountManagement;

using JsonException = Newtonsoft.Json.JsonException;

namespace WsmConnectorAdService.ActiveDirectory
{
    // Class to represent a time range
    public class TimeRange
    {
        [JsonPropertyName("start")]
        public int Start { get; set; }
        [JsonPropertyName("end")]
        public int End { get; set; }
    }

    // Class to encapsulate user's schedule
    public class Schedule
    {
        [JsonPropertyName("timezone")]
        public string TimeZone { get; set; } = string.Empty;

        [JsonPropertyName("allowed_work_hours")]
        public Dictionary<string, TimeRange[]> AllowedSchedule { get; set; } = new Dictionary<string, TimeRange[]>();
    }
  
    public class AdManager
    {
        string domainName = Setup.GetFromRegistry("ACTIVE_DIRECTORY_HOST");

        public string UpdateAdUser(string jsonRequest)
        {
            JObject jsonObject = JObject.Parse(jsonRequest);

            string? username = (string?)jsonObject["uid"];
            string? enableAccount = (string?)jsonObject["enable"];
            string? unlockAccount = (string?)jsonObject["unlock"];
            string? allowedWorkHours = (string?)jsonObject["allowed_work_hours"];

            if (string.IsNullOrWhiteSpace(username))
                throw new ArgumentException("Username (uid) is required in the JSON input.");

            var actionsTaken = new List<string>();

            try
            {
                using (var context = new PrincipalContext(ContextType.Domain, domainName))
                using (var user = UserPrincipal.FindByIdentity(context, IdentityType.SamAccountName, username))
                {
                    if (user == null)
                        throw new InvalidOperationException($"User '{username}' not found in Active Directory.");

                    var directoryEntry = (DirectoryEntry)user.GetUnderlyingObject();

                    if (!string.IsNullOrWhiteSpace(enableAccount))
                    {
                        bool shouldEnable = enableAccount.Equals("true", StringComparison.OrdinalIgnoreCase);
                        user.Enabled = shouldEnable;
                        user.Save();
                        var enableMsg = $"User '{username}' has been {(shouldEnable ? "enabled" : "disabled")}";
                        Setup.LogToEventViewer(enableMsg, EventLogEntryType.Information);
                        actionsTaken.Add(enableMsg);
                    }

                    if (!string.IsNullOrWhiteSpace(unlockAccount) && unlockAccount.Equals("true", StringComparison.OrdinalIgnoreCase))
                    {
                        if (user.IsAccountLockedOut())
                        {
                            user.UnlockAccount();
                            user.Save();
                            var unlockMsg = $"User '{username}' has been unlocked.";
                            Setup.LogToEventViewer(unlockMsg, EventLogEntryType.Information);
                            actionsTaken.Add(unlockMsg);
                        }
                        else
                        {
                            var notLockedMsg = $"User '{username}' is not locked.";
                            Setup.LogToEventViewer(notLockedMsg, EventLogEntryType.Information);
                            actionsTaken.Add(notLockedMsg);
                        }
                    }

                    if (!string.IsNullOrWhiteSpace(allowedWorkHours))
                    {
                        Dictionary<string, TimeRange[]> workHoursDictionary = JsonConvert.DeserializeObject<Dictionary<string, TimeRange[]>>(allowedWorkHours)
                            ?? throw new InvalidOperationException("Deserialization of allowed_work_hours resulted in null.");

                        byte[] newLogonHours = GenerateLogonHours(workHoursDictionary);

                        directoryEntry.Properties["logonHours"].Value = newLogonHours;
                        directoryEntry.CommitChanges();
                        var logonMsg = "Logon hours have been updated.";
                        Setup.LogToEventViewer(logonMsg, EventLogEntryType.Information);
                        actionsTaken.Add(logonMsg);
                    }
                }
                return string.Join(" | ", actionsTaken);
            }
            catch (JsonException ex)
            {
                Setup.LogToEventViewer($"JSON error in UpdateAdUser: {ex.Message}", EventLogEntryType.Error);
                throw new InvalidOperationException("Failed to parse input JSON.", ex);
            }
            catch (Exception ex)
            {
                Setup.LogToEventViewer($"Unexpected error in UpdateAdUser: {ex.Message}", EventLogEntryType.Error);
                throw new InvalidOperationException("An unexpected error occurred while updating the AD user.", ex);
            }
        }

        // Generate logon hours from schedule
        // Initialize all bytes to zero
        static byte[] GenerateLogonHours(Dictionary<string, TimeRange[]> workHoursDictionary)
        {
            byte[] logonHours = new byte[21]; // 21 bytes represent 7 days * 3 bytes per day
            for (int i = 0; i < logonHours.Length; i++)
                logonHours[i] = 0;

            var allLogMessages = new List<string>(); // Lista para armazenar os logs de todos os dias

            foreach (var day in workHoursDictionary)
            {
                int dayIndex = Array.IndexOf(["SUNDAY", "MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY"], day.Key);
                var logMessages = new List<string>
                {
                    $"Processing day: {day.Key}"
                };

                if (dayIndex == -1)
                {
                    logMessages.Add($"Invalid day: {day.Key}. Skipping.");
                    allLogMessages.AddRange(logMessages);
                    continue;
                }

                if (day.Value != null && day.Value.Length > 0)
                {
                    logMessages.Add("  Allowed times:");
                    foreach (var timeRange in day.Value)
                    {
                        // Caso especial: liberar todos os horários do dia
                        if (timeRange.Start == 0 && timeRange.End == 1)
                        {
                            timeRange.End = 1439;
                        }
                        if (!IsEmptyTimeRange(timeRange))
                        {
                            int localStartHour = timeRange.Start / 60;
                            int localStartMinute = timeRange.Start % 60;
                            int localEndHour = timeRange.End / 60;
                            int localEndMinute = timeRange.End % 60;

                            DateTime localStart = DateTime.ParseExact($"{localStartHour:D2}:{localStartMinute:D2}", "HH:mm", null, DateTimeStyles.AssumeLocal);
                            DateTime localEnd = DateTime.ParseExact($"{localEndHour:D2}:{localEndMinute:D2}", "HH:mm", null, DateTimeStyles.AssumeLocal);

                            if (localEnd.Minute > 0)
                                localEnd = localEnd.AddHours(1).AddMinutes(-localEnd.Minute);

                            logMessages.Add($"    Local Start: {localStart} - {localStart.Kind}");
                            logMessages.Add($"    Local End: {localEnd} - {localEnd.Kind}");

                            var utcStart = TimeZoneInfo.ConvertTimeToUtc(localStart);
                            var utcEnd = TimeZoneInfo.ConvertTimeToUtc(localEnd);

                            int startHour = utcStart.Hour;
                            int endHour = utcEnd.Hour;

                            bool spansToNextDay = utcStart.DayOfWeek < utcEnd.DayOfWeek || endHour < startHour;
                            bool startsOnNextDay = utcStart.DayOfWeek > utcEnd.DayOfWeek;

                            logMessages.Add($"    From: {timeRange.Start} To: {timeRange.End}");

                            if (spansToNextDay)
                            {
                                for (int hour = startHour; hour < 24; hour++)
                                    SetBits(logonHours, dayIndex % 7, hour, hour + 1);
                                for (int hour = 0; hour < endHour; hour++)
                                    SetBits(logonHours, (dayIndex + 1) % 7, hour, hour + 1);
                                if (endHour != 0)
                                    SetBits(logonHours, (dayIndex + 1) % 7, endHour - 1, endHour);

                                logMessages.Add("      Spans to next day. Bits set for current and next day.");
                            }
                            else if (startsOnNextDay)
                            {
                                for (int hour = startHour; hour < endHour; hour++)
                                    SetBits(logonHours, (dayIndex + 1) % 7, hour, hour + 1);

                                logMessages.Add("      Starts on next day. Bits set for next day.");
                            }
                            else
                            {
                                for (int hour = startHour; hour < endHour; hour++)
                                    SetBits(logonHours, dayIndex % 7, hour, hour + 1);

                                logMessages.Add($"      Same day. Bits set for hours {startHour} to {endHour}.");
                            }
                        }
                        else
                        {
                            logMessages.Add("    Empty TimeRange encountered.");
                        }
                    }
                }
                else
                {
                    logMessages.Add("  No allowed times for this day.");
                }
                allLogMessages.AddRange(logMessages);
            }
            //Setup.LogToEventViewer(string.Join("\n", allLogMessages), EventLogEntryType.Information);
            return logonHours;
        }

        // Helper method to set bits in the logon hours array
        static void SetBits(byte[] hours, int dayIndex, int startHour, int endHour)
        {
            for (int hour = startHour; hour < endHour; hour++)
            {
                int byteIndex = dayIndex * 3 + hour % 24 / 8;
                int bitIndex = hour % 24 % 8;
                hours[byteIndex] |= (byte)(1 << bitIndex);
            }
        }

        // Check if a TimeRange is empty
        static bool IsEmptyTimeRange(TimeRange timeRange)
        {
            return timeRange.Start == 0 && timeRange.End == 0;
        }

        
    }
}

