using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

using System.DirectoryServices;
using System.Text.Json;
using System.Text.Json.Serialization;
using System.Linq;
using System.Globalization;
using Newtonsoft.Json.Linq;
using System.Collections;
using Org.BouncyCastle.Utilities;

using WsmConnectorAdService;

namespace WsmConnectorAd
{
    // Struct to represent a time range
    public struct TimeRange
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

        [JsonPropertyName("allowed_schedule")]
        public Dictionary<string, TimeRange[]> AllowedSchedule { get; set; } = new Dictionary<string, TimeRange[]>();
    }

    public class AdManager
    {
        string userToUpdateHours = "";
        string domainName = "";
        string jsonSchedule = "";

        public void updateADLogonHours(string request)
        {
            jsonSchedule = request;

            JObject jsonObject = JObject.Parse(jsonSchedule);
            string username = (string)jsonObject["user"];

            userToUpdateHours = username;

            var options = new JsonSerializerOptions
            {
                PropertyNameCaseInsensitive = true
            };

            DirectoryEntry? user = FindUserByUsername(domainName, userToUpdateHours);

            if (user != null)
            {
                // Display old logon hours if any
                if (user.Properties.Contains("logonHours"))
                {
                    byte[]? oldLogonHours = user.Properties["logonHours"].Value as byte[];
                    LogManager.Log("Old Logon Hours: " + BitConverter.ToString(oldLogonHours ?? Array.Empty<byte>()));
                }
                else
                {
                    LogManager.Log("No previous logon hours set.");
                }

                // Generate new logon hours based on the schedule
                var schedule = JsonSerializer.Deserialize<Schedule>(jsonSchedule, options);
                if (schedule != null)
                {
                    byte[] newLogonHours = GenerateLogonHours(schedule);
                    LogManager.Log("New Logon Hours: " + BitConverter.ToString(newLogonHours));

                    // Update user's logon hours
                    user.Properties["logonHours"].Value = newLogonHours;
                    user.CommitChanges();

                    LogManager.Log("Logon hours have been updated.");
                }
                else
                {
                    LogManager.Log("Failed to deserialize schedule.");
                }
            }
            else
            {
                LogManager.Log("User not found.");
            }
        }

        // Method to find user by username in Active Directory
        static DirectoryEntry? FindUserByUsername(string domainName, string userName)
        {
            try
            {
                DirectoryEntry domain = new DirectoryEntry($"LDAP://{domainName}","", "");
                DirectorySearcher searcher = new DirectorySearcher(domain);
                searcher.Filter = $"(sAMAccountName={userName})";
                return searcher.FindOne()?.GetDirectoryEntry();
            }
            catch (Exception ex)
            {
                LogManager.Log($"An error occurred while searching for the user: {ex.Message}");
                return null;
            }
        }

        // Generate logon hours from schedule
        static byte[] GenerateLogonHours(Schedule schedule)
        {
            byte[] logonHours = new byte[21]; // 21 bytes represent 7 days * 3 bytes per day

            // Initialize all bytes to zero
            for (int i = 0; i < logonHours.Length; i++)
            {
                logonHours[i] = 0;
            }

            TimeZoneInfo userTimeZone = GetTimeZoneInfo(schedule.TimeZone);

            foreach (var day in schedule.AllowedSchedule)
            {
                int dayIndex = Array.IndexOf(new[] { "sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday" }, day.Key);
                LogManager.Log($"\n\nProcessing day: {day.Key}, dayIndex: {dayIndex}, timezone: {schedule.TimeZone}");
                if (dayIndex == -1) continue;

                if (day.Value != null && day.Value.Length > 0)
                {
                    LogManager.Log($"  Allowed times:");
                    foreach (var timeRange in day.Value)
                    {
                        if (!IsEmptyTimeRange(timeRange))
                        {
                            int localStartHour = timeRange.Start / 60;
                            int localStartMinute = timeRange.Start % 60;

                            int localEndHour = timeRange.End / 60;
                            int localEndMinute = timeRange.End % 60;

                            // Parse times and convert to UTC
                            DateTime localStart = DateTime.ParseExact($"{localStartHour:D2}:{localStartMinute:D2}", "HH:mm", null, DateTimeStyles.AssumeLocal);
                            DateTime localEnd = DateTime.ParseExact($"{localEndHour:D2}:{localEndMinute:D2}", "HH:mm", null, DateTimeStyles.AssumeLocal);


                            // Round up end time if not on the hour
                            if (localEnd.Minute > 0)
                            {
                                localEnd = localEnd.AddHours(1).AddMinutes(-localEnd.Minute);
                            }

                            LogManager.Log($"  Local Start: {localStart} - {localStart.Kind}");
                            LogManager.Log($"  Local End: {localEnd} - {localEnd.Kind}");
                            LogManager.Log($"  userTimeZone: {userTimeZone.StandardName}, ID: {userTimeZone.Id}, Offset: {userTimeZone.BaseUtcOffset}");

                            var utcStart = TimeZoneInfo.ConvertTimeToUtc(localStart);
                            var utcEnd = TimeZoneInfo.ConvertTimeToUtc(localEnd);

                            int startHour = utcStart.Hour;
                            int endHour = utcEnd.Hour;

                            bool spansToNextDay = (utcStart.DayOfWeek < utcEnd.DayOfWeek || endHour < startHour);
                            bool startsOnNextDay = utcStart.DayOfWeek > utcEnd.DayOfWeek;

                            LogManager.Log($"    From: {timeRange.Start} To: {timeRange.End}, utcStart: {utcStart.DayOfWeek}, utcEnd: {utcEnd.DayOfWeek}, " + (spansToNextDay ? " (Spans to next day)" : ""));

                            if (spansToNextDay)
                            {
                                // Set bits for current day
                                for (int hour = startHour; hour < 24; hour++)
                                {
                                    SetBits(logonHours, dayIndex % 7, hour, hour + 1);
                                    LogManager.Log($"      Setting bit for current day, hour: {hour} on day {dayIndex}");
                                }

                                // Set bits for next day up to end hour
                                for (int hour = 0; hour < endHour; hour++)
                                {
                                    SetBits(logonHours, (dayIndex + 1) % 7, hour, hour + 1);
                                    LogManager.Log($"      Setting bit for next day, hour: {hour} on day {(dayIndex + 1) % 7}");
                                }
                                if (endHour != 0)
                                {
                                    SetBits(logonHours, (dayIndex + 1) % 7, endHour - 1, endHour);
                                    LogManager.Log($"      Setting end hour {endHour} on day {(dayIndex + 1) % 7}");
                                }
                            }
                            else if (startsOnNextDay)
                            {
                                // Set bits for next day only
                                for (int hour = startHour; hour < endHour; hour++)
                                {
                                    SetBits(logonHours, (dayIndex + 1) % 7, hour, hour + 1);
                                    LogManager.Log($"      Setting bit for next day, hour: {hour} on day {(dayIndex + 1) % 7}");
                                }
                            }
                            else
                            {
                                // Set bits for the same day
                                for (int hour = startHour; hour < endHour; hour++)
                                {
                                    SetBits(logonHours, dayIndex % 7, hour, hour + 1);
                                    LogManager.Log($"      Setting bit for hour: {hour} on day {dayIndex}");
                                }
                            }
                        }
                        else
                        {
                            LogManager.Log("    Empty TimeRange encountered.");
                        }
                    }
                }
                else
                {
                    LogManager.Log("  No allowed times for this day.");
                }
            }

            return logonHours;
        }

        // Method to get TimeZoneInfo based on provided timezone string
        static TimeZoneInfo GetTimeZoneInfo(string timeZoneString)
        {
            try
            {
                if (TimeZoneInfo.GetSystemTimeZones().Any(tz => string.Equals(tz.StandardName, timeZoneString, StringComparison.OrdinalIgnoreCase)))
                {
                    return TimeZoneInfo.FindSystemTimeZoneById(timeZoneString);
                }

                if (timeZoneString.StartsWith("UTC", StringComparison.OrdinalIgnoreCase))
                {
                    var offsetString = timeZoneString.Substring(3).Trim();
                    bool isNegative = offsetString.StartsWith("-");
                    offsetString = offsetString.TrimStart('-');
                    var timeParts = offsetString.Split(':');
                    int hours;
                    int minutes = 0;

                    if (int.TryParse(timeParts[0], out hours))
                    {
                        if (timeParts.Length > 1 && int.TryParse(timeParts[1], out minutes))
                        {
                            var offset = new TimeSpan(0, hours * (isNegative ? -1 : 1), minutes, 0, 0);
                            return TimeZoneInfo.GetSystemTimeZones().FirstOrDefault(tz => tz.BaseUtcOffset == offset) ?? TimeZoneInfo.Utc;
                        }
                        else
                        {
                            var offset = new TimeSpan(0, hours * (isNegative ? -1 : 1), 0, 0, 0);
                            return TimeZoneInfo.GetSystemTimeZones().FirstOrDefault(tz => tz.BaseUtcOffset == offset) ?? TimeZoneInfo.Utc;
                        }
                    }
                }

                LogManager.Log($"Warning: Timezone '{timeZoneString}' not found, defaulting to UTC.");
                return TimeZoneInfo.Utc;
            }
            catch (Exception ex)
            {
                LogManager.Log($"Error finding timezone: {ex.Message}");
                return TimeZoneInfo.Utc;
            }
        }

        // Helper method to set bits in the logon hours array
        static void SetBits(byte[] hours, int dayIndex, int startHour, int endHour)
        {
            for (int hour = startHour; hour < endHour; hour++)
            {
                int byteIndex = dayIndex * 3 + (hour % 24) / 8;
                int bitIndex = (hour % 24) % 8;
                hours[byteIndex] |= (byte)(1 << bitIndex);
            }
        }

        // Check if a TimeRange is empty
        static bool IsEmptyTimeRange(TimeRange timeRange)
        {
            return (string.IsNullOrEmpty((timeRange.Start).ToString()) && (string.IsNullOrEmpty((timeRange.End).ToString())));
        }
    }
}

