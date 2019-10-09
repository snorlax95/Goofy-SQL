import pymysql
from pymysql.cursors import DictCursor


class MySQL():
    def __init__(self, connection):
        self.connection = connection
        self.selected_database = None
        self.selected_table = None

    def __exit__(self):
        self.connection.close()

    def create_database(self, name, encoding, collation):
        print('creating database')
        cursor = self.connection.cursor(DictCursor)
        try:
            cursor.execute(f"CREATE DATABASE {name} SET {encoding} COLLATE {collation}")
            cursor.close()
            return True
        except (pymysql.MySQLError, pymysql.Warning, pymysql.Error, pymysql.InterfaceError, pymysql.DatabaseError,
                pymysql.DataError, pymysql.OperationalError, pymysql.IntegrityError, pymysql.InternalError,
                pymysql.ProgrammingError, pymysql.NotSupportedError) as e:
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
        except (pymysql.MySQLError, pymysql.Warning, pymysql.Error, pymysql.InterfaceError, pymysql.DatabaseError,
                pymysql.DataError, pymysql.OperationalError, pymysql.IntegrityError, pymysql.InternalError,
                pymysql.ProgrammingError, pymysql.NotSupportedError) as e:
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
        except (pymysql.MySQLError, pymysql.Warning, pymysql.Error, pymysql.InterfaceError, pymysql.DatabaseError,
                pymysql.DataError,  pymysql.OperationalError, pymysql.IntegrityError, pymysql.InternalError,
                pymysql.ProgrammingError, pymysql.NotSupportedError) as e:
            cursor.close()
            return 'Got error {!r}, errno is {}'.format(e, e.args[0])
