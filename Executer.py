import pymysql
import configparser
import logging

from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
import sqlalchemy as db
from sqlalchemy import exc

from alembic import op
from sqlalchemy import Column, String


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

        self.cursor, self.engine = self.connect_me(hst, usr, pwd, db_name)

    # Connect to DB
    def connect_me(self, hst, usr, pwd, db_name):
        """
        This method is used to establish a connection to MySQL DB.
        Credentials , host and DB name are taken from "config.ini" file.

        :param hst: host
        :param usr: user
        :param pwd: password
        :param db_name: DB name
        :return: SqlAlchemy connection (cursor)
        """
        import sqlalchemy
        try:

            url = f'mysql+pymysql://{usr}:{pwd}@{hst}:3306/{db_name}'

            # Create an engine object.
            engine = create_engine(url, echo=True)

            # Create database if it does not exist.
            if not database_exists(engine.url):
                create_database(engine.url)
                cursor = engine.connect()
                return cursor, engine
            else:
                # Connect the database if exists.
                cursor = engine.connect()
                return cursor, engine

        # Wrong Credentials error
        except sqlalchemy.exc.OperationalError as e:
            logging.critical("SQL DB -  Can't connect, verify credentials and host, verify the server is available")
            logging.critical(e)

        # General error
        except Exception as e:
            logging.critical("SQL DB - Failed to connect, reason is unclear")
            logging.critical(e)


    # def validate_args(self, received_arg):
    #     if isinstance(received_arg, str):
    #         return len(received_arg.split(" ")) == 1 and received_arg != ';'
    #
    #     elif isinstance(received_arg, list):
    #         for element in received_arg:
    #             if len(element.split(" ")) != 1 or element == ';':
    #                 return False
    #         return True

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
        return self.add_data_existing_table(file_name, column_names, table_data, skip_columns_verification=True)

        # cursor = self.cursor
        #
        # cursor.execute('show tables')
        # tups = cursor.fetchall()
        #
        # tables = [tup[0] for tup in tups]
        #
        # if file_name in tables:
        #     cursor.execute(f"drop table {file_name}")
        #
        # added_columns = " varchar(255),".join(column_names)
        # query = f"CREATE TABLE {file_name} ({added_columns} " + "varchar(255)" + ");"
        # logging.info(f"Executing query |{query}|")
        # cursor.execute(query)

        #return self.fill_table(file_name, table_data)

    def fill_table(self, file_name, table_data, table_emp, column_names):

        logging.info(f"Executer: Filling the table '{file_name}' with data")

        added_values = []

        for row in table_data:
            element = {}
            for column_number in range(0, len(column_names)):
                element[column_names[column_number]] = row[column_number]

            added_values.append(element)

        query = table_emp.insert().values([*added_values])
        self.cursor.execute(query)

        return {"response": "DB was successfully updated"}

    def create_table_from_scratch(self, file_name, column_names, table_data):

        logging.info(f"Executer: Creating a new table from scratch -  '{file_name}'")
        tables = self.engine.table_names()

        # Creating new table to store the file content if not exist.
        if file_name not in tables:
            logging.info(f"{file_name} table is missing! Creating the {file_name} table")
            metadata = db.MetaData()

            # Creating table - column names are provided in a tuple
            columns_list = [db.Column(x, db.String(255)) for x in column_names]

            # SQL Alchemy table instance is passed to the "fill_table" method
            table_emp = db.Table(file_name, metadata, *columns_list, extend_existing=True)
            metadata.create_all(self.engine)

        else:
            return {"error": f"Can't create a new table - table with name {file_name} already exists"}

        return self.fill_table(file_name, table_data, table_emp, column_names)

    def add_data_existing_table(self, file_name, column_names, table_data, skip_columns_verification=None):

        logging.info(f"Executer: Adding data to an existing table - '{file_name}'")
        tables = self.engine.table_names()

        # Verifying the table exist - if it doesn't creating a new table from scratch
        if file_name not in tables:
            logging.warning(f"Table {file_name} does not exists in DB - can't update or overwrite")
            return self.create_table_from_scratch(file_name, column_names, table_data)

        # Skipping this verification when overwriting a table
        if skip_columns_verification is None:
            # Verifying provided column names against current column names.
            columns_to_add = self.columns_verification(self.get_columns(file_name), column_names)

            # Provided column names don't contain the current table columns or their order is different.
            if columns_to_add is False:
                return {"error": "The original table columns can't be removed/replaced and their order can't be modified."}

        metadata = db.MetaData()

        # Creating table - column names are provided in a tuple
        columns_list = [db.Column(x, db.String(255)) for x in column_names]

        # SQL Alchemy table instance is passed to the "fill_table" method
        table_emp = db.Table(file_name, metadata, *columns_list, extend_existing=True)
        metadata.drop_all(self.engine)
        metadata.create_all(self.engine)

        logging.info(f"{file_name} - table with such name already exists.")
        logging.info(f"Log: Table data - {table_data}")

        return self.fill_table(file_name, table_data, table_emp, column_names)

    def get_columns(self, table):
        """
        Get Table Column Names
        :param table: table name, String
        :return: list of columns
        """
        metadata = db.MetaData()
        table_ = db.Table(table, metadata, autoload=True, autoload_with=self.engine)

        return table_.columns.keys()

    def get_table_content(self, table):
        """
        Get table content from DB
        :param table: table name, String
        :return: tuple
        """
        # Verifying no SQL injection can be performed here
        unchecked_input = table
        input_check = self.validate_args(unchecked_input)

        if input_check is False:
            return {"error": f"Can't provide table content - input is invalid"}

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


    executer = Executer("./config.ini")
    file_name = 'bars'
    # column_names = ("car", "speed", "location")
    # table_data = (('Volvo', '110', 'Rishon Le Zion'), ('Hammer', '130', 'Berlin'), ('Kia', '80', 'Kiev'))
    #
    # # Creating from scratch and filling SQL table
    # print(executer.create_table_from_scratch(file_name, column_names, table_data))
    #
    # # Adding columns to an existing table: added column "condition"
    # column_names = ("car", "speed", "location", "condition")
    # table_data_updated = (('Volvo', '110', 'Rishon Le Zion', "OK"), ('Hammer', '130', 'Berlin', "Good"), ('Kia', '80', 'Kiev', "Broken"))
    # print(executer.add_data_existing_table(file_name, column_names, table_data_updated))

    # Get table columns as list
    columns = executer.get_columns(file_name)
    print(columns)

    # Overwriting an existing table




