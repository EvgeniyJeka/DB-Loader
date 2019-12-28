import pymysql
import configparser

# hst = '127.0.0.1'
# usr = 'root'
# pwd = '7417418@a'
# db_name = 'mysql'

# Reading DB name, host and credentials from config
# config = configparser.ConfigParser()
# config.read("./config.ini")
# hst = config.get("SQL_DB","host")
# usr = config.get("SQL_DB","user")
# pwd = config.get("SQL_DB","password")
# db_name = config.get("SQL_DB","db_name")


# Add ID that would be added automatically on insertion.

class Executer(object):
    """
    This class contains all CRUD methods.
    The methods can be used via class instance.

    The method 'connect_me' is used to create a cursor, that can
    be passed to other method that require cursor.

    """

    def __init__(self,config_file_path):

        # # Reading DB name, host and credentials from config
        config = configparser.ConfigParser()
        config.read(config_file_path)
        hst = config.get("SQL_DB","host")
        usr = config.get("SQL_DB","user")
        pwd = config.get("SQL_DB","password")
        db_name = config.get("SQL_DB","db_name")

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

    def create_fill_table(self, file_name, column_names, table_data, action_type):
        """
        This method is used to handle several scenarios:
        1. New table needs to be created - action type "create".
        2. An existing table should be overwritten - the table is removed an new table is created from scratch with
        the same name - action type "overwrite_1".
        3. New rows or columns are added to an existing table. Current data saved in the table isn't modified - action
        type "add_data".

        :param file_name: table name.
        :param column_names: table column names.
        :param table_data: table content (list of lists)
        :param action_type: supported action type, string - "create", "overwrite_1" or "add_data".
        :return: success message on success, error message on error - JSON.
        """
        cursor = self.cursor

        # Upload a new table with the name of an existing table
        if action_type == "overwrite":

            cursor.execute('show tables')
            tups = cursor.fetchall()

            tables = [tup[0] for tup in tups]

            if file_name in tables:
                cursor.execute(f"drop table {file_name}")

            added_columns = " varchar(255),".join(column_names)
            query = f"CREATE TABLE {file_name} ({added_columns} " + "varchar(255)" + ");"
            print(f"Log: Executing query |{query}|")
            cursor.execute(query)

        # Create a new table
        elif action_type == "create":
            cursor.execute('show tables')
            tups = cursor.fetchall()

            tables = [tup[0] for tup in tups]

            # Creating new table to store the file content if not exist.
            if file_name not in tables:
                print(f"Logs: {file_name} table is missing! Creating the {file_name} table")

                added_columns = " varchar(255),".join(column_names)
                query = f"CREATE TABLE {file_name} ({added_columns} " + "varchar(255)" + ");"
                print(f"Log: Executing query |{query}|")

                # Handling invalid input if provided.
                try:
                    cursor.execute(query)
                except pymysql.err.ProgrammingError as e:
                    print(f"Failed to create a table - {e}")
                    return {"error": f"Can't create a new table - input is invalid"}

            else:
                return {"error": f"Can't create a new table - table with name {file_name} already exists"}

        # Add data to existing table - insert new rows or columns
        elif action_type == "add_data":
            # Verifying provided column names against current column names.
            columns_to_add = self.columns_verification(self.get_columns(file_name), column_names)

            # Provided column names don't contain the current table columns or their order is different.
            if columns_to_add is False:
                return {"error": "The original table columns can't be removed/replaced and their order can't be modified."}

            # New columns are to be added to the table
            elif isinstance(columns_to_add, list):
                for new_column_name in columns_to_add:
                    query = f"ALTER TABLE {file_name} ADD COLUMN {new_column_name} varchar(255)"

                    # Handling invalid input if provided.
                    try:
                        cursor.execute(query)
                    except pymysql.err.ProgrammingError as e:
                        print(f"Failed to update a table - {e}")
                        return {"error": f"Can't update the table - input is invalid"}

            print(f"Logs: {file_name} - table with such name already exists.")

            print(f"Log: Table data - {table_data}")

        else:
            return {"error": f"Illegal action type - {action_type}"}

        # Filling the table
        for row in table_data:
            inserted_values = "', '".join(row)
            query = f"insert into {file_name} values ('{inserted_values}');"
            print(query)
            cursor.execute(query)

        return {"response": "DB was successfully updated"}

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

    # Checks for the difference between current and suggested table columns.
    def columns_verification(self, existing_columns: list, new_columns: list):

        if len(existing_columns) > len(new_columns):
            return False

        for i in range(len(existing_columns)):
            if existing_columns[i] != new_columns[i]:
                return False

        if len(new_columns) > len(existing_columns):
                return new_columns[len(existing_columns):]

        return True



if __name__ == "__main__":
    executer = Executer()
    new_columns = ["City","Color", "ID", "Altitude", "Depth"]

    print(executer.columns_verification(executer.get_columns("cities"), new_columns))

