import pytest
import requests
import json
from Executer import Executer
from tests.conftest import TestTools, workers_json_valid_content, workers_single_worker_content, \
    workers_json_overwritten_content, create_workers_test_table
import configparser

config = configparser.ConfigParser()
config.read("../config.ini")
base_url = config.get("URL", "base_url")


class TestJsonUpload(object):
    executer = Executer("./config.ini")

    # Overwrite an existing table by sending JSON with the same name
    @pytest.mark.parametrize("remove_table", [["workers"]], indirect=True)
    def test_overwrite_existing_table_json(self, remove_table):
        """
        Overwrite an existing table by sending JSON with the same name and using "overwrite" action type.

        """

        test_name = "Overwrite an existing table by sending JSON."
        print(f"-----------------Test: '{test_name}'-----------------")

        url = base_url + "add_json/overwrite"

        # Creating the table
        create_workers_test_table(workers_json_valid_content)

        # Overwrite an existing table
        content = workers_json_overwritten_content

        response = requests.post(url, json=content)
        response_parsed = json.loads(response.content)

        assert 'response' in response_parsed.keys(), "Error - failed to get confirmation from the server."
        assert response_parsed['response'] == 'DB was successfully updated'

        print(f"-----------------Test '{test_name}' passed-----------------\n")

        # Overwrite an existing table by sending JSON with the same name

    @pytest.mark.parametrize("remove_table", [["workers"]], indirect=True)
    def test_verify_content_overwritten_table_json(self, remove_table):
        """
        Verify table content after it was overwritten.

        """
        test_name = "Verify table content after it was overwritten."
        print(f"-----------------Test: '{test_name}'-----------------")

        url = base_url + "add_json/overwrite"

        # Creating the 'workers' table
        create_workers_test_table(workers_json_valid_content)

        # Overwrite an existing table
        content = workers_json_overwritten_content

        response = requests.post(url, json=content)
        response_parsed = json.loads(response.content)
        assert response_parsed['response'] == 'DB was successfully updated'

        # Getting table content from DB
        db_table_content = self.executer.get_table_content("workers")
        db_table_content = [list(x) for x in db_table_content]
        db_table_columns = self.executer.get_columns("workers")

        uploaded_json_values = []
        uploaded_json_keys = []

        for i in workers_json_overwritten_content["workers"]:
            uploaded_json_values.append(list(i.values()))

        uploaded_json_keys.append(list(i.keys()))

        # Verifying uploaded content
        assert db_table_columns == uploaded_json_keys[0], "Error - wrong column names."
        assert db_table_content == uploaded_json_values, "Error - table content doesn't match."

        print(f"-----------------Test '{test_name}'' passed-----------------\n")