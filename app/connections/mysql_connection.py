import pymysql
from pymysql.cursors import DictCursor


class MySQL():
    def __init__(self, connection):
        self.connection = connection
        self.cursor = self.connection.cursor(DictCursor)
        self.selected_database = None
        self.selected_table = None

    def __exit__(self):
        self.cursor.close()
        self.connection.close()

    def select_database(self, db_name):
        self.cursor.execute(f"USE `{db_name}`")
        self.selected_database = db_name
        self.selected_table = None

    def get_databases(self):
        self.cursor.execute("SHOW DATABASES")
        databases = self.cursor.fetchall()
        database_names = {
            "common": ['sys', 'information_schema', 'mysql', 'performance_schema'],
            "unique": []
        }
        for database in databases:
            if database['Database'] not in database_names['common']:
                database_names['unique'].append(database['Database'])
        return database_names

    def get_tables(self):
        self.cursor.execute("SHOW TABLES")
        tables = self.cursor.fetchall()
        table_names = []
        for table in tables:
            table_names.append(table[f'Tables_in_{self.selected_database}'])
        return table_names

    def custom_query(self, query):
        try:
            if query[:6] == 'SELECT':
                self.cursor.execute(query)
                result = self.cursor.fetchall()
            else:
                result = self.cursor.execute(query)
                self.connection.commit()
            return result
        except (pymysql.MySQLError, pymysql.Warning, pymysql.Error, pymysql.InterfaceError, pymysql.DatabaseError,
                pymysql.DataError,  pymysql.OperationalError, pymysql.IntegrityError, pymysql.InternalError,
                pymysql.ProgrammingError, pymysql.NotSupportedError) as e:
            return 'Got error {!r}, errno is {}'.format(e, e.args[0])
