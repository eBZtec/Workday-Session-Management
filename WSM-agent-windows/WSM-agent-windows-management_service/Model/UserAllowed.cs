namespace SessionService.Model
{
    internal class UserAllowed
    {
        public string username { get; set; }
        public AllowedSchedule allowed_schedule { get; set; }


        public static bool allowAll = false;

        public UserAllowed()
        { }

        public UserAllowed(ServerResponse response)
        {
            this.username = response.user;
            this.allowed_schedule = response.allowed_schedule;
        }
    }
}
