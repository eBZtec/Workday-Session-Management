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

        public static void Vigilance(List<UserSession> userSessions, List<UserAllowed> usersAllowed, PublisherSocket publisher)
        {
            NetMQMessage msg = new(2);
            Command cmd = new Command(null, null, null, null);

            while (true)
            {
                userSessions = SessionManager.EnumerateSessions();
                foreach (UserSession user in userSessions)
                {
                    foreach (UserAllowed userAllowed in usersAllowed)
                    {
                        if (user.username.Equals(userAllowed.username))
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
                                    LogManager.Log($"Vigilance -> User: {user.username} not allowed at this time!");

                                    msg = new(2);
                                    msg.Append(user.username);
                                    cmd = new Command("notify", Utils.Utils.unallowed_work_title, Utils.Utils.unallowed_work, "yes_no");
                                    msg.Append(JsonSerializer.Serialize(cmd));

                                    publisher.SendMultipartMessage(msg);
                                    _ = Task.Run(() => LogoffUnallowed(user.sessionID, user.username));
                                    break;

                                case DayOfWeek.Monday:
                                    foreach (Schedule monday in userAllowed.allowed_schedule.monday)
                                    {
                                        if (currentMinutes >= monday.start && currentMinutes <= monday.end)
                                        {
                                            Console.WriteLine($"User: {user.username} allowed to work");
                                            goto default;
                                        }
                                    }
                                    LogManager.Log($"Vigilance -> User: {user.username} not allowed at this time!");

                                    msg = new(2);
                                    msg.Append(user.username);
                                    cmd = new Command("notify", Utils.Utils.unallowed_work_title, Utils.Utils.unallowed_work, "yes_no");
                                    msg.Append(JsonSerializer.Serialize(cmd));

                                    publisher.SendMultipartMessage(msg);
                                    _ = Task.Run(() => LogoffUnallowed(user.sessionID, user.username));
                                    break;

                                case DayOfWeek.Tuesday:
                                    foreach (Schedule tuesday in userAllowed.allowed_schedule.tuesday)
                                    {
                                        if (currentMinutes >= tuesday.start && currentMinutes <= tuesday.end)
                                        {
                                            Console.WriteLine($"User: {user.username} allowed to work");
                                            goto default;
                                        }
                                    }
                                    LogManager.Log($"Vigilance -> User: {user.username} not allowed at this time!");

                                    msg = new(2);
                                    msg.Append(user.username);
                                    cmd = new Command("notify", Utils.Utils.unallowed_work_title, Utils.Utils.unallowed_work, "yes_no");
                                    msg.Append(JsonSerializer.Serialize(cmd));

                                    publisher.SendMultipartMessage(msg);
                                    _ = Task.Run(() => LogoffUnallowed(user.sessionID, user.username));
                                    break;

                                case DayOfWeek.Wednesday:
                                    foreach (Schedule wednesday in userAllowed.allowed_schedule.wednesday)
                                    {
                                        if (currentMinutes >= wednesday.start && currentMinutes <= wednesday.end)
                                        {
                                            Console.WriteLine($"User: {user.username} allowed to work");
                                            goto default;
                                        }
                                    }
                                    LogManager.Log($"Vigilance -> User: {user.username} not allowed at this time!");

                                    msg = new(2);
                                    msg.Append(user.username);
                                    cmd = new Command("notify", Utils.Utils.unallowed_work_title, Utils.Utils.unallowed_work, "yes_no");
                                    msg.Append(JsonSerializer.Serialize(cmd));

                                    publisher.SendMultipartMessage(msg);
                                    _ = Task.Run(() => LogoffUnallowed(user.sessionID, user.username));
                                    break;

                                case DayOfWeek.Thursday:
                                    foreach (Schedule thursday in userAllowed.allowed_schedule.thursday)
                                    {
                                        if (currentMinutes >= thursday.start && currentMinutes <= thursday.end)
                                        {
                                            Console.WriteLine($"User: {user.username} allowed to work");
                                            goto default;
                                        }
                                    }
                                    LogManager.Log($"Vigilance -> User: {user.username} not allowed at this time!");

                                    msg = new(2);
                                    msg.Append(user.username);
                                    cmd = new Command("notify", Utils.Utils.unallowed_work_title, Utils.Utils.unallowed_work, "yes_no");
                                    msg.Append(JsonSerializer.Serialize(cmd));

                                    publisher.SendMultipartMessage(msg);
                                    _ = Task.Run(() => LogoffUnallowed(user.sessionID, user.username));
                                    break;

                                case DayOfWeek.Friday:
                                    foreach (Schedule friday in userAllowed.allowed_schedule.friday)
                                    {
                                        if (currentMinutes >= friday.start && currentMinutes <= friday.end)
                                        {
                                            Console.WriteLine($"User: {user.username} allowed to work");
                                            goto default;
                                        }
                                    }
                                    LogManager.Log($"Vigilance -> User: {user.username} not allowed at this time!");

                                    msg = new(2);
                                    msg.Append(user.username);
                                    cmd = new Command("notify", Utils.Utils.unallowed_work_title, Utils.Utils.unallowed_work, "yes_no");
                                    msg.Append(JsonSerializer.Serialize(cmd));

                                    publisher.SendMultipartMessage(msg);
                                    _ = Task.Run(() => LogoffUnallowed(user.sessionID, user.username));
                                    break;

                                case DayOfWeek.Saturday:
                                    foreach (Schedule saturday in userAllowed.allowed_schedule.saturday)
                                    {
                                        if (currentMinutes >= saturday.start && currentMinutes <= saturday.end)
                                        {
                                            Console.WriteLine($"User: {user.username} allowed to work");
                                            goto default;
                                        }
                                    }
                                    LogManager.Log($"Vigilance -> User: {user.username} not allowed at this time!");

                                    msg = new(2);
                                    msg.Append(user.username);
                                    cmd = new Command("notify", Utils.Utils.unallowed_work_title, Utils.Utils.unallowed_work, "yes_no");
                                    msg.Append(JsonSerializer.Serialize(cmd));

                                    publisher.SendMultipartMessage(msg);
                                    _ = Task.Run(() => LogoffUnallowed(user.sessionID, user.username));
                                    break;

                                default:
                                    break;
                            }
                        }
                    }
                }
                Thread.Sleep(TimeSpan.FromSeconds(30));
            }
        }

        public static void LogoffUnallowed(int id, string username)
        {
            Thread.Sleep(TimeSpan.FromSeconds(5));
            SessionManager.LogoffSession(id, username);
        }
    }
}
