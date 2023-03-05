import pytest
import requests
import json
from Executer import Executer
import logging
import configparser


config = configparser.ConfigParser()
config.read("../config.ini")
base_url = config.get("URL", "base_url")


class TestJsonUpload(object):
    executer = Executer("./config.ini")

    @pytest.mark.parametrize("remove_table", [["workers"]], indirect=True)
    def test_table_blank_cells_json(self, remove_table, create_worker):
        """
        Verifying table that contains blank cells and empty strings is created and it's content is saved.

        :param remove_table: fixture used to remove the "workers" table if exists.
        """
        test_name = "Verifying table with blank cells is created and it's content is saved."
        logging.info(f"-----------------Test: '{test_name}'-----------------")

        # Creating new table that contains "null" values and empty strings.
        create_worker["title"] = None
        create_worker["location"] = ""
        content = {"workers": [create_worker]}

        # Sending the request
        url = base_url + "add_json/create"
        response = requests.post(url, json=content)
        response_parsed = json.loads(response.content)
        assert response_parsed['response'] == 'DB was successfully updated'

        # Getting table content from DB
        db_table_content = self.executer.get_table_content("workers")
        db_table_content = [list(x) for x in db_table_content]
        db_table_columns = self.executer.get_columns("workers")

        uploaded_json_values = []
        uploaded_json_keys = []

        for i in content["workers"]:
            uploaded_json_values.append(list(i.values()))

        # The value None is saved as "None" in the DB.
        uploaded_json_values[0][2] = "None"
        uploaded_json_keys.append(list(i.keys()))

        # Verifying uploaded content
        assert db_table_columns == uploaded_json_keys[0], "Error - wrong column names."
        assert db_table_content == uploaded_json_values, "Error - table content doesn't match."
        print(f"-----------------Test '{test_name}' passed-----------------\n")





















