import pytest
import requests
import json
from Executer import Executer
from tests.conftest import TestTools
import configparser, logging


config = configparser.ConfigParser()
config.read("./config.ini")
base_url = config.get("URL", "base_url")


class TestSupportedExtensions(object):
    executer = Executer("./config.ini")


    @pytest.mark.parametrize("remove_table", [["planets"]], indirect=True)
    def test_upload_xls(self, remove_table):
        """
        Verifying xls files content is successfully uploaded to MySQL DB.

        """
        test_name = "Verifying xls files content is successfully uploaded to MySQL DB."
        logging.info(f"\n-----------------Test: '{test_name}'-----------------")
        url = base_url + "add_file/create"

        fin = open('./test_files/planets.xls', 'rb')
        files = {'file': fin}
        try:
            response = requests.post(url, files=files)
            response_parsed = json.loads(response.content)

            assert 'response' in response_parsed.keys(), "Error - failed to get confirmation from the server."
            assert response_parsed['response'] == 'DB was successfully updated'
            assert TestTools.table_in_db("planets") is True, "Error - table wasn't created."

        finally:
            fin.close()

        # Getting table content from DB
        db_table_content = self.executer.get_table_content("planets")
        db_table_content = [list(x) for x in db_table_content]
        db_table_columns = self.executer.get_columns("planets")

        # Getting table content from xlsx file used for the test
        xls_file_content = TestTools.get_excel_file_content("./test_files/planets.xls")

        # Verifying uploaded content
        assert db_table_columns == xls_file_content["table_headers"], "Error - wrong column names."
        assert db_table_content == xls_file_content["table_content"], "Error - table content doesn't match."
        logging.info(f"-----------------Test '{test_name}'' passed-----------------\n")