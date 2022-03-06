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


class TestJsonDownload(object):
    executer = Executer("./config.ini")

    # Download table content as JSON, verify against DB table.
    @pytest.mark.parametrize("prepare_table", [['./test_files/cities_test.xlsx']],indirect=True)
    def test_table_as_json(self, prepare_table):

        # Sending the request
        url = base_url + "table_to_json/cities_test"

        response = requests.get(url=url)
        response_parsed = json.loads(response.content)

        db_table_content = self.executer.get_table_content("cities_test")
        db_table_content = [list(x) for x in db_table_content]
        db_table_columns = self.executer.get_columns("cities_test")

        uploaded_json_values = []
        uploaded_json_keys = []

        for i in response_parsed:
            uploaded_json_values.append(list(i.values()))

        uploaded_json_keys.append(list(i.keys()))

        assert db_table_columns == uploaded_json_keys[0], "Error - wrong column names."
        assert db_table_content == uploaded_json_values, "Error - table content doesn't match."







