import pytest
import requests
import json
from Executer import Executer
from tests.conftest import TestTools
import configparser

config = configparser.ConfigParser()
config.read("../config.ini")
base_url = config.get("URL", "base_url")


class TestFileUpload(object):
    executer = Executer("../config.ini")

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

    def test_table_created_negative(self):
        """
        Verify an error message is received when trying to create a table while table with such name already exists.

        """
        test_name = "Error message is received when a table with such name already exists"
        print(f"-----------------Test: '{test_name}'-----------------")

        url = base_url + "add_file/create"

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

    def test_uploaded_table_content(self):
        """
        Verifies the content of the uploaded file.

        """
        test_name = "SQL DB content is identical to uploaded file content - XLSX extension."
        print(f"-----------------Test: '{test_name}'-----------------")

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

    # Overwrite an existing table by sending xlsx file
    def test_overwrite_existing_table(self):
        """
        Overwrite an existing table by sending file with the same name and using "overwrite" action type.

        """
        test_name = "Overwrite an existing table by sending xlsx file"
        print(f"-----------------Test: '{test_name}'-----------------")

        url = base_url + "add_file/overwrite"
        fin = open('./test_files/overwrite_1/cities_test.xlsx', 'rb')
        files = {'file': fin}

        try:
            response = requests.post(url, files=files)
            response_parsed = json.loads(response.content)

            assert 'response' in response_parsed.keys(), "Error - failed to get confirmation from the server."
            assert response_parsed['response'] == 'DB was successfully updated'

        finally:
            fin.close()

        print(f"-----------------Test '{test_name}' passed-----------------\n")

    def test_verify_content_overwritten_table(self):
        """
        Verify table content after it was overwritten.

        """
        test_name = "Verify table content after it was overwritten."
        print(f"-----------------Test: '{test_name}'-----------------")

        # Getting table content from DB
        db_table_content = self.executer.get_table_content("cities_test")
        db_table_content = [list(x) for x in db_table_content]
        db_table_columns = self.executer.get_columns("cities_test")

        # Getting table content from xlsx file used for the test
        excel_file_content = TestTools.get_excel_file_content("./test_files/overwrite_1/cities_test.xlsx")

        # Verifying uploaded content
        assert db_table_columns == excel_file_content["table_headers"], "Error - wrong column names."
        assert db_table_content == excel_file_content["table_content"], "Error - table content doesn't match."

        print(f"-----------------Test '{test_name}'' passed-----------------\n")

    # Adding a row and a column to existing table, verifying table content was updated.
    @pytest.mark.parametrize("prepare_table", [['./test_files/overwrite_1/cities_test.xlsx']])
    @pytest.mark.parametrize("table_add_data_expected_result",
                             [["./test_files/overwrite_2/cities_test.xlsx", "cities_test"]], indirect=True)
    def test_add_data(self, prepare_table, table_add_data_expected_result):
        """
        Adding a row and a column to existing table, verifying table content was updated.

        :param prepare_table: fixture used to set precondition.
        :param table_add_data_expected_result: fixture used to set precondition.
        """
        test_name = "Adding a row and a column to existing table, verifying table content was updated."
        print(f"-----------------Test: '{test_name}'-----------------")

        # Updating the table via service method
        url = base_url + "add_file/add_data"
        fin = open('./test_files/overwrite_2/cities_test.xlsx', 'rb')

        files = {'file': fin}

        try:
            response = requests.post(url, files=files)
            response_parsed = json.loads(response.content)
            assert response_parsed['response'] == 'DB was successfully updated', "Error - add data request denied"

        finally:
            fin.close()

        # Verifying the update in DB
        db_table_content = self.executer.get_table_content("cities_test")
        db_table_content = [list(x) for x in db_table_content]
        db_table_columns = self.executer.get_columns("cities_test")

        assert db_table_content == table_add_data_expected_result["expected_table_content"], \
            "Table content wasn't updated as expected."
        assert db_table_columns == table_add_data_expected_result["expected_table_columns"], \
            "Table columns weren't updated as expected."

        print(f"-----------------Test '{test_name}' passed-----------------\n")

    def test_add_data_negative(self):
        """
        Verifying illegal table modification is blocked. When adding data rows and columns can be only added.

        """
        test_name = "Adding a row and a column to existing table - negative test."
        print(f"-----------------Test: '{test_name}'-----------------")

        # Data addition can't be performed, since the rows of the table in this file are ordered differently.
        url = base_url + "add_file/add_data"
        fin = open('./test_files/overwrite_3/cities_test.xlsx', 'rb')

        files = {'file': fin}

        try:
            response = requests.post(url, files=files)
            response_parsed = json.loads(response.content)
            assert response_parsed['error'] == \
                   "The original table columns can't be removed/replaced and their order can't be modified."

        finally:
            fin.close()

        print(f"-----------------Test '{test_name}' passed-----------------\n")

    @pytest.mark.parametrize("remove_table", [["cities_test"]], indirect=True)
    def test_overwrite_non_existing(self, remove_table):
        """
        Verifying new table is created when trying to overwrite non-existing table.
        :param remove_table: fixture used to set precondition.
        """
        test_name = "Overwriting non-existing table, verifying content."
        print(f"-----------------Test: '{test_name}'-----------------")

        url = base_url + "add_file/overwrite"
        fin = open('./test_files/overwrite_1/cities_test.xlsx', 'rb')
        files = {'file': fin}

        # Performing overwrite procedure - using non-existing table name.
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
        excel_file_content = TestTools.get_excel_file_content("./test_files/overwrite_1/cities_test.xlsx")

        # Verifying uploaded content
        assert db_table_columns == excel_file_content["table_headers"], "Error - wrong column names."
        assert db_table_content == excel_file_content["table_content"], "Error - table content doesn't match."

        print(f"-----------------Test '{test_name}' passed-----------------\n")

    @pytest.mark.parametrize("remove_table", [["invalid_table"]], indirect=True)
    def test_create_invalid_table(self, remove_table):
        """
        Verifying table isn't created and error message is presented when sending file with invalid table structure.
        :param remove_table: fixture used to set precondition.
        """
        test_name = "Create table - sending file with invalid content, more columns than column names."
        print(f"-----------------Test: '{test_name}'-----------------")

        url = base_url + "add_file/create"

        fin = open('./test_files/invalid_table.xlsx', 'rb')
        files = {'file': fin}
        try:
            response = requests.post(url, files=files)
            response_parsed = json.loads(response.content)

            assert response_parsed['error'] == "Can't create a new table - input is invalid", \
                "Error - invalid input handling has failed. Error message expected."
            assert TestTools.table_in_db("invalid_table") is False, \
                "Error - table created although invalid query was used."

        finally:
            fin.close()

        print(f"-----------------Test '{test_name}' passed-----------------\n")

    @pytest.mark.parametrize("remove_table", [["empty_cell"]], indirect=True)
    def test_create_table_blank_cells(self, remove_table):
        """
        Verifying table with blank cells is created and it's content is saved.

        :param remove_table: fixture used to set precondition.
        """
        test_name = "Verifying table with blank cells is created and it's content is saved. "
        print(f"-----------------Test: '{test_name}'-----------------")

        # Sending the request
        url = base_url + "add_file/overwrite"
        fin = open('./test_files/empty_cell.xlsx', 'rb')
        files = {'file': fin}

        try:
            response = requests.post(url, files=files)
            response_parsed = json.loads(response.content)

            assert 'response' in response_parsed.keys(), "Error - failed to get confirmation from the server."
            assert response_parsed['response'] == 'DB was successfully updated'

        finally:
            fin.close()

        # Verifying content
        db_table_content = self.executer.get_table_content("empty_cell")
        db_table_content = [list(x) for x in db_table_content]
        db_table_columns = self.executer.get_columns("empty_cell")

        # Getting table content from xlsx file used for the test
        excel_file_content = TestTools.get_excel_file_content("./test_files/empty_cell.xlsx")

        # Verifying uploaded content
        assert db_table_columns == excel_file_content["table_headers"], "Error - wrong column names."
        assert db_table_content == excel_file_content["table_content"], "Error - table content doesn't match."

        print(f"-----------------Test '{test_name}' passed-----------------\n")
