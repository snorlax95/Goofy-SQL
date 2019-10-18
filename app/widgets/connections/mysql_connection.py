import pymysql
from sshtunnel import SSHTunnelForwarder
from pymysql.cursors import DictCursor


class MySQL():
    def __init__(self):
        self.connection = None
        self.server = None
        self.selected_database = None
        self.selected_table = None
        self.selected_table_schema = None
        self.charset_collation = {}
        self.default_charset = None
        self.engines = []
        self.default_engine = None

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

    def get_database_options(self):
        cursor = self.connection.cursor(DictCursor)
        cursor.execute("SHOW CHARACTER SET")
        charsets = cursor.fetchall()
        cursor.execute("SHOW COLLATION")
        collations = cursor.fetchall()
        cursor.execute("SELECT default_character_set_name FROM information_schema.SCHEMATA")
        default_result = cursor.fetchone()
        if 'DEFAULT_CHARACTER_SET_NAME' in default_result:
            default_charset = default_result['DEFAULT_CHARACTER_SET_NAME']
        else:
            default_charset = default_result['default_character_set_name']
        
        cursor.execute("SHOW ENGINES")
        engines = cursor.fetchall()
        for engine in engines:
            if engine['Support'] != 'NO':
                self.engines.append(engine['Engine'])
            if engine['Support'] == 'DEFAULT':
                self.default_engine = engine['Engine']

        cursor.close()
        for charset in charsets:
            self.default_charset = default_charset
            self.charset_collation[charset['Charset']] = {"collations": [], "default": charset['Default collation']}
        for collation in collations:
            self.charset_collation[collation['Charset']]["collations"].append(collation['Collation'])
    
    def create_database(self, name, encoding, collation):
        cursor = self.connection.cursor(DictCursor)
        try:
            cursor.execute(f"CREATE DATABASE {name} CHARACTER SET {encoding} COLLATE {collation}")
            cursor.close()
            return True
        except Exception as e:
            return 'Got error {!r}, errno is {}'.format(e, e.args[0])

    def create_table(self, name, encoding, collation, engine):
        cursor = self.connection.cursor(DictCursor)
        cursor = self.use_database(self.selected_database, cursor)
        try:
            cursor.execute(f"CREATE TABLE {name} (id INT NOT NULL AUTO_INCREMENT, PRIMARY KEY (id)) \
                ENGINE={engine} CHARACTER SET {encoding} COLLATE {collation}")
            cursor.close()
            return True
        except Exception as e:
            return 'Got error {!r}, errno is {}'.format(e, e.args[0])

    def delete_table(self, name):
        cursor = self.connection.cursor(DictCursor)
        cursor = self.use_database(self.selected_database, cursor)
        try:
            cursor.execute(f"DROP TABLE IF EXISTS {name}")
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

    def get_table_schema(self, table=None):
        cursor = self.connection.cursor(DictCursor)
        if table is None:
            table = self.selected_table
        try:
            cursor.execute(f"DESCRIBE {table}")
            results = cursor.fetchall()
            cursor.close()
            self.selected_table_schema = results
            return results
        except Exception as e:
            cursor.close()
            return 'Got error {!r}, errno is {}'.format(e, e.args[0])

    def select_all(self, index, interval):
        select_query = f"SELECT * FROM {self.selected_table}  LIMIT {index}, {interval};"
        count_query = f"SELECT COUNT(*) as count FROM {self.selected_table};"
        self.connection.autocommit(True)
        cursor = self.connection.cursor(DictCursor)
        cursor = self.use_database(self.selected_database, cursor)
        try:
            cursor.execute(select_query)
            results = cursor.fetchall()
            cursor.execute(count_query)
            count = cursor.fetchone()['count']
            cursor.close()
            self.connection.autocommit(False)
            return {'results': results, 'count': count}
        except Exception as e:
            cursor.close()
            self.connection.autocommit(False)
            return 'Got error {!r}, errno is {}'.format(e, e.args[0])

    def convert_value(self, table, column, value):
        if table is None:
            table = self.selected_table
        if self.selected_table_schema is None:
            schema = self.get_table_schema(table)
        else:
            schema = self.selected_table_schema

        column_type = schema[column]['Type']
        if 'varchar' in column_type.lower():
            return str(value)
        if 'datetime' in column_type.lower():
            return value.toString('yyyy-MM-dd hh:mm:ss')
        if 'date' in column_type.lower():
            return value.toString('yyyy-MM-dd')


    def get_identifier_column(self, table):
        if table is None:
            table = self.selected_table
        if self.selected_table_schema is None:
            schema = self.get_table_schema(table)
        else:
            schema = self.selected_table_schema
        for idx, column in enumerate(schema):
            if 'PRI' in column['Key']:
                return {'column_name': column['Field'], 'column_index': idx}
            if 'UNI' in column['Key']:
                return {'column_name': column['Field'], 'column_index': idx}
        return False

    def update_query(self, table, column_index, column_value, row_index, cell_value, row_values):
        if table is None:
            table = self.selected_table

        converted_value = self.convert_value(table, column_index, cell_value)
        identifier_column = self.get_identifier_column(table)
        if identifier_column is False:
            # WHERE every single row value is checked, no key to rely on. LIMIT 1
            # WHERE column=value, column=value, column=value LIMIT 1
            update_query = f"UPDATE {table} SET {column_value}='{converted_value}' WHERE " \
                f"{identifier_column}={table} LIMIT 1"
        else:
            if isinstance(converted_value, str):
                update_query = f"UPDATE {table} SET {column_value}='{converted_value}' WHERE " \
                    f"{identifier_column['column_name']}={row_values[identifier_column['column_index']]}"
            else:
                update_query = f"UPDATE {table} SET {column_value}={converted_value} WHERE " \
                    f"{identifier_column['column_name']}={row_values[identifier_column['column_index']]}"

        print(update_query)
        cursor = self.connection.cursor(DictCursor)
        cursor = self.use_database(self.selected_database, cursor)
        try:
            affected_rows = cursor.execute(update_query)
            self.connection.commit()
            cursor.close()
            return affected_rows
        except Exception as e:
            cursor.close()
            return 'Got error {!r}, errno is {}'.format(e, e.args[0])
