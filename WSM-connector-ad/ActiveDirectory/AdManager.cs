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
using System.Diagnostics;
using WsmConnectorAdService.Controller;
using System.DirectoryServices.Protocols;
using Newtonsoft.Json;
using static WsmConnectorAdService.Utils.Cryptography;


namespace WsmConnectorAdService.ActiveDirectory
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

        [JsonPropertyName("allowed_work_hours")]
        public Dictionary<string, TimeRange[]> AllowedSchedule { get; set; } = new Dictionary<string, TimeRange[]>();
    }
  
    public class AdManager
    {
        string domainName = Setup.GetFromRegistry("ACTIVE_DIRECTORY_HOST");
        string jsonSchedule = "";

        public void updateADLogonHours(string jsonSchedule)
        {
            
            JObject jsonObject = JObject.Parse(jsonSchedule);
            string username = (string)jsonObject["uid"];
            string allowedWorkHours = (string)jsonObject["allowed_work_hours"];
            
            // Deserialize JSON to Dictionary
            var workHoursDictionary = JsonConvert.DeserializeObject<Dictionary<string, TimeRange[]>>(allowedWorkHours);
           
            var options = new JsonSerializerOptions
            {
                PropertyNameCaseInsensitive = true
            };

            DirectoryEntry? user;
            try
            {
                var domainConnection = ConnectToActiveDirectory(domainName);
                if (domainConnection != null)
                {
                    user = FindUserByUsername(domainConnection, username);
                    if (user != null)
                    {
                        // Display old logon hours if any
                        if (user.Properties.Contains("logonHours"))
                        {
                            byte[]? oldLogonHours = user.Properties["logonHours"].Value as byte[];
                            Setup.LogToEventViewer("Old Logon Hours: " + BitConverter.ToString(oldLogonHours ?? Array.Empty<byte>()), EventLogEntryType.Information);
                        }
                        else
                        {
                            Setup.LogToEventViewer("No previous logon hours set.", EventLogEntryType.Information);
                        }

                        // Generate new logon hours based on the schedule
                        //var schedule = JsonConvert.DeserializeObject<Schedule>(jsonSchedule);
                        if (allowedWorkHours != null)
                        {
                            byte[] newLogonHours = GenerateLogonHours(workHoursDictionary);
                            Setup.LogToEventViewer("New Logon Hours: " + BitConverter.ToString(newLogonHours), EventLogEntryType.Information);

                            // Update user's logon hours
                            user.Properties["logonHours"].Value = newLogonHours;
                            user.CommitChanges();

                            Setup.LogToEventViewer("Logon hours have been updated.", EventLogEntryType.Information);
                        }
                        else
                        {
                            throw new InvalidOperationException("Failed to deserialize the schedule.");
                        }
                    }
                    else
                    {
                        throw new InvalidOperationException($"User '{username}' not found in Active Directory.");
                    }
                }
                else
                {
                    throw new InvalidOperationException("Failed to connect to Active Directory.");
                }
            }
            catch (InvalidOperationException ex)
            {
                // Log the error and propagate the exception
                Setup.LogToEventViewer($"Error in updateADLogonHours: {ex.Message}", EventLogEntryType.Error);
                throw;
            }
            catch (Exception ex)
            {
                // Catch any other unexpected errors
                Setup.LogToEventViewer($"Unexpected error in updateADLogonHours: {ex.Message}", EventLogEntryType.Error);
                throw new InvalidOperationException("An unexpected error occurred while updating logon hours.", ex);
            }
        }

        // Função para estabelecer conexão e validar autenticação no Active Directory
        static DirectoryEntry? ConnectToActiveDirectory(string domainName)
        {
            try
            {
                DirectoryEntry domain = new DirectoryEntry($"LDAP://{domainName}");
                object nativeObject = domain.NativeObject;
                return domain;
            }
            catch (LdapException ldapEx)
            {
                Setup.LogToEventViewer($"LDAP error: {ldapEx.Message}", EventLogEntryType.Error);
                throw new InvalidOperationException("Failed to authenticate with the Active Directory. Check credentials and domain settings.", ldapEx);
            }
            catch (Exception ex)
            {
                Setup.LogToEventViewer($"An unexpected error occurred during AD connection: {ex.Message}", EventLogEntryType.Error);
                throw new InvalidOperationException("An unexpected error occurred while connecting to the Active Directory.", ex);
            }
        }

        // Função para buscar o usuário no Active Directory
        static DirectoryEntry? FindUserByUsername(DirectoryEntry domainConnection, string userName)
        {
            try
            {
                // Realiza a busca do usuário com o sAMAccountName fornecido
                using (DirectorySearcher searcher = new DirectorySearcher(domainConnection))
                {
                    searcher.Filter = $"(sAMAccountName={userName})";
                    var result = searcher.FindOne();

                    if (result != null)
                    {
                        return result.GetDirectoryEntry();
                    }
                    else
                    {
                        // Registro no log caso o usuário não seja encontrado
                        Setup.LogToEventViewer($"User '{userName}' not found in domain '{domainConnection.Path}'.", EventLogEntryType.Warning);
                        return null;
                    }
                }
            }
            catch (Exception ex)
            {
                // Log de erros durante a pesquisa
                Setup.LogToEventViewer($"An error occurred while searching for the user: {ex.Message}", EventLogEntryType.Error);
                throw new InvalidOperationException("An unexpected error occurred while searching for the user in Active Directory.", ex);
            }
        }

        // Generate logon hours from schedule
        static byte[] GenerateLogonHours(Dictionary<string, TimeRange[]>? workHoursDictionary)
        {
            byte[] logonHours = new byte[21]; // 21 bytes represent 7 days * 3 bytes per day

            // Initialize all bytes to zero
            for (int i = 0; i < logonHours.Length; i++)
            {
                logonHours[i] = 0;
            }

            //TimeZoneInfo userTimeZone = GetTimeZoneInfo(schedule.TimeZone);

            var allLogMessages = new List<string>(); // Lista para armazenar os logs de todos os dias

            foreach (var day in workHoursDictionary)//schedule.AllowedSchedule)
            {
                int dayIndex = Array.IndexOf(new[] { "SUNDAY", "MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY" }, day.Key);
                var logMessages = new List<string>();
                logMessages.Add($"Processing day: {day.Key}");

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
                        if (timeRange.Start == 0 && timeRange.End == 1)
                        {
                            // Caso especial: liberar todos os horários do dia
                            for (int hour = 0; hour < 24; hour++)
                            {
                                SetBits(logonHours, dayIndex, hour, hour + 1);
                            }
                            break;
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
                            //logMessages.Add($"    User TimeZone: {userTimeZone.StandardName}");

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

                // Adiciona os logs do dia atual na lista geral
                allLogMessages.AddRange(logMessages);
            }

            // Registra todas as mensagens acumuladas em uma única entrada no Event Viewer
            Setup.LogToEventViewer(string.Join("\n", allLogMessages), EventLogEntryType.Information);


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

                Setup.LogToEventViewer($"Warning: Timezone '{timeZoneString}' not found", EventLogEntryType.Information);
                return TimeZoneInfo.Utc;
            }
            catch (Exception ex)
            {
                Setup.LogToEventViewer($"Error finding timezone: {ex.Message}", EventLogEntryType.Information);
                return TimeZoneInfo.Utc;
            }
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
            return string.IsNullOrEmpty(timeRange.Start.ToString()) && string.IsNullOrEmpty(timeRange.End.ToString());
        }
    }
}

