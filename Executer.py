import pymysql
import configparser
import logging

from psycopg2 import sql


class Executer(object):
    """
    This class contains all CRUD methods.
    The methods can be used via class instance.

    The method 'connect_me' is used to create a cursor, that can
    be passed to other method that require cursor.

    """

    def __init__(self, config_file_path):

        # Reading DB name, host and credentials from config
        config = configparser.ConfigParser()
        config.read(config_file_path)
        hst = config.get("SQL_DB", "host")
        usr = config.get("SQL_DB", "user")
        pwd = config.get("SQL_DB", "password")
        db_name = config.get("SQL_DB", "db_name")

        self.cursor = self.connect_me(hst, usr, pwd, db_name)

    # Connect to DB
    def connect_me(self, hst, usr, pwd, db_name):
        """
        This method is used to establish a connection to MySQL DB.
        Credentials , host and DB name are taken from "config.ini" file.

        :param hst: host
        :param usr: user
        :param pwd: password
        :param db_name: DB name
        :return: mysql cursor
        """
        try:
            conn = pymysql.connect(host=hst, user=usr, password=pwd, autocommit='True')
            cursor = conn.cursor()

            cursor.execute('show databases')
            databases = [x[0] for x in cursor.fetchall()]

            if db_name in databases:
                query = f"USE {db_name}"
                logging.info(f"Executing query |{query}|")
                cursor.execute(query)

            else:
                query = f"CREATE DATABASE {db_name}"
                logging.info(f"Executing query | {query}|")
                cursor.execute(query)

        # Wrong Credentials error
        except pymysql.err.OperationalError as e:
            logging.critical("SQL DB -  Wrong Credentials or Host")
            logging.critical(e)

        # Wrong DB name error
        except pymysql.err.InternalError as e:
            logging.critical("SQL DB - Unknown Database")
            logging.critical(e)

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
            return self.overwrite_table(file_name, column_names, table_data)

        # Create a new table
        elif action_type == "create":
            return self.create_table_from_scratch(file_name, column_names, table_data)

        # Add data to existing table - insert new rows or columns
        elif action_type == "add_data":
            return self.add_data_existing_table(file_name, column_names, table_data)

        else:
            return {"error": f"Illegal action type - {action_type}"}

    def overwrite_table(self, file_name, column_names, table_data):
        cursor = self.cursor

        cursor.execute('show tables')
        tups = cursor.fetchall()

        tables = [tup[0] for tup in tups]

        if file_name in tables:
            cursor.execute(f"drop table {file_name}")

        added_columns = " varchar(255),".join(column_names)
        query = f"CREATE TABLE {file_name} ({added_columns} " + "varchar(255)" + ");"
        logging.info(f"Executing query |{query}|")
        cursor.execute(query)

        return self.fill_table(file_name, table_data)

    def fill_table(self, file_name, table_data):
        cursor = self.cursor

        # Filling the table
        for row in table_data:
            inserted_values = "', '".join(row)
            query = f"insert into {file_name} values ('{inserted_values}');"
            logging.info(f"Executing query |{query}|")
            cursor.execute(query)

        return {"response": "DB was successfully updated"}

    def create_table_from_scratch(self, file_name, column_names, table_data):
        cursor = self.cursor

        cursor.execute('show tables')
        tups = cursor.fetchall()

        tables = [tup[0] for tup in tups]

        # Creating new table to store the file content if not exist.
        if file_name not in tables:
            logging.info(f"{file_name} table is missing! Creating the {file_name} table")

            added_columns = " varchar(255),".join(column_names)
            query = f"CREATE TABLE {file_name} ({added_columns} " + "varchar(255)" + ");"
            logging.info(f"Executing query |{query}|")

            # Handling invalid input if provided.
            try:
                cursor.execute(query)
            except pymysql.err.ProgrammingError as e:
                logging.warning(f"Failed to create a table - {e}")
                return {"error": f"Can't create a new table - input is invalid"}

        else:
            return {"error": f"Can't create a new table - table with name {file_name} already exists"}

        return self.fill_table(file_name, table_data)

    def add_data_existing_table(self, file_name, column_names, table_data):
        cursor = self.cursor

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

        logging.info(f"{file_name} - table with such name already exists.")
        logging.info(f"Log: Table data - {table_data}")

        return self.fill_table(file_name, table_data)

    def get_columns(self, table):
        """
        Get Table Column Names
        :param table: table name, String
        :return: list
        """
        cursor = self.cursor
        query = 'show columns from ''%s'';' % table
        cursor.execute(query)
        columns = cursor.fetchall()
        result = []

        for cl in columns:
            result.append(cl[0])

        return result

    def get_table_content(self, table):
        """
        Get table content from DB
        :param table: table name, String
        :return: tuple
        """
        cursor = self.cursor
        query = f'select * from {table};'
        cursor.execute(query)
        result = cursor.fetchall()
        return result

    def columns_verification(self, existing_columns: list, new_columns: list):
        """
        Checks for the difference between current and suggested table columns.
        :param existing_columns: list
        :param new_columns: list
        :return: list
        """
        if len(existing_columns) > len(new_columns):
            return False

        for i in range(len(existing_columns)):
            if existing_columns[i] != new_columns[i]:
                return False

        if len(new_columns) > len(existing_columns):
            return new_columns[len(existing_columns):]

        return True


if __name__ == "__main__":

    mplanet = 'Mars'

    direction = 'Down'
    bars = 760

    executer = Executer("./config.ini")
    # query = "select * from planets where Planet = %(mplanet)s;"
    # executer.cursor.execute(query,{'mplanet': mplanet})
    # print(executer.cursor.fetchall())


    query = "select * from moderate where Moves = %s and Bars = %s;"
    executer.cursor.execute(query, (direction, bars))
    print(executer.cursor.fetchall())


