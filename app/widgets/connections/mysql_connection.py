import pymysql
import copy
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
        try:
            cursor = self.get_cursor(db_name=self.selected_database)
            cursor.execute(f"CREATE TABLE {name} (id INT NOT NULL AUTO_INCREMENT, PRIMARY KEY (id)) \
                ENGINE={engine} CHARACTER SET {encoding} COLLATE {collation}")
            cursor.close()
            return True
        except Exception as e:
            return 'Got error {!r}, errno is {}'.format(e, e.args[0])

    def delete_table(self, name):
        try:
            cursor = self.get_cursor(db_name=self.selected_database)
            cursor.execute(f"DROP TABLE IF EXISTS {name}")
            cursor.close()
            return True
        except Exception as e:
            return 'Got error {!r}, errno is {}'.format(e, e.args[0])

    def select_database(self, db_name):
        cursor = self.get_cursor(db_name=db_name)
        cursor.close()
        if isinstance(cursor, str):
            return False
        else:
            self.selected_database = db_name
            self.selected_table = None
            return True

    def get_cursor(self, db_name=None):
        cursor = self.connection.cursor(DictCursor)
        if db_name is not None:
            cursor.execute(f"USE `{db_name}`")
        return cursor

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
        cursor = self.get_cursor(db_name=self.selected_database)
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        table_names = []
        for table in tables:
            table_names.append(table[f'Tables_in_{self.selected_database}'])
        cursor.close()
        return table_names

    def custom_query(self, query):
        try:
            cursor = self.get_cursor(db_name=self.selected_database)
            if query[:6] == 'SELECT' or query[:4] == 'SHOW':
                cursor.execute(query)
                result = cursor.fetchall()
            else:
                result = cursor.execute(query)
                self.connection.commit()
            cursor.close()
            return result
        except Exception as e:
            return 'Got error {!r}, errno is {}'.format(e, e.args[0])

    def get_table_schema(self, table=None):
        if table is None:
            table = self.selected_table
        try:
            cursor = self.get_cursor(db_name=self.selected_database)
            cursor.execute(f"DESCRIBE {table}")
            results = cursor.fetchall()
            cursor.close()
            self.selected_table_schema = results
            return results
        except Exception as e:
            return 'Got error {!r}, errno is {}'.format(e, e.args[0])

    def get_standardized_schema(self, table, schema):
        simple_types = {"VARCHAR": "string", "LONGTEXT": "string", "INT": "number", "BIGINT": "number",
        "SMALLINT": "number", "FLOAT": "number", "DATETIME": "date", "DATE": "date"}
        if table is None:
            table = self.selected_table
        if schema is None:
            schema = self.get_table_schema(table)
            
        columns = {'columns': {}, 'indexes': {}}
        for idx, column in enumerate(schema):
            new_column = {'Type': None, 'Null': False, 'Unsigned': False, 'Zerofill': False,
                          'Binary': False, 'Key': None, 'Default': None, 'Extra': None, 
                          'Simple_Type': None, 'encoding': None, 'collation': None}

            if column['Null'] == 'YES':
                new_column['Null'] = True
            if 'UNSIGNED' in column['Type'].upper():
                column['Type'] = column['Type'].upper().replace(' UNSIGNED', '', 1)
                new_column['Unsigned'] = True
            if 'ZEROFILL' in column['Type'].upper():
                column['Type'] = column['Type'].upper().replace(' ZEROFILL', '', 1)
                new_column['Zerofill'] = True

            start_index = column['Type'].find('(')
            if start_index != -1:
                simple_type = copy.copy(column['Type'])[0:start_index].upper()
            else:
                simple_type = copy.copy(column['Type']).upper()
            if simple_type in simple_types:
                new_column['Simple_Type'] = simple_types[simple_type]

            new_column['Type'] = column['Type'].upper()
            new_column['Key'] = column['Key'].upper() if column['Key'] is not None else None
            new_column['Default'] = column['Default'] if column['Default'] is not None else None
            new_column['Extra'] = column['Extra'].upper() if column['Extra'] is not None else None
           
            columns['columns'][column['Field']] = new_column
            columns['indexes'][column['Field']] = idx
        return columns

    def select_all(self, index, interval):
        select_query = f"SELECT * FROM {self.selected_table}  LIMIT {index}, {interval};"
        count_query = f"SELECT COUNT(*) as count FROM {self.selected_table};"
        self.connection.autocommit(True)
        try:
            cursor = self.get_cursor(db_name=self.selected_database)
            cursor.execute(select_query)
            results = cursor.fetchall()
            cursor.execute(count_query)
            count = cursor.fetchone()['count']
            cursor.close()
            self.connection.autocommit(False)
            return {'results': results, 'count': count}
        except Exception as e:
            self.connection.autocommit(False)
            return 'Got error {!r}, errno is {}'.format(e, e.args[0])

    def convert_value(self, table, column_index, value):
        if table is None:
            table = self.selected_table
        if self.selected_table_schema is None:
            schema = self.get_table_schema(table)
        else:
            schema = self.selected_table_schema

        column_type = schema[column_index]['Type']
        if 'varchar' in column_type.lower():
            return str(value)
        if 'datetime' in column_type.lower():
            return value.toString('yyyy-MM-dd hh:mm:ss')
        if 'date' in column_type.lower():
            return value.toString('yyyy-MM-dd')

    def column_type(self, table, column):
        if table is None:
            table = self.selected_table
        if self.selected_table_schema is None:
            schema = self.get_table_schema(table)
        else:
            schema = self.selected_table_schema

        column_type = None
        for table_column in schema:
            if table_column['Field'] == column:
                column_type = table_column['Type']
                break

        if table_column is None:
            return None

        if 'varchar' in column_type.lower():
            return 'string'
        elif 'datetime' in column_type.lower():
            return 'datetime'
        elif 'date' in column_type.lower():
            return 'date'
        elif 'json' in column_type.lower():
            return 'json'

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

    def drop_table_column(self, table, column_name):
        if table is None:
            table = self.selected_table

        query = f"ALTER TABLE `{table}` DROP `{column_name}`"
        print(query)
        try:
            cursor = self.get_cursor(db_name=self.selected_database)
            result = cursor.execute(query)
            self.connection.commit()
            cursor.close()
            return result
        except Exception as e:
            return 'Got error {!r}, errno is {}'.format(e, e.args[0])

    def modify_table_column(self, table, values, simple_type):
        # CHARACTER SET {char_set}
        # COLLATION {collation}
        # Figure out Binary
        if table is None:
            table = self.selected_table

        if values['Default'] is None or values['Default'] == '':
            default = ""
        else:
            if simple_type == "number":
                default = f"DEFAULT {values['Default']} "
            else:
                default = f"DEFAULT '{values['Default']}' "
                
        query = f"ALTER TABLE `{table}` MODIFY " \
            f"{values['Field']} {values['Type']} " \
            f"{'UNSIGNED ' if values['Unsigned'] else ''}" \
            f"{'ZEROFILL ' if values['Zerofill'] else ''}" \
            f"{'NULL ' if values['Allow Null'] else 'NOT NULL '}" \
            f"{values['Extra'] if values['Extra'] is not None else ''}" \
            f"{default}"
        print(query)

        try:
            cursor = self.get_cursor(db_name=self.selected_database)
            affected_rows = cursor.execute(query)
            self.connection.commit()
            cursor.close()
            return affected_rows
        except Exception as e:
            return 'Got error {!r}, errno is {}'.format(e, e.args[0])

    def modify_table_key(self, table, columns, index_type, name):
        if index_type == 'primary':
            query = f"ALTER TABLE `{table}` DROP PRIMARY KEY, ADD PRIMARY KEY({columns})"
        else:
            query = f"CREATE {type} INDEX ({name}) ON {table}({columns})"
        print(query)

    def update_query(self, table, column_index, column_value, row_index, cell_value, row_values):
        if table is None:
            table = self.selected_table

        converted_value = self.convert_value(table, column_index, cell_value)
        identifier_column = self.get_identifier_column(table)
        if identifier_column is False:
            # WHERE every single row value is checked, no key to rely on. LIMIT 1
            # WHERE column=value, column=value, column=value LIMIT 1
            update_query = f"UPDATE `{table}` SET {column_value}='{converted_value}' WHERE " \
                f"{identifier_column}=`{table}` LIMIT 1"
        else:
            if isinstance(converted_value, str):
                update_query = f"UPDATE `{table}` SET {column_value}='{converted_value}' WHERE " \
                    f"{identifier_column['column_name']}={row_values[identifier_column['column_index']]}"
            else:
                update_query = f"UPDATE `{table}` SET {column_value}={converted_value} WHERE " \
                    f"{identifier_column['column_name']}={row_values[identifier_column['column_index']]}"

        print(update_query)
        try:
            cursor = self.get_cursor(db_name=self.selected_database)
            affected_rows = cursor.execute(update_query)
            self.connection.commit()
            cursor.close()
            return affected_rows
        except Exception as e:
            cursor.close()
            return 'Got error {!r}, errno is {}'.format(e, e.args[0])
