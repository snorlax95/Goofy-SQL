class MySQL():
    def __init__(self, connection):
        self.connection = connection
        self.cursor = self.connection.cursor()

    def select_database(self, db_name):
        self.cursor.execute(f"USE `{db_name}`")

    def get_databases(self):
        databases = ("SHOW DATABASES")
        self.cursor.execute(databases)
        database_names = {
            "common": ['sys', 'information_schema', 'mysql', 'performance_schema'],
            "unique": []
        }
        for (databases) in self.cursor:
            if databases[0] not in database_names['common']:
                database_names['unique'].append(databases[0])
        return database_names

    def get_tables(self):
        tables = ("SHOW TABLES")
        self.cursor.execute(tables)
        table_names = []
        for (tables) in self.cursor:
            table_names.append(tables[0])
        return table_names
