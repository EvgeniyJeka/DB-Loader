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

    @pytest.mark.parametrize("remove_table", [["workers"]], indirect=True)
    def test_add_data_json(self, create_worker, remove_table):
        """
        Adding a row  to existing table, verifying table content was updated.

        """
        test_name = "Adding a row and a column to existing table, verifying table content was updated."
        print(f"-----------------Test: '{test_name}'-----------------")

        # Creating the 'workers' table
        create_workers_test_table(workers_json_valid_content)

        # Adding a new worker
        workers_json_valid_content['workers'].append(create_worker)

        # Sending the request
        url = base_url + "add_json/add_data"
        content = {"workers": [create_worker]}

        response = requests.post(url, json=content)
        response_parsed = json.loads(response.content)
        assert response_parsed['response'] == 'DB table workers was successfully updated'

        # Getting table content from DB
        db_table_content = self.executer.get_table_content("workers")
        db_table_content = [list(x) for x in db_table_content]
        db_table_columns = self.executer.get_columns("workers")

        uploaded_json_values = []
        uploaded_json_keys = []

        for i in workers_json_valid_content["workers"]:
            uploaded_json_values.append(list(i.values()))

        uploaded_json_keys.append(list(i.keys()))

        # Verifying uploaded content
        assert db_table_columns == uploaded_json_keys[0], "Error - wrong column names."
        assert db_table_content == uploaded_json_values, "Error - table content doesn't match."
        print(f"-----------------Test '{test_name}'' passed-----------------\n")

    def test_add_data_negative_json_column_renamed(self, worker_invalid_column_name):
        """
        Verifying illegal table modification is blocked - existing columns names can't be modified

        """
        test_name = "Adding new record to an existing table: existing columns can't be renamed - negative test."
        print(f"-----------------Test: '{test_name}'-----------------")

        # Creating the 'workers' table
        tables = self.executer.engine.table_names()
        if 'workers' not in tables:
            create_workers_test_table(workers_json_valid_content)

        # Data addition can't be performed, since the rows of the table in this file are ordered differently.
        url = base_url + "add_json/add_data"

        content = {"workers": [worker_invalid_column_name]}

        response = requests.post(url, json=content)
        response_parsed = json.loads(response.content)

        assert response_parsed['error'] == "The original table columns can't be removed or replaced"

        print(f"-----------------Test '{test_name}' passed-----------------\n")

    def test_add_data_negative_json_column_removed(self, worker_column_missing):
        """
        Verifying illegal table modification is blocked - existing columns  can't be removed

        """
        test_name = "Adding new record to an existing table: existing columns can't be removed - negative test."
        print(f"-----------------Test: '{test_name}'-----------------")

        # Creating the 'workers' table
        tables = self.executer.engine.table_names()
        if 'workers' not in tables:
            create_workers_test_table(workers_json_valid_content)

        # Data addition can't be performed, since the rows of the table in this file are ordered differently.
        url = base_url + "add_json/add_data"

        content = {"workers": [worker_column_missing]}

        response = requests.post(url, json=content)
        response_parsed = json.loads(response.content)

        assert response_parsed['error'] == "The original table columns can't be removed or replaced"

        print(f"-----------------Test '{test_name}' passed-----------------\n")

    def test_add_data_negative_json_column_added(self, worker_column_added):
        """
        Verifying illegal table modification is blocked - columns can't be added to a table on record insertion

        """
        test_name = "Adding new record to an existing table: new columns can't be added  - negative test."
        print(f"-----------------Test: '{test_name}'-----------------")

        # Creating the 'workers' table
        tables = self.executer.engine.table_names()
        if 'workers' not in tables:
            create_workers_test_table(workers_json_valid_content)

        # Data addition can't be performed, since the rows of the table in this file are ordered differently.
        url = base_url + "add_json/add_data"

        content = {"workers": [worker_column_added]}

        response = requests.post(url, json=content)
        response_parsed = json.loads(response.content)

        assert response_parsed['error'] == "The original table columns can't be removed or replaced"

        print(f"-----------------Test '{test_name}' passed-----------------\n")

