import pytest
from Executer import Executer
import requests
import json
import xlrd
import configparser
import random
import csv

config = configparser.ConfigParser()
config.read("../config.ini")
base_url = config.get("URL","base_url")
#base_url = f"http://127.0.0.1:5000/"

executer = Executer("../config.ini")

@pytest.fixture(scope = "function")
def remove_table(request):
    table_tame = request.param[0]

    cursor = executer.cursor

    cursor.execute('show tables')
    tups = cursor.fetchall()
    tables = [tup[0] for tup in tups]

    if table_tame in tables:
        cursor.execute(f"drop table {table_tame}")


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
    worker_4["location"] = "Italy"

    return worker_4

@pytest.fixture(scope= "function")
def worker_invalid_column_order():
    # Creating new row to be inserted to the table.
    worker_4 = {}
    worker_4["name"] = f"John_{random.randint(1,1000)}"
    worker_4["ID"] = str(random.randint(1,1000))
    worker_4["location"] = "Italy"
    worker_4["title"] = "QA"

    return worker_4

@pytest.fixture(scope = "class")
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

        return {"content":rows, "headers":column_names}

    @staticmethod
    def table_in_db(table_name):
        executer.cursor.execute('show tables')
        tups = executer.cursor.fetchall()
        tables = [tup[0] for tup in tups]

        if table_name in tables:
            return True

        return False







