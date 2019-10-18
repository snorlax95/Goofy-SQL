class ConnectionModel:
    def __init__(self, saved_connection):
        if saved_connection is None:
            self.name = None
            self.host = None
            self.username = None
            self.password = None
            self.database = None
            self.port = None
            self.connection_type = None
            self.ssh_host = None
            self.ssh_user = None
            self.ssh_password = None
            self.ssh_port = None
        else:
            self.name = saved_connection['name']
            self.host = saved_connection['host']
            self.username = saved_connection['username']
            self.password = saved_connection['password']
            self.database = saved_connection['database']
            self.port = saved_connection['port']
            self.connection_type = saved_connection['connection_type']
            self.ssh_host = saved_connection['ssh_host']
            self.ssh_user = saved_connection['ssh_user']
            self.ssh_password = saved_connection['ssh_password']
            self.ssh_port = saved_connection['ssh_port']

    def get_details_dict(self):
        return {
            'name': self.name,
            'host': self.host,
            'username': self.username,
            'password': self.password,
            'database': self.database,
            'port': self.port,
            'connection_type': self.connection_type,
            'ssh_host': self.ssh_host,
            'ssh_user': self.ssh_user,
            'ssh_password': self.ssh_password,
            'ssh_port': self.ssh_port
        }
