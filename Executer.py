import configparser
import logging

from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
import sqlalchemy as db
from sqlalchemy import exc


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
        """
        This method can be used to overwrite an existing table. Table structure can be changed.
        The original table is removed, and new one is created and filled
        :param file_name:  Table name, str
        :param column_names: Table columns list
        :param table_data: a list - each element will become a record in the table
        :return:
        """

        logging.info(f"Executer: Adding data to an existing table - '{file_name}'")
        tables = self.engine.table_names()

        # Verifying the table exist - if it doesn't creating a new table from scratch
        if file_name not in tables:
            logging.warning(f"Table {file_name} does not exists in DB - can't update or overwrite")
            return self.create_table_from_scratch(file_name, column_names, table_data)

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

    def fill_table(self, file_name, table_data, table_emp, column_names):
        """
         This method can be used to fill a table with data
        :param file_name:  Table name, str
        :param table_data: a list - each element will become a record in the table
        :param table_emp: Sql alchemy instance that represents the table
        :param column_names: Table columns list
        :return:
        """

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
        """
        This method can be used to create a new SQL table from scratch.
        :param file_name: Table name, str
        :param column_names: Table columns list
        :param table_data: table data, list - each element will become a record in the table
        :return: dict (confirmation message or error message)
        """

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

    def add_data_existing_table(self, file_name, column_names, table_data):
        """
        This method can be used to add records to an existing table. Added record must match the table structure.
        :param file_name: Table name, str
        :param column_names: Table columns, list
        :param table_data: Records that should be added, list or tuple
        :return: dict (confirmation message)
        """

        logging.info(f"Executer: Adding data to an existing table - '{file_name}'")

        # Validating input
        if isinstance(self.validating_record_before_adding(file_name, column_names, table_data), dict):
            return self.validating_record_before_adding(file_name, column_names, table_data)

        # Inserting the records
        metadata = db.MetaData()
        updated_table = db.Table(file_name, metadata, autoload=True, autoload_with=self.engine)

        added_values = []

        for row in table_data:
            element = {}
            for column_number in range(0, len(column_names)):
                element[column_names[column_number]] = row[column_number]

            added_values.append(element)

        query = updated_table.insert().values([*added_values])
        self.cursor.execute(query)

        return {"response": f"DB table {file_name} was successfully updated"}

    def validating_record_before_adding(self, file_name, column_names, table_data):
        """
         This method is used to verify that the provided record can be added to the given table.
         The table must exist in the DB.
         The columns amount in the record must be identical to the columns amount in the table
        :param file_name: table name, str
        :param column_names: columns list, list
        :param table_data: , added record (list or tuple)
        :return: error message (dict) on error
        """

        tables = self.engine.table_names()

        # Verifying the table exist - if it doesn't it can't be updated
        if file_name not in tables:
            logging.warning(f"Table {file_name} does not exists in DB - can't update or overwrite")
            return {"error": f"Table {file_name} does not exists in DB - can't update or overwrite"}

        table_columns_amount = len(column_names)

        # Validating provided column names
        table_columns = self.get_columns(file_name)
        if table_columns != column_names:
            logging.error(f"Table columns: {table_columns}, provided column names: {column_names}")
            return {"error": "The original table columns can't be removed or replaced"}

        # Verifying the provided data can be inserted into the table
        for record in table_data:
            if len(record) != table_columns_amount:
                return {"error": "Column count doesn't match value count"}

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
        metadata = db.MetaData()
        table_ = db.Table(table, metadata, autoload=True, autoload_with=self.engine)

        query = db.select([table_])
        ResultProxy = self.cursor.execute(query)
        result = ResultProxy.fetchall()

        return result




if __name__ == "__main__":
    pass


    # executer = Executer("./config.ini")
    #
    # a = ['workers', ['name', 'ID', 'title'], [['Anna0x00', '352', 'Designer'], ['Boris', '451', 'Front-end Developer']]]
    # print(executer.validate_args(a))

    # file_name = '"; select true;"'
    # column_names = ("car", "speed", "location")
    # table_data = (('Volvo', '110', 'Rishon Le Zion'), ('Hammer', '130', 'Berlin'), ('Kia', '80', 'Kiev'))
    #
    # #print(executer.validate_args([file_name, column_names, table_data]))
    #
    # # Creating from scratch and filling SQL table
    # print(executer.create_table_from_scratch(file_name, column_names, table_data))
    # added_data = (('Nissan', '80', 'New York'),)
    #
    #
    # # Adding record to an existing table
    # added_data_ = (('Nissan', '80', 'New York'), ('Subaru', '98', 'New York'))
    # print(executer.add_data_existing_table(file_name, column_names, added_data_))




    # # Adding columns to an existing table: added column "condition"
    #column_names = ("car", "speed", "location", "condition")
    # table_data_updated = (('Volvo', '110', 'Rishon Le Zion', "OK"), ('Hammer', '130', 'Berlin', "Good"), ('Kia', '80', 'Kiev', "Broken"))
    # print(executer.add_data_existing_table(file_name, column_names, table_data_updated))
    #
    # # Get table columns as list
    # columns = executer.get_columns(file_name)
    # print(columns)
    #
    # # Overwriting an existing table
    # table_data_updated_ = (('Volvo', '110', 'Rishon Le Zion', "OK"), ('Hammer', '130', 'Berlin', "Good"), ('Kia', '80', 'Kiev', "Good"))
    # print(executer.overwrite_table(file_name, column_names, table_data_updated_))
    #
    # # Getting table content
    # print(executer.get_table_content('cars'))




