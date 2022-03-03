import pytest
import requests
import json
from Executer import Executer
from tests.conftest import TestTools
import configparser


config = configparser.ConfigParser()
config.read("./config.ini")
base_url = config.get("URL", "base_url")


class TestSupportedExtensions(object):
    executer = Executer("./config.ini")

    @pytest.mark.parametrize("remove_table", [["moderate"]], indirect=True)
    def test_upload_csv(self, remove_table):
        """
        Verifying csv files content is successfully uploaded to MySQL DB.

        """
        test_name = "Verifying csv files content is successfully uploaded to MySQL DB."
        print(f"\n-----------------Test: '{test_name}'-----------------")

        url = base_url + "add_file/create"

        fin = open('./test_files/moderate.csv', 'rb')
        files = {'file': fin}
        try:
            response = requests.post(url, files=files)
            response_parsed = json.loads(response.content)

            assert 'response' in response_parsed.keys(), "Error - failed to get confirmation from the server."
            assert response_parsed['response'] == 'DB was successfully updated'
            assert TestTools.table_in_db("moderate") is True, "Error - table wasn't created."

        finally:
            fin.close()

        # Getting table content from DB
        db_table_content = self.executer.get_table_content("moderate")
        db_table_content = [list(x) for x in db_table_content]
        db_table_columns = self.executer.get_columns("moderate")

        # Getting table content from xlsx file used for the test
        csv_file_content = TestTools.getc_csv_content("./test_files/moderate.csv")

        # Verifying uploaded content
        assert db_table_columns == csv_file_content["headers"], "Error - wrong column names."
        assert db_table_content == csv_file_content["content"], "Error - table content doesn't match."

        print(f"-----------------Test '{test_name}'' passed-----------------\n")

