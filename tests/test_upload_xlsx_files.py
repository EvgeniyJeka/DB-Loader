import pytest
import requests
import json
from Executer import Executer
from tests.conftest import TestTools, add_records_xlsx_files_expected_result
import configparser

config = configparser.ConfigParser()
config.read("./config.ini")
base_url = config.get("URL", "base_url")


class TestFileUpload(object):
    executer = Executer("./config.ini")

    @pytest.mark.parametrize("prepare_table", [['./test_files/overwrite_1/cities_test.xlsx']], indirect=True)
    def test_add_data(self, prepare_table):
        """
        Adding several records  to an existing table, verifying table content was updated.

        :param prepare_table: fixture used to set precondition.

        """
        test_name = "Adding several records  to an existing table, verifying table content was updated.."
        print(f"-----------------Test: '{test_name}'-----------------")

        # Updating the table via service method
        url = base_url + "add_file/add_data"
        fin = open('./test_files/overwrite_2/cities_test.xlsx', 'rb')

        files = {'file': fin}

        try:
            response = requests.post(url, files=files)
            response_parsed = json.loads(response.content)
            print(response_parsed)
            assert response_parsed['response'] == 'DB table cities_test was successfully updated', \
                "Error - add data request denied"
        finally:
            fin.close()

        # Verifying the update in DB
        db_table_content = self.executer.get_table_content("cities_test")
        db_table_content = [list(x) for x in db_table_content]

        assert db_table_content == add_records_xlsx_files_expected_result, \
            "Table content wasn't updated as expected."

        print(f"-----------------Test '{test_name}' passed-----------------\n")

    @pytest.mark.parametrize("prepare_table", [['./test_files/overwrite_1/cities_test.xlsx']], indirect=True)
    def test_add_data_negative(self, prepare_table):
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
