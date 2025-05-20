using NetMQ;
using NetMQ.Sockets;
using SessionService.Model;
using System.Text.Json;
namespace SessionService.Service
{
    internal class WorkdayManager
    {
        public static void UpdateUserAllowed(ServerResponse response, List<UserAllowed> usersAllowed, PublisherSocket publisher)
        {
            UserAllowed userWorkhour = new UserAllowed(response);

            NetMQMessage messagemq = new NetMQMessage(2);
            messagemq.Append(userWorkhour.username);
            Command cmd = new Command("notify", Utils.Utils.updated_workhour_title, Utils.Utils.updated_workhour, "yes_no");
            messagemq.Append(JsonSerializer.Serialize(cmd));

            foreach (UserAllowed userAllowed in usersAllowed)
            {
                if (userWorkhour.username.Equals(userAllowed.username))
                {
                    userAllowed.allowed_schedule = userWorkhour.allowed_schedule;
                    publisher.SendMultipartMessage(messagemq);
                    return;
                }
            }
            usersAllowed.Add(userWorkhour);
            publisher.SendMultipartMessage(messagemq);
            return;
        }

        public static async void Vigilance(List<UserSession> userSessions, List<UserAllowed> usersAllowed, PublisherSocket publisher, CancellationToken cancellationToken)
        {
            while (!cancellationToken.IsCancellationRequested)
            {
                try
                {
                    userSessions = SessionManager.EnumerateSessions();
                    SessionManager.DescribeUsers(userSessions);

                    foreach (UserSession user in userSessions)
                    {
                        foreach (UserAllowed userAllowed in usersAllowed)
                        {
                            if (user.username.Equals(userAllowed.username))
                            {

                                if (userAllowed.allowed_schedule != null)
                                {
                                    int currentMinutes = (DateTimeOffset.UtcNow.LocalDateTime.Hour * 60) + DateTimeOffset.UtcNow.LocalDateTime.Minute;

                                    switch (DateTimeOffset.UtcNow.LocalDateTime.DayOfWeek)
                                    {
                                        case DayOfWeek.Sunday:
                                            foreach (Schedule sunday in userAllowed.allowed_schedule.sunday)
                                            {
                                                if (currentMinutes >= sunday.start && currentMinutes <= sunday.end)
                                                {
                                                    goto default;
                                                }
                                            }

                                            if (userAllowed.grace_time > 0)
                                            {
                                                userAllowed.grace_time--;
                                                LogManager.Log($"Vigilance -> User: {user.username} in grace time, minutes remaning: {userAllowed.grace_time}");
                                                break;
                                            }
                                            LogManager.Log($"Vigilance -> User: {user.username} not allowed at this time!");
                                            HandleWrongHour(user.sessionID, user.username, publisher);
                                            break;

                                        case DayOfWeek.Monday:
                                            foreach (Schedule monday in userAllowed.allowed_schedule.monday)
                                            {
                                                if (currentMinutes >= monday.start && currentMinutes <= monday.end)
                                                {
                                                    goto default;
                                                }
                                            }

                                            if (userAllowed.grace_time > 0)
                                            {
                                                userAllowed.grace_time--;
                                                LogManager.Log($"Vigilance -> User: {user.username} in grace time, minutes remaning: {userAllowed.grace_time}");
                                                break;
                                            }
                                            LogManager.Log($"Vigilance -> User: {user.username} not allowed at this time!");
                                            HandleWrongHour(user.sessionID, user.username, publisher);
                                            break;

                                        case DayOfWeek.Tuesday:
                                            foreach (Schedule tuesday in userAllowed.allowed_schedule.tuesday)
                                            {
                                                if (currentMinutes >= tuesday.start && currentMinutes <= tuesday.end)
                                                {
                                                    goto default;
                                                }
                                            }

                                            if (userAllowed.grace_time > 0)
                                            {
                                                userAllowed.grace_time--;
                                                LogManager.Log($"Vigilance -> User: {user.username} in grace time, minutes remaning: {userAllowed.grace_time}");
                                                break;
                                            }
                                            LogManager.Log($"Vigilance -> User: {user.username} not allowed at this time!");
                                            HandleWrongHour(user.sessionID, user.username, publisher);
                                            break;

                                        case DayOfWeek.Wednesday:
                                            foreach (Schedule wednesday in userAllowed.allowed_schedule.wednesday)
                                            {
                                                if (currentMinutes >= wednesday.start && currentMinutes <= wednesday.end)
                                                {
                                                    goto default;
                                                }
                                            }

                                            if (userAllowed.grace_time > 0)
                                            {
                                                userAllowed.grace_time--;
                                                LogManager.Log($"Vigilance -> User: {user.username} in grace time, minutes remaning: {userAllowed.grace_time}");
                                                break;
                                            }
                                            LogManager.Log($"Vigilance -> User: {user.username} not allowed at this time!");
                                            HandleWrongHour(user.sessionID, user.username, publisher);
                                            break;

                                        case DayOfWeek.Thursday:
                                            foreach (Schedule thursday in userAllowed.allowed_schedule.thursday)
                                            {
                                                if (currentMinutes >= thursday.start && currentMinutes <= thursday.end)
                                                {
                                                    goto default;
                                                }
                                            }

                                            if (userAllowed.grace_time > 0)
                                            {
                                                userAllowed.grace_time--;
                                                LogManager.Log($"Vigilance -> User: {user.username} in grace time, minutes remaning: {userAllowed.grace_time}");
                                                break;
                                            }
                                            LogManager.Log($"Vigilance -> User: {user.username} not allowed at this time!");
                                            HandleWrongHour(user.sessionID, user.username, publisher);
                                            break;

                                        case DayOfWeek.Friday:
                                            foreach (Schedule friday in userAllowed.allowed_schedule.friday)
                                            {
                                                if (currentMinutes >= friday.start && currentMinutes <= friday.end)
                                                {
                                                    goto default;
                                                }
                                            }

                                            if (userAllowed.grace_time > 0)
                                            {
                                                userAllowed.grace_time--;
                                                LogManager.Log($"Vigilance -> User: {user.username} in grace time, minutes remaning: {userAllowed.grace_time}");
                                                break;
                                            }
                                            LogManager.Log($"Vigilance -> User: {user.username} not allowed at this time!");
                                            HandleWrongHour(user.sessionID, user.username, publisher);
                                            break;

                                        case DayOfWeek.Saturday:
                                            foreach (Schedule saturday in userAllowed.allowed_schedule.saturday)
                                            {
                                                if (currentMinutes >= saturday.start && currentMinutes <= saturday.end)
                                                {
                                                    goto default;
                                                }
                                            }

                                            if (userAllowed.grace_time > 0)
                                            {
                                                userAllowed.grace_time--;
                                                LogManager.Log($"Vigilance -> User: {user.username} in grace time, minutes remaning: {userAllowed.grace_time}");
                                                break;
                                            }
                                            LogManager.Log($"Vigilance -> User: {user.username} not allowed at this time!");
                                            HandleWrongHour(user.sessionID, user.username, publisher);
                                            break;

                                        default:
                                            break;
                                    }
                                }
                                else
                                {
                                    if (userAllowed.grace_time > 0)
                                    {
                                        userAllowed.grace_time--;
                                        LogManager.Log($"Vigilance -> User: {user.username} in grace time, minutes remaning: {userAllowed.grace_time}");
                                    }
                                    else
                                    {
                                    LogManager.Log($"Vigilance -> User: {user.username} does not have schedule!");
                                    HandleWrongHour(user.sessionID, user.username, publisher);
                                    }
                                }
                            }
                        }
                    }
                }
                catch (Exception ex)
                {
                    LogManager.Log($"Vigilance -> exception: {ex.Message}");
                }

                try
                {
                    await Task.Delay(TimeSpan.FromSeconds(60), cancellationToken);
                }
                catch (TaskCanceledException)
                {
                    break;
                }
            }
        }

        public static void HandleWrongHour(int sessionID, string username, PublisherSocket publisher)
        {
            NetMQMessage msg = new NetMQMessage(2);
            msg.Append(username);
            var cmd = new Command("notify", Utils.Utils.unallowed_work_title, Utils.Utils.unallowed_work, "yes_no");
            msg.Append(JsonSerializer.Serialize(cmd));

            publisher.SendMultipartMessage(msg);
            _ = Task.Run(() => LogoffUnallowed(sessionID, username));
        }

        public static void LogoffUnallowed(int id, string username)
        {
            if(Worker.inAuditMode) return;
            Thread.Sleep(TimeSpan.FromSeconds(10));
            SessionManager.LogoffSession(id, username);
        }
    }
}
