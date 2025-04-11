from src.models.models import Sessions, Client, StandardWorkHours
from src.connections.database_manager import DatabaseManager
from src.services.working_hours_service import WorkingHoursService
from src.services.rabbitmq_session_audit_producer import RabbitMQSessionAuditProducer
from src.logs.logger import Logger
from src.config import config
from sqlalchemy.inspection import inspect
import datetime, json
import re

class MessageProcessor:

    def __init__(self):
        self.logger = Logger(log_name='WSM-Router').get_logger()
        self.dm = DatabaseManager()
        self.work_hours = WorkingHoursService()
        self.send_audit = RabbitMQSessionAuditProducer()


    def process_client_message(self, ZMQ_client_id, client_message):
        try:
            #heartbeat_data = json.loads(client_message)
            client_data = client_message.get("Heartbeat")
            if client_data:
                client_data = json.loads(client_data)
            else:
                client_data = {}
        except json.JSONDecodeError as e:
            message = {"status": "error", "message": f"Error decoding JSON: {str(e)}"}
            self.logger.error(message)
            return message

        try:
            client = Client(
                hostname = client_data.get("hostname"),
                ip_address = client_data.get("ip_address"),
                client_version = client_data.get("client_version"),
                os_name = client_data.get("os_name"),
                os_version = client_data.get("os_version"),
                agent_info = client_data.get("agent_info"),
                uptime = client_data.get("uptime"),
                create_timestamp = client_data.get("create_timestamp"),
                update_timestamp = client_data.get("update_timestamp")
                )
            
            existing_client = self.dm.get_by_hostname(Client,client_data.get("hostname"))          
            if existing_client:
                #SqlAlchemy obj to dict()
                client = {c.key: getattr(client, c.key) for c in inspect(client).mapper.column_attrs}
                client.update({"create_timestamp": existing_client.create_timestamp})
                client.update({"update_timestamp": datetime.datetime.now(datetime.timezone.utc)})
                self.dm.update_entry(Client,existing_client.hostname,client)
                return {"status": "beating", "message": "Done"}
            else:
                self.dm.add_entry(client)     
            self.logger.info(f"WSM Router - message_processor - Processing Client: Hostname={client_data.get("hostname")}, IP={client_data.get("ip_address")},"
              f"Version={client_data.get("client_version")}, OS={client_data.get("os_name")} {client_data.get("os_version")}, Agent={client_data.get("agent_info")}")
            # return confirmation
            message = {"status": "success", "message": "Client information processed"}
            self.logger.info(message)
            return message
        except KeyError as e:
            # return this error when the key in the json is not found
            message = {"status": "error", "message": f"Missing key in client data: {str(e)}"}
            self.logger.error(message)
            return message
        except Exception as e:
            # capture other errors
            message = {"status": "error", "message": f"An error occurred while processing client data: {str(e)}"}
            self.logger.error(message)
            return message

        
    def process_session_message(self, ZMQ_client_id, session_data):
        """
            Process messages of "Session" type.
        """
        try:
            # Verify if hostname exists into Client table
            hostname_exists = self.dm.get_by_hostname(Client,session_data["hostname"])
            if not hostname_exists:
                error_message = "Error: hostname not available in the database."
                self.logger.error(error_message)
                return {"status":"error", "message": error_message}

            #Verify if the user is allowed to login this time
            working_hours_service = WorkingHoursService()
            is_allowed_ = working_hours_service.check_valid_session(session_data["user"])
            if not is_allowed_:
                error_message = f"User {session_data['user']} is not allowed to login at this time."
                self.logger.error(error_message)
                return {"status": "error", "message": error_message}
            
            # Create a session json with received data
            session = Sessions(
                    hostname = session_data.get("hostname"),
                    event_type=session_data.get("event_type"),
                    start_time=session_data.get("start_time"),
                    end_time=session_data.get("end_time"),
                    user=session_data.get("user"),
                    status=session_data.get("status")
                )

            # Check if the session already exists
            existing_session = self.dm.get_by_hostname_and_user(Sessions, session.hostname, session.user)
            if existing_session:
                # Convert the session object to dict and update session data
                    session_dict = {c.key: getattr(session, c.key) for c in inspect(session).mapper.column_attrs}
                    session_dict.update({
                        "update_timestamp": datetime.datetime.now(datetime.timezone.utc),
                        "create_timestamp": existing_session.create_timestamp
                    })
                    try:
                        self.dm.update_by_hostname_and_user(Sessions, session.hostname, session.user, session_dict)
                        message = (f"Processing Session: Hostname={session_dict['hostname']}, User={session_dict['user']}, "
                            f"Start={session_dict['start_time']}, End={session_dict['end_time']}, Status={session_dict['status']}")
                        self.logger.info(message)
                        message = {"status": "success", "message": f"Session information updated: Hostname={session_dict['hostname']}, User = {session_dict['user']}"}
                        return message
                    except Exception as e:
                        message = {"status": "error", "message": f"Error updating existing session: {e}"}
                        self.logger.error(message)
                        return  {"status": "error", "message": f"Error updating existing session: {e}"}
            else:
                try:
                    self.dm.add_entry(session)
                    message = (f"Processing New Session: Hostname={session.hostname}, User={session.user}, "
                        f"Start={session.start_time}, End={session.end_time}, Status={session.status}")
                    self.logger.info(message)
                    return {"status": "success", "message": f"New session added: Hostname={session.hostname}, User={session.user}"}
                except Exception as e:
                    self.logger.error(f"Error adding new session: {e}")
                    return {"status": "error", "message": f"Error adding new session: {e}"}
        except Exception as e:
            self.logger.error(f"WSM - process_session_message - Error processing session message: {e}")
            return {"status": "error", "message": f"Error processing session message: {e}"}  
        

    def process_user_disconnection(self, disconnection_data):
        try:
            hostname = disconnection_data["DisconnectionRequest"].get("hostname")
            user = disconnection_data["DisconnectionRequest"].get("user")
            dc_datetime = disconnection_data["DisconnectionRequest"].get("dc_datetime")
            
            if not hostname or not user or not dc_datetime:
                self.logger.error("WSM - process_user_disconnection - Invalid disconnection request data: missing hostname or user")
                return {"status": "error", "message": "Invalid disconnection request data"}
            else:
                message_data = {
                    "message_type":"logoff",
                    "hostname": hostname,
                    "user": user,
                    "dc_datetime": dc_datetime
                }
                return message_data
        except KeyError as e:
            self.logger.error(f"WSM - process_user_disconnection - Missing key in disconnection request data: {str(e)}")
            return {"status": "error", "message": "Invalid disconnection request format"}
        except Exception as e:
            self.logger.error(f"WSM - process_user_disconnection - General error in process_user_disconnection: {str(e)}")
            return {"status": "error", "message": "Failed to process disconnection request"}


    #Delete user from Sessions table when the disconnection was processed
    def process_user_already_disconnected(self,disconnected_data):
        disconnected_data = json.loads(disconnected_data["SessionDisconnected"])
        try:
            hostname = disconnected_data["hostname"]
            user = disconnected_data["user"]
            if not hostname or not user:
                self.logger.error("Invalid disconnection request data: missing hostname or user")
                return {"status": "error", "message": "Invalid disconnection request data"}
            else:
                try:
                    session_to_audit = self.dm.get_by_hostname_and_user(Sessions,hostname,user)
                    session_to_audit = self.to_dict(session_to_audit)
                    

                    self.sent_to_session_audit(action_type="end",session_data=session_to_audit)#Sent do function to preprare to sent do audit_database, when user ENDS to use
                    self.dm.delete_user_disconnected(Sessions,hostname,user) #remove from session_db

                    return {"status": "success", "message": "Disconnected user removed from database."}
                except KeyError as e:
                    self.logger.error(f"WSM Router - process_user_already_disconnected - Missing key in disconnection request data: {str(e)}")
                    return {"status": "error", "message": "Invalid disconnection request format"}
                except Exception as e:
                    self.logger.error(f"WSM Router - process_user_already_disconnected - General error in process_user_disconnection: {str(e)}")
                    return {"status": "error", "message": "Failed to process disconnection request"}  
        except KeyError as e:
            self.logger.error(f"WSM Router - process_user_already_disconnected - Missing key in disconnection request data: {str(e)}")
            return {"status": "error", "message": "Invalid disconnection request format"}
        except Exception as e:
            self.logger.error(f"WSM Router - process_user_already_disconnected - General error in process_user_disconnection: {str(e)}")
            return {"status": "error", "message": "Failed to process disconnection request"}
        
    # transform sqlAlchemy instance to dict
    def to_dict(self,instance):
        if instance is None:
            return None
        return {column.name: getattr(instance, column.name) for column in instance.__table__.columns}


    def process_connected_user(self,message_data):
        message_data = message_data["LogonRequest"]
        message_data = json.loads(message_data)
        try:
            hostname = message_data["hostname"]
            user = message_data["user"]
            status = message_data["status"]
            logon_time = message_data["logonTime"]
            logoff_time = message_data["logoffTime"]
            timestamp = message_data["timestamp"]
            action = "updateHours" #can be interact,lock, logoff, notify, ping, updateHours in this case for msg that comes to server to update user workhours
            timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
            timezone = str(datetime.datetime.now().astimezone().tzinfo)
            allowed_schedule = None
            message= None
            title = "Notification"
            options = "yes_no"
            try:
                account = self.dm.get_by_uid(StandardWorkHours, user)
                if account:
                    unrestricted = account.unrestricted
                    enable = account.enable
                    allowed_schedule = self.work_hours.get_allowed_schedule(user)
                    session_data = {
                        "hostname": hostname,
                        "event_type": "logon",
                        "user": user,
                        "status": "active",
                        "start_time": logon_time,
                        "end_time": None,
                    }
                    self.add_new_session(session_data) #Send start session to session table

                    self.sent_to_session_audit(action_type="start", session_data=session_data) #Sent do function to preprare to sent do audit_database, when user STARTS to use
                    user_json = {"action": action, "hostname": hostname, "user": user, "timezone": timezone,"unrestricted": unrestricted,"enable": enable, "allowed_schedule": allowed_schedule,"timestamp": timestamp,"message":message,"title":title,"options":options}
                    return user_json
                else:
                    self.logger.error(f"WSM Router - message_processor -  Error when trying to find user:{user}")
                    not_allowed_user = {"action": "logoff", "hostname": hostname, "user": user, "timezone": timezone, "unrestricted": False, "enable": False, "allowed_schedule": None, "timestamp" : timestamp, "message": "User cant be found on the database", "title": title, "options": None }
                    return not_allowed_user
            except Exception as e:
                self.logger.error(f"WSM Router - message_processor - Error when trying to set schedule for this uid:{user}")
                return{"status": "error", "message": f"No schedule for user {user}"}
        except Exception as e :
            self.logger.error(f"WSM Router - message_processor - Missing key in user connection data: {str(e)}")
            return {"status": "error", "message": "Invalid logon format request"}
        return

    def sent_to_session_audit(self,action_type,session_data):
        
        try:
            hostname = session_data.get("hostname")
            related_client = self.dm.get_by_hostname(model=Client,hostname=hostname)
            
            if related_client:
                related_client = self.to_dict(related_client)
            else:
                raise ValueError(f"Client not found for hostname: {hostname}")
            
            end_time = None
            if action_type == "end":
                end_time = datetime.datetime.now(datetime.timezone.utc)
            else:
                end_time = session_data.get("end_time")
            start_time = session_data.get("start_time") if session_data.get("start_time") else None
            if isinstance(start_time, datetime.datetime):
                start_time = start_time.isoformat()
            data = {
                "hostname":hostname,
                "event_type":"logout" if action_type == "end" else "logon",
                "login":session_data.get("user"),
                "status":session_data.get("status") if action_type =="start" else "disconnected",
                "start_time":start_time,
                "end_time":end_time.isoformat() if end_time else None,
                "os_version":related_client.get("os_version"),
                "os_name":related_client.get("os_name"),
                "ip_address":related_client.get("ip_address"),
                "client_version":related_client.get("client_version"),
                "agent_info":related_client.get("agent_info")
            }

            self.send_audit.send_message(table="SessionsAudit", data=data)

        except KeyError as e:
            self.logger.error(f"Missing required field in data: {e}")
        except ValueError as e:
            self.logger.error(f"Validation error: {e}")
        except AttributeError as e:
            self.logger.error(f"Unexpected attribute issue: {e}")
        except Exception as e:
            self.logger.error(f"An unexpected error occurred: {e}")
 
    def process_direct_message(self,message_data,hostname):
        try:
            message_data = message_data.get("RoutingClientMessage",{})

            user = message_data.get("user")
            title = message_data.get("title")
            message = message_data.get("message")
            action = message_data.get("action")
            timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
            timezone = str(datetime.datetime.now().astimezone().tzinfo)
            unrestricted = False
            enable = False
            allowed_schedule = None
            options = "yes_no"
            user_json = {"action": action, "hostname": hostname, "user": user, "timezone": timezone, "unrestricted": unrestricted,"enable": enable, "allowed_schedule": allowed_schedule,"timestamp": timestamp,"message":message,"title":title,"options":options}
            return(hostname, user_json)
        except Exception as e:
            self.logger.error(f"WSM Router: Error when trying to send message for this uid:{user}")
            return{"status": "error", "message": f"No schedule for user {user}"}   


    def process_wsm_agent_updater_message(self, message_data, hostname):
        try:
            user = message_data["RoutingClientMessage"]["uid"]
            start_time =message_data["RoutingClientMessage"]["start_time"]
            end_time = message_data["RoutingClientMessage"]["end_time"]
            uf = message_data["RoutingClientMessage"]["uf"]
            enable =message_data["RoutingClientMessage"]["enable"]
            st = message_data["RoutingClientMessage"]["st"]
            c = message_data["RoutingClientMessage"]["c"]
            weekdays = message_data["RoutingClientMessage"]["weekdays"]
            session_termination_action = message_data["RoutingClientMessage"]["session_termination_action"]
            cn = message_data["RoutingClientMessage"]["cn"]
            l = message_data["RoutingClientMessage"]["l"]
            enable = message_data["RoutingClientMessage"]["enable"]
            unrestricted = message_data["RoutingClientMessage"]["unrestricted"]
            deactivation_date = message_data["RoutingClientMessage"]["deactivation_date"]
            allowed_schedule:str = message_data["RoutingClientMessage"]["allowed_work_hours"]
            allowed_schedule = allowed_schedule.lower()
            allowed_schedule = json.loads(allowed_schedule)
            # Variables to set client json
            action = "updateHours" #can be interact,lock, logoff, notify, ping, updateHours in this case for msg that comes to server to update user workhours
            timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
            timezone = str(datetime.datetime.now().astimezone().tzinfo)
            message= None
            title = "Notification"
            options = "yes_no"
            try:
                try:
                    user_json = {"action": action, "hostname": hostname, "user": user, "timezone": timezone, "unrestricted": unrestricted,"enable": enable, "allowed_schedule": allowed_schedule,"timestamp": timestamp,"message":message,"title":title,"options":options}
                    return hostname,user_json
                except Exception as e:
                    self.logger.error(f"WSM Router: No hostname find for this uid {user}")
                    return {"status": "error", "message": f"No allowed schedule are set for {user}"}     
            except Exception as e:
                self.logger.error(f"WSM Router: No hostname find for this uid {user}")
                return {"status": "error", "message": f"No hostname find for this user {user}"}
        except Exception as e :
            self.logger.error(f"WSM Router - message_processor - Missing key in WSM Agent Updater data: {str(e)}")
            return {"status": "error", "message": "Invalid logon format request"}

    def add_new_session(self, session_data):
        try:
            new_session = Sessions(
                hostname=session_data["hostname"],
                event_type=session_data["event_type"],
                user=session_data["user"],
                status=session_data["status"],
                start_time=session_data["start_time"],
                end_time=session_data["end_time"]
            )
            self.dm.add_entry(new_session)
        except Exception as e:
            self.logger.error(f"WSM Router - message_processor - Missing key in add_new_session data: {str(e)}")
        

    def process_lock_or_unlock_user(self, message_data):
        return