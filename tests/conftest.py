import time

import pytest
from Executer import Executer
import requests
import json
import xlrd
import configparser
import random
import csv
import sqlalchemy as db

config = configparser.ConfigParser()
config.read("../config.ini")
base_url = config.get("URL", "base_url")

executer = Executer("./config.ini")

worker_1 = {"name": "Anna", "ID": "352", "title": "Designer"}
worker_2 = {"name": "Boris", "ID": "451", "title": "Front-end Developer"}
workers_json_valid_content = {"workers": [worker_1, worker_2]}

worker_1 = {"name": "Mike", "ID": '920', "title": "Product Manager"}
workers_single_worker_content = {"workers": [worker_1]}

worker_3 = {"name": "Alla", "ID": "651", "title": "Delivery Manager"}
worker_4 = {"name": "Alex", "ID": "1011", "title": "RnD Director"}
workers_json_overwritten_content = {"workers": [worker_3, worker_4]}

city_1 = {"City": "Tel Aviv", "Color": "Green", "ID": "101"}
city_2 = {"City": "Petah Tikva", "Color": "Red", "ID": "201"}
city_3 = {"City": "Rishon LeZion", "Color": "Purple", "ID": "301"}
city_4 = {"City": "Haifa", "Color": "Blue", "ID": "401"}
city_5 = {"City": "Jerusalem", "Color": "White", "ID": "501"}
city_6 = {"City": "Rome", "Color": "Yellow", "ID": "121"}
cities_json_content = {"cities_test": [city_1, city_2, city_3, city_4, city_5, city_6]}


def create_cities_test_table(content):
    url = base_url + "add_json/overwrite"
    # Creating the table
    response = requests.post(url, json=content)
    response_parsed = json.loads(response.content)
    assert response_parsed['response'] == 'DB was successfully updated', "Failed to create the 'workers' test table"


def create_workers_test_table(content):
    url = base_url + "add_json/overwrite"
    # Creating the table
    response = requests.post(url, json=content)
    response_parsed = json.loads(response.content)
    assert response_parsed['response'] == 'DB was successfully updated', "Failed to create the 'workers' test table"


@pytest.fixture(scope="function")
def remove_table(request):
    table_name = request.param[0]

    tables = executer.engine.table_names()

    if table_name in tables:
        #executer.cursor.execute(f"drop table {table_name}")
        metadata = db.MetaData()
        db.Table(table_name, metadata, autoload=True, autoload_with=executer.engine)
        metadata.drop_all(executer.engine)



@pytest.fixture(scope="class")
def prepare_table(request):
    file_path = request.param[0]

    # Uploading the initial table variation
    url = base_url + "add_file/overwrite"
    fin = open(file_path, 'rb')

    files = {'file': fin}

    try:
        response = requests.post(url, files=files)
        response_parsed = json.loads(response.content)
        assert response_parsed['response'] == 'DB was successfully updated'

    except json.decoder.JSONDecodeError as e:
        print(f"Failed to convert the response to JSON, response: {response}, text: {response.content}")
        raise e

    finally:
        fin.close()

@pytest.fixture(scope= "function")
def create_worker():
    # Creating new row to be inserted to the table.
    worker_4 = {}
    worker_4["name"] = f"John_{random.randint(1,1000)}"
    worker_4["ID"] = str(random.randint(1,1000))
    worker_4["title"] = "QA"

    return worker_4

@pytest.fixture(scope= "function")
def worker_invalid_column_name():
    # Creating new row to be inserted to the table.
    worker_4 = {}
    worker_4["name"] = f"John_{random.randint(1,1000)}"
    worker_4["position"] = "QA"
    worker_4["ID"] = str(random.randint(1,1000))

    return worker_4

@pytest.fixture(scope= "function")
def worker_column_missing():
    # Creating new row to be inserted to the table.
    worker_5 = {}
    worker_5["name"] = f"John_{random.randint(1,1000)}"
    worker_5["ID"] = str(random.randint(1,1000))

    return worker_5


@pytest.fixture(scope="function")
def worker_column_added():
    # Creating new row to be inserted to the table.
    worker_6 = {"name": f"John_{random.randint(1, 1000)}", "position": "QA", "ID": str(random.randint(1, 1000)),
                "location": "Italy"}

    return worker_6


@pytest.fixture(scope="class")
def table_add_data_expected_result(request):
    update_file_path = request.param[0]
    table_name = request.param[1]

    # Saving the columns and the content of the file that contains the update
    wb = xlrd.open_workbook(update_file_path)
    sheet = wb.sheet_by_index(0)

    table_columns = []
    table_rows = []

    for i in range(sheet.ncols):
        table_columns.append(sheet.cell_value(0, i))

    expected_table_columns = table_columns

    # Saving the content of DB table before the update.
    expected_table_content = executer.get_table_content(table_name)
    expected_table_content = [list(x) for x in expected_table_content]

    # Emulating the update - appending the data taken from the file to the data saved in DB table
    for i in range(1, sheet.nrows):
        table_rows.append([str(x) for x in sheet.row_values(i)])

    # No values in newly added column
    for el in expected_table_content:
        el.append(None)

    for row in table_rows:
        expected_table_content.append(row)

    return {"expected_table_columns": expected_table_columns, "expected_table_content": expected_table_content}


class TestTools(object):

    @staticmethod
    def get_excel_file_content(path):

        # Getting the content of excel file
        wb = xlrd.open_workbook(path)
        sheet = wb.sheet_by_index(0)

        table_headers = []
        table_content = []

        for i in range(sheet.ncols):
            table_headers.append(sheet.cell_value(0, i))

        for i in range(1, sheet.nrows):
            table_content.append([str(x) for x in sheet.row_values(i)])

        return {"table_headers":table_headers, "table_content":table_content}

    @staticmethod
    def getc_csv_content(path):

        received_file = open(path, "r")
        line_count = 0
        csv_reader = csv.reader(received_file, delimiter=',')

        rows = []

        for row in csv_reader:
            if line_count == 0:
                column_names = row
                line_count += 1
            else:
                if row:
                    rows.append(row)

        return {"content": rows, "headers": column_names}

    @staticmethod
    def table_in_db(table_name):
        # executer.cursor.execute('show tables')
        # tups = executer.cursor.fetchall()
        tables =  executer.engine.table_names()

        if table_name in tables:
            return True

        return False







