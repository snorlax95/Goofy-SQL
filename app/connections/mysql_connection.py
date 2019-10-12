import pymysql
from sshtunnel import SSHTunnelForwarder
from pymysql.cursors import DictCursor


class MySQL():
    def __init__(self):
        self.connection = None
        self.server = None
        self.selected_database = None
        self.selected_table = None

    def connect_tcp(self, details):
        self.connection = pymysql.connect(host=details.host,
                                          user=details.username,
                                          password=details.password,
                                          port=details.port,
                                          database=details.database)
        return True

    def connect_ssh(self, details):
        host = details.host if details.host != details.ssh_host else '127.0.0.1'
        port = details.port if details.port is not None else 3306
        ssh_port = details.ssh_port if details.ssh_port is not None else 22

        self.server = SSHTunnelForwarder((details.ssh_host, ssh_port),
                                         ssh_password=details.ssh_password,
                                         ssh_username=details.ssh_user,
                                         remote_bind_address=(host, port))

        self.server.start()
        self.connection = pymysql.connect(host=host,
                                          user=details.username,
                                          password=details.password,
                                          port=self.server.local_bind_port,
                                          database=details.database)
        return True

    def create_database(self, name, encoding, collation):
        cursor = self.connection.cursor(DictCursor)
        try:
            cursor.execute(f"CREATE DATABASE {name} SET {encoding} COLLATE {collation}")
            cursor.close()
            return True
        except Exception as e:
            return 'Got error {!r}, errno is {}'.format(e, e.args[0])

    def select_database(self, db_name):
        cursor = self.connection.cursor(DictCursor)
        cursor = self.use_database(db_name, cursor)
        cursor.close()
        if isinstance(cursor, str):
            return False
        else:
            self.selected_database = db_name
            self.selected_table = None
            return True

    def use_database(self, db_name, cursor):
        try:
            cursor.execute(f"USE `{db_name}`")
            return cursor
        except Exception as e:
            return 'Got error {!r}, errno is {}'.format(e, e.args[0])

    def get_databases(self):
        cursor = self.connection.cursor(DictCursor)
        cursor.execute("SHOW DATABASES")
        databases = cursor.fetchall()
        database_names = {
            "common": ['sys', 'information_schema', 'mysql', 'performance_schema'],
            "unique": []
        }
        for database in databases:
            if database['Database'] not in database_names['common']:
                database_names['unique'].append(database['Database'])
        cursor.close()
        return database_names

    def get_tables(self):
        cursor = self.connection.cursor(DictCursor)
        cursor = self.use_database(self.selected_database, cursor)
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        table_names = []
        for table in tables:
            table_names.append(table[f'Tables_in_{self.selected_database}'])
        cursor.close()
        return table_names

    def get_table_schema(self, table):
        cursor = self.connection.cursor(DictCursor)
        cursor.execute(f"DESCRIBE {table}")
        schema = cursor.fetchall()
        cursor.close()
        return schema

    def custom_query(self, query):
        cursor = self.connection.cursor(DictCursor)
        cursor = self.use_database(self.selected_database, cursor)
        try:
            if query[:6] == 'SELECT' or query[:4] == 'SHOW':
                cursor.execute(query)
                result = cursor.fetchall()
            else:
                result = cursor.execute(query)
                self.connection.commit()
            cursor.close()
            return result
        except Exception as e:
            cursor.close()
            return 'Got error {!r}, errno is {}'.format(e, e.args[0])

    def update_query(self, table, column, value, identifier_column, identifier):
            if table is None:
                table = self.selected_table
            update_query = f"UPDATE {table} SET {column}={value} WHERE {identifier_column}={identifier}"
            cursor = self.connection.cursor(DictCursor)
            cursor = self.use_database(self.selected_database, cursor)
            try:
                affected_rows = cursor.execute(update_query)
                cursor.commit()
                cursor.close()
                return affected_rows
            except Exception as e:
                cursor.close()
                return 'Got error {!r}, errno is {}'.format(e, e.args[0])
