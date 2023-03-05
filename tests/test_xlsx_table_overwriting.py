import pytest
import requests
import json
from Executer import Executer
from tests.conftest import TestTools
import configparser, logging

config = configparser.ConfigParser()
config.read("./config.ini")
base_url = config.get("URL", "base_url")


class TestFileUpload(object):
    executer = Executer("./config.ini")

    # Overwrite an existing table by sending xlsx file
    @pytest.mark.parametrize("prepare_table", [['./test_files/cities_test.xlsx']], indirect=True)
    def test_overwrite_existing_table(self, prepare_table):
        """
        Overwrite an existing table by sending file with the same name and using "overwrite" action type.

        """
        test_name = "Overwrite an existing table by sending xlsx file"
        logging.info(f"-----------------Test: '{test_name}'-----------------")

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

        logging.info(f"-----------------Test '{test_name}' passed-----------------\n")

    @pytest.mark.parametrize("prepare_table", [['./test_files/cities_test.xlsx']], indirect=True)
    def test_verify_content_overwritten_table(self, prepare_table):
        """
        Verify table content after it was overwritten.

        """
        test_name = "Verify table content after it was overwritten."
        logging.info(f"-----------------Test: '{test_name}'-----------------")

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

        # Getting table content from DB
        db_table_content = self.executer.get_table_content("cities_test")
        db_table_content = [list(x) for x in db_table_content]
        db_table_columns = self.executer.get_columns("cities_test")

        # Getting table content from xlsx file used for the test
        excel_file_content = TestTools.get_excel_file_content("./test_files/overwrite_1/cities_test.xlsx")

        # Verifying uploaded content
        assert db_table_columns == excel_file_content["table_headers"], "Error - wrong column names."
        assert db_table_content == excel_file_content["table_content"], "Error - table content doesn't match."

        logging.info(f"-----------------Test '{test_name}'' passed-----------------\n")

