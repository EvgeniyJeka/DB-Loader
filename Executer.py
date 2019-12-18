import pymysql


hst = '127.0.0.1'
usr = 'root'
pwd = '7417418@a'
db_name = 'mysql'

# Add ID that would be added automatically on insertion.

class Executer(object):

    """
    This class contains all CRUD methods.
    The methods can be used via class instance.

    The method 'connect_me' is used to create a cursor, that can
    be passed to other method that require cursor.

    """


    def __init__(self):
        self.cursor = self.connect_me(hst, usr, pwd, db_name)

    # Connect to DB
    def connect_me(self, hst, usr, pwd, db_name):

        try:
            conn = pymysql.connect(host=hst, user=usr, password=pwd, db=db_name, autocommit='True')
            cursor = conn.cursor()

        # Wrong Credentials error
        except pymysql.err.OperationalError:
            print("Wrong Credentials or Host")

        # Wrong DB name error
        except pymysql.err.InternalError:
            print("Unknown Database")

        return cursor

    def create_fill_table(self, file_name, column_names, table_data):

        cursor = self.cursor

        cursor.execute('show tables')
        tups = cursor.fetchall()

        tables = [tup[0] for tup in tups]

        # Creating new table to store the file content if required.
        if file_name not in tables:
            print(f"Logs: {file_name} table is missing! Creating the {file_name} table")

            added_columns = " varchar(255),".join(column_names)
            query = f"CREATE TABLE {file_name} ({added_columns} "+"varchar(255)"+");"
            print(f"Log: Executing query |{query}|")
            cursor.execute(query)

        else:
            print(f"Logs: {file_name} - table with such name already exists.")

        print(f"Log: Table data - {table_data}")

        # Filling the table
        for row in table_data:
            inserted_values = "', '".join(row)
            query = f"insert into {file_name} values ('{inserted_values}');"
            print(query)
            cursor.execute(query)

        return {"response":"DB was successfully updated"}

    # Get Table Column Names
    def get_columns(self, table):
        cursor = self.cursor
        query = 'show columns from ''%s'';' % table
        cursor.execute(query)
        columns = cursor.fetchall()
        result = []

        for cl in columns:
            result.append(cl[0])

        return result

    # Get table content from DB
    def get_table_content(self, table):
        cursor = self.cursor
        query = f'select * from {table};'
        cursor.execute(query)
        result = cursor.fetchall()
        return result







# if __name__ == "__main__":
#     executer = Executer()
#     lls = ["apple","bannana"]
#     executer.create_validate_tables("arkan",lls)


