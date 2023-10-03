import pytest
import requests
import json
from Executer import Executer
from tests.conftest import TestTools, workers_json_valid_content, create_workers_test_table
import configparser, logging


config = configparser.ConfigParser()
config.read("../config.ini")
base_url = config.get("URL", "base_url")


class TestJsonUpload(object):
    executer = Executer("./config.ini")

    @pytest.mark.parametrize("remove_table", [["workers"]], indirect=True)
    def test_table_creation_json(self, remove_table):
        """
         Verify confirmation is received on table successful creation.
         Creating the table with "add_json"  action.

        """
        test_name = "Verify confirmation is received on table successful creation. Sending JSON."
        logging.info(f"\n-----------------Test: '{test_name}'-----------------")

        url = base_url + "add_json/create"

        content = workers_json_valid_content

        response = requests.post(url, json=content)
        response_parsed = json.loads(response.content)

        assert 'response' in response_parsed.keys(), "Error - failed to get confirmation from the server."
        assert response_parsed['response'] == 'DB was successfully updated'
        assert TestTools.table_in_db("workers") is True, "Error - table wasn't created."

        logging.info(f"-----------------Test '{test_name}' passed-----------------\n")

    @pytest.mark.parametrize("remove_table", [["workers"]], indirect=True)
    def test_uploaded_table_content_json(self, remove_table):
        """
        Verifies the content of the uploaded file.

        """
        test_name = "SQL DB content is identical to uploaded JSON content - XLSX extension."
        logging.info(f"-----------------Test: '{test_name}'-----------------")

        create_workers_test_table(workers_json_valid_content)

        # Getting table content from DB
        db_table_content = self.executer.get_table_content("workers")
        db_table_content = [list(x) for x in db_table_content]
        db_table_columns = self.executer.get_columns("workers")

        uploaded_json_values = []
        uploaded_json_keys = []

        for i in workers_json_valid_content['workers']:
            uploaded_json_values.append(list(i.values()))

        uploaded_json_keys.append(list(i.keys()))

        # Verifying uploaded content
        assert db_table_columns == uploaded_json_keys[0], "Error - wrong column names."
        assert db_table_content == uploaded_json_values, "Error - table content doesn't match."

        logging.info(f"-----------------Test '{test_name}'' passed-----------------\n")

    def test_table_created_negative_json(self):
        """
         Verify an error message is received when trying to create a table while table with such name already exists.
         Trying to create a table with "add_json" action and "create" action type.

        """
        test_name = "Error message is received when a table with such name already exists. Sending JSON."
        logging.info(f"\n-----------------Test: '{test_name}'-----------------")

        url = base_url + "add_json/create"

        # Creating the 'workers' table
        tables = TestTools.get_tables_list()
        if 'workers' not in tables:
            create_workers_test_table(workers_json_valid_content)

        # Trying to create another table with the same name
        response = requests.post(url, json=workers_json_valid_content)
        response_parsed = json.loads(response.content)

        assert 'error' in response_parsed.keys(), "Error - incorrect response from the server."
        assert response_parsed['error'] == \
               "Can't create a new table - table with name workers already exists"

        logging.info(f"-----------------Test '{test_name}' passed-----------------\n")




















