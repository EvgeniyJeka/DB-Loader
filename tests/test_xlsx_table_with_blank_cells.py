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
