namespace SessionService.Model
{
    internal class UserSession
    {
        public string username { get; set; }
        public int sessionID { get; set; }
        public string pWinStationName { get; set; }
        public WTS_CONNECTSTATE_CLASS state { get; set; }

        public UserSession(string username, int sessionID, string pWinStationName, WTS_CONNECTSTATE_CLASS state)
        {
            this.username = username;
            this.sessionID = sessionID;
            this.pWinStationName = pWinStationName;
            this.state = state;
        }

        public override string ToString()
        {
            return "ID: " + sessionID + " - User: " + username + " - StationName: " + pWinStationName + " - State: " + state;
        }
    }
    public enum WTS_CONNECTSTATE_CLASS
    {
        WTSActive,          //atualmente ativo e interagindo com a sessão. A sessão está em uso
        WTSConnected,       //A sessão do usuário está conectada a um cliente remoto, mas não está ativa no momento
        WTSConnectQuery,    //A sessão está em um estado intermediário de conexão, aguardando que a conexão seja totalmente estabelecida
        WTSShadow,          //A sessão está sendo espelhada ou monitorada (shadowed), indicando que outro usuário ou administrador está observando ou controlando essa sessão
        WTSDisconnected,    //A sessão foi desconectada, mas ainda está ativa no servidor. Nenhum cliente está conectado a ela.
        WTSIdle,            //A sessão está ociosa e não está em uso. Não há atividades em andamento.
        WTSListen,          //A sessão está aguardando uma conexão. Isso geralmente indica um estado de escuta em que a sessão aguarda uma solicitação de cliente.
        WTSReset,           //A sessão está sendo reiniciada. Todos os recursos alocados são liberados, e a sessão é redefinida.
        WTSDown,            //A sessão está no processo de desligamento, indicando que ela está sendo terminada ou desmontada.
        WTSInit             //A sessão está em processo de inicialização, preparando-se para ser usada ou para estabelecer uma conexão.
    }
}
