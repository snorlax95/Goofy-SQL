import pymysql
from sshtunnel import SSHTunnelForwarder
from pymysql.cursors import DictCursor


class MySQL():
    def __init__(self):
        self.connection = None
        self.server = None
        self.selected_database = None
        self.selected_table = None
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

    def get_table_schema(self, table):
        cursor = self.connection.cursor(DictCursor)
        if table is None:
            table = self.selected_table
        try:
            cursor.execute(f"DESCRIBE {table}")
            results = cursor.fetchall()
            cursor.close()
            return results
        except Exception as e:
            cursor.close()
            return 'Got error {!r}, errno is {}'.format(e, e.args[0])

    def get_standardized_schema(self, table, schema):
        if table is None:
            table = self.selected_table
        if schema is None:
            schema = self.get_table_schema(table)
            
        columns = {'columns': {}, 'indexes': {}}
        for idx, column in enumerate(schema):
            new_column = {'Type': None, 'Null': False, 'Unsigned': False, 'Zerofill': False,
                'Binary': False, 'Key': None, 'default': None, 'extra': None, 'encoding': None, 'collation': None}

            new_column['Type'] = column['Type']
            if column['Null'] == 'YES':
                new_column['Null'] = True
            if 'unsigned' in column['Type'].lower():
                new_column['Unsigned'] = True
            if 'zerofill' in column['Type'].lower():
                new_column['Zerofill'] = True
            new_column['Key'] = column['Key']
            new_column['Default'] = column['Default']
            new_column['Extra'] = column['Extra']
           
            columns['columns'][column['Field']] = new_column
            columns['indexes'][column['Field']] = idx
        return columns

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

    def convert_value(self, schema, column, value):
        column_type = schema['types'][column]
        if column_type == 'string':
            return str(value)
        if column_type == 'datetime':
            return value.toString('yyyy-MM-dd hh:mm:ss')
        if column_type == 'date':
            return value.toString('yyyy-MM-dd')
        if column_type == 'number':
            return value

    def get_simplified_schema(self, table, schema):
        if table is None:
            table = self.selected_table
        if schema is None:
            schema = self.get_table_schema(table)
            

        columns = {'types': {}, 'keys': {}, 'columns': [], 'indexes': {}}
        for idx, column in enumerate(schema):
            column_key = None
            if 'PRI' in column['Key']:
                column_key = 'primary'
            elif 'UNI' in column['Key']:
                column_key = 'unique'
            columns['keys'][column['Field']] = column_key

            column_type = 'str'
            if 'varchar' in column['Type'].lower():
                column_type = 'string'
            elif 'datetime' in column['Type'].lower():
                column_type = 'datetime'
            elif 'date' in column['Type'].lower():
                column_type = 'date'
            elif 'json' in column['Type'].lower():
                column_type = 'json'
            elif 'int' in column['Type'].lower():
                column_type = 'number'
            columns['types'][column['Field']] = column_type
            columns['columns'].append(column)
            columns['indexes'][column['Field']] = idx
        return columns

    def update_query(self, table, schema, column_index, column_value, row_index, cell_value, row_values):
        if table is None:
            table = self.selected_table

        converted_value = self.convert_value(schema, column_value, cell_value)
        identifier_column = None
        identifier_type = None
        for key, val in schema['keys'].items():
            if (val == 'primary' or val == 'unique') and identifier_type != 'primary':
                identifier_type = val
                identifier_column = key

        if isinstance(converted_value, str):
            set_clause = f"SET {column_value}='{converted_value}'"
        else:
            set_clause = f"SET {column_value}={converted_value}"

        if identifier_column is None:
            where_clause = "WHERE LIMIT 1"
        else:
            identifier_column_value = self.convert_value(schema, identifier_column, row_values[column_index])
            column_index = schema['indexes'][identifier_column]
            where_clause = f"WHERE {identifier_column}={identifier_column_value}"
        
        update_query = f"UPDATE {table} {set_clause} {where_clause}"
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
