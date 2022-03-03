import pytest
import requests
import json
from Executer import Executer
from tests.conftest import TestTools, create_workers_test_table, create_cities_test_table
import configparser

config = configparser.ConfigParser()
config.read("./config.ini")
base_url = config.get("URL", "base_url")


class TestFileUpload(object):
    executer = Executer("./config.ini")

    @pytest.mark.parametrize("remove_table", [["cities_test"]], indirect=True)
    def test_table_created_response(self, remove_table):
        """
         Verify confirmation is received on table successful creation.
        :param remove_table: fixture used to remove a table from DB
        """
        test_name = "Create new table from xlsx file"
        print(f"-----------------Test: '{test_name}'-----------------")

        url = base_url + "add_file/create"

        fin = open('./test_files/cities_test.xlsx', 'rb')
        files = {'file': fin}
        try:
            response = requests.post(url, files=files)
            response_parsed = json.loads(response.content)

            assert 'response' in response_parsed.keys(), "Error - failed to get confirmation from the server."
            assert response_parsed['response'] == 'DB was successfully updated'
            assert TestTools.table_in_db("cities_test") is True, "Error - table wasn't created."

        finally:
            fin.close()

        print(f"-----------------Test '{test_name}' passed-----------------\n")

    @pytest.mark.parametrize("remove_table", [["cities_test"]], indirect=True)
    def test_uploaded_table_content(self, remove_table):
        """
        Verifies the content of the uploaded file.

        """
        test_name = "SQL DB content is identical to uploaded file content - XLSX extension."
        print(f"-----------------Test: '{test_name}'-----------------")

        url = base_url + "add_file/create"

        fin = open('./test_files/cities_test.xlsx', 'rb')
        files = {'file': fin}
        try:
            response = requests.post(url, files=files)
            response_parsed = json.loads(response.content)

            assert 'response' in response_parsed.keys(), "Error - failed to get confirmation from the server."
            assert response_parsed['response'] == 'DB was successfully updated'
            assert TestTools.table_in_db("cities_test") is True, "Error - table wasn't created."

        finally:
            fin.close()

        # Getting table content from DB
        db_table_content = self.executer.get_table_content("cities_test")
        db_table_content = [list(x) for x in db_table_content]
        db_table_columns = self.executer.get_columns("cities_test")

        # Getting table content from xlsx file used for the test
        excel_file_content = TestTools.get_excel_file_content("./test_files/cities_test.xlsx")

        # Verifying uploaded content
        assert db_table_columns == excel_file_content["table_headers"], "Error - wrong column names."
        assert db_table_content == excel_file_content["table_content"], "Error - table content doesn't match."

        print(f"-----------------Test '{test_name}'' passed-----------------\n")

    def test_table_created_negative(self):
        """
        Verify an error message is received when trying to create a table while table with such name already exists.

        """
        test_name = "Error message is received when a table with such name already exists"
        print(f"-----------------Test: '{test_name}'-----------------")

        url = base_url + "add_file/create"

        # Creating the 'cities_test' table (if not exists)
        tables = self.executer.engine.table_names()
        if 'cities_test' not in tables:
            create_workers_test_table(create_cities_test_table)

        fin = open('./test_files/cities_test.xlsx', 'rb')
        files = {'file': fin}

        try:
            response = requests.post(url, files=files)
            response_parsed = json.loads(response.content)

            assert 'error' in response_parsed.keys(), "Error - incorrect response from the server."
            assert response_parsed['error'] == \
                   "Can't create a new table - table with name cities_test already exists"

        finally:
            fin.close()

        print(f"-----------------Test '{test_name}'' passed-----------------\n")