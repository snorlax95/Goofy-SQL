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
        else:
            self.name = saved_connection['name']
            self.host = saved_connection['host']
            self.username = saved_connection['username']
            self.password = saved_connection['password']
            self.database = saved_connection['database']
            self.port = saved_connection['port']
            self.connection_type = saved_connection['connection_type']

    def get_details_dict(self):
        return {}