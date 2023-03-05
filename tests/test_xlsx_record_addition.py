import pytest
import requests
import json
from Executer import Executer
from tests.conftest import add_records_xlsx_files_expected_result
import configparser, logging

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
        logging.info(f"-----------------Test: '{test_name}'-----------------")

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

        logging.info(f"-----------------Test '{test_name}' passed-----------------\n")

    @pytest.mark.parametrize("prepare_table", [['./test_files/overwrite_1/cities_test.xlsx']], indirect=True)
    def test_add_data_negative(self, prepare_table):
        """
        Verifying illegal table modification attempt is blocked.

        """
        test_name = "Adding a row and a column to existing table - negative test."
        logging.info(f"-----------------Test: '{test_name}'-----------------")

        # Data addition can't be performed, since the new table in the xlsx file has a different structure.
        url = base_url + "add_file/add_data"
        fin = open('./test_files/overwrite_3/cities_test.xlsx', 'rb')

        files = {'file': fin}

        try:
            response = requests.post(url, files=files)
            response_parsed = json.loads(response.content)
            print(response_parsed)
            assert response_parsed['error'] == \
                   "The original table columns can't be removed or replaced"

        finally:
            fin.close()

        logging.info(f"-----------------Test '{test_name}' passed-----------------\n")