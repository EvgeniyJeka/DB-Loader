import pytest
import requests
import json
from Executer import Executer
from tests.conftest import TestTools
import configparser
from tests import conftest

config = configparser.ConfigParser()
config.read("../config.ini")
base_url = config.get("URL", "base_url")


class TestJsonUpload(object):
    executer = Executer("../config.ini")
    content = None

    @pytest.mark.parametrize("remove_table", [["workers"]], indirect=True)
    def test_table_creation_json(self, remove_table):
        """
         Verify confirmation is received on table successful creation.
         Creating the table with "add_json" action.
        :param remove_table: fixture used to remove a table from DB

        """
        test_name = "Verify confirmation is received on table successful creation. Sending JSON."
        print(f"\n-----------------Test: '{test_name}'-----------------")

        url = base_url + "add_json/create"

        worker_1 = {"name": "Anna", "ID": "352", "title": "Designer"}
        worker_2 = {"name": "Boris", "ID": "451", "title": "Front-end Developer"}

        content = {"workers": [worker_1, worker_2]}

        TestJsonUpload.content = content

        response = requests.post(url, json=content)
        response_parsed = json.loads(response.content)

        assert 'response' in response_parsed.keys(), "Error - failed to get confirmation from the server."
        assert response_parsed['response'] == 'DB was successfully updated'
        assert TestTools.table_in_db("workers") is True, "Error - table wasn't created."

        print(f"-----------------Test '{test_name}' passed-----------------\n")

    def test_table_created_negative_json(self):
        """
         Verify an error message is received when trying to create a table while table with such name already exists.
         Trying to create a table with "add_json" action and "create" action type.

        """
        test_name = "Error message is received when a table with such name already exists. Sending JSON."
        print(f"\n-----------------Test: '{test_name}'-----------------")

        url = base_url + "add_json/create"

        worker_1 = {"name": "Anna", "ID": 352, "title": "Designer"}
        content = {"workers": [worker_1]}

        response = requests.post(url, json=content)
        response_parsed = json.loads(response.content)

        assert 'error' in response_parsed.keys(), "Error - incorrect response from the server."
        assert response_parsed['error'] == \
               "Can't create a new table - table with name workers already exists"

        print(f"-----------------Test '{test_name}' passed-----------------\n")

    def test_uploaded_table_content_json(self):
        """
        Verifies the content of the uploaded file.

        """
        test_name = "SQL DB content is identical to uploaded JSON content - XLSX extension."
        print(f"-----------------Test: '{test_name}'-----------------")

        # Getting table content from DB
        db_table_content = self.executer.get_table_content("workers")
        db_table_content = [list(x) for x in db_table_content]
        db_table_columns = self.executer.get_columns("workers")

        uploaded_json_values = []
        uploaded_json_keys = []

        for i in TestJsonUpload.content["workers"]:
            uploaded_json_values.append(list(i.values()))

        uploaded_json_keys.append(list(i.keys()))

        # Verifying uploaded content
        assert db_table_columns == uploaded_json_keys[0], "Error - wrong column names."
        assert db_table_content == uploaded_json_values, "Error - table content doesn't match."

        print(f"-----------------Test '{test_name}'' passed-----------------\n")

    # Overwrite an existing table by sending xlsx file
    def test_overwrite_existing_table_json(self):
        """
        Overwrite an existing table by sending file with the same name and using "overwrite" action type.

        """
        test_name = "Overwrite an existing table by sending JSON."
        print(f"-----------------Test: '{test_name}'-----------------")

        url = base_url + "add_json/overwrite"

        worker_1 = {"name": "Mike", "ID": '920', "title": "Product Manager"}
        content = {"workers": [worker_1]}

        TestJsonUpload.content = content

        response = requests.post(url, json=content)
        response_parsed = json.loads(response.content)

        assert 'response' in response_parsed.keys(), "Error - failed to get confirmation from the server."
        assert response_parsed['response'] == 'DB was successfully updated'

        print(f"-----------------Test '{test_name}' passed-----------------\n")

    def test_verify_content_overwritten_table_json(self):
        """
        Verify table content after it was overwritten.

        """
        test_name = "Verify table content after it was overwritten."
        print(f"-----------------Test: '{test_name}'-----------------")

        # Getting table content from DB
        db_table_content = self.executer.get_table_content("workers")
        db_table_content = [list(x) for x in db_table_content]
        db_table_columns = self.executer.get_columns("workers")

        uploaded_json_values = []
        uploaded_json_keys = []

        for i in TestJsonUpload.content["workers"]:
            uploaded_json_values.append(list(i.values()))

        uploaded_json_keys.append(list(i.keys()))

        # Verifying uploaded content
        assert db_table_columns == uploaded_json_keys[0], "Error - wrong column names."
        assert db_table_content == uploaded_json_values, "Error - table content doesn't match."

        print(f"-----------------Test '{test_name}'' passed-----------------\n")

    def test_add_data_json(self, create_worker):
        """
        Adding a row and a column to existing table, verifying table content was updated.

        """
        test_name = "Adding a row and a column to existing table, verifying table content was updated."
        print(f"-----------------Test: '{test_name}'-----------------")

        TestJsonUpload.content['workers'].append(create_worker)

        # Sending the request
        url = base_url + "add_json/add_data"
        content = {"workers": [create_worker]}

        response = requests.post(url, json=content)
        response_parsed = json.loads(response.content)
        assert response_parsed['response'] == 'DB was successfully updated'

        # Getting table content from DB
        db_table_content = self.executer.get_table_content("workers")
        db_table_content = [list(x) for x in db_table_content]
        db_table_columns = self.executer.get_columns("workers")

        uploaded_json_values = []
        uploaded_json_keys = []

        for i in TestJsonUpload.content["workers"]:
            uploaded_json_values.append(list(i.values()))

        uploaded_json_values[0].append(None)

        uploaded_json_keys.append(list(i.keys()))

        # Verifying uploaded content
        assert db_table_columns == uploaded_json_keys[0], "Error - wrong column names."
        assert db_table_content == uploaded_json_values, "Error - table content doesn't match."
        print(f"-----------------Test '{test_name}'' passed-----------------\n")

    def test_add_data_negative_json(self, worker_invalid_column_order):
        """
        Verifying illegal table modification is blocked. When adding data rows and columns can be only added.

        """
        test_name = "Adding a row and a column to existing table - negative test."
        print(f"-----------------Test: '{test_name}'-----------------")

        # Data addition can't be performed, since the rows of the table in this file are ordered differently.
        url = base_url + "add_json/add_data"

        content = {"workers": [worker_invalid_column_order]}

        response = requests.post(url, json=content)
        response_parsed = json.loads(response.content)

        assert response_parsed['error'] == \
               "The original table columns can't be removed/replaced and their order can't be modified."

        print(f"-----------------Test '{test_name}' passed-----------------\n")

    @pytest.mark.parametrize("remove_table", [["workers"]], indirect=True)
    def test_table_blank_cells_json(self, remove_table, create_worker):
        """
        Verifying table that contains blank cells and empty strings is created and it's content is saved.

        :param remove_table: fixture used to remove the "workers" table if exists.
        """
        test_name = "Verifying table with blank cells is created and it's content is saved."
        print(f"-----------------Test: '{test_name}'-----------------")

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


        # Next test:
        # Download table content as JSON, verify against DB table.

    @pytest.mark.parametrize("prepare_table", [['./test_files/cities_test.xlsx']])
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

    @pytest.mark.parametrize("remove_table", [["workers"]], indirect=True)
    def test_sql_injection_table_name_blocked(self, remove_table):
        """
         Verify SQL injection in file name is blocked
        :param remove_table: fixture used to remove a table from DB

        """
        test_name = "Verify SQL injection in file name is blocked. Sending JSON."
        print(f"\n-----------------Test: '{test_name}'-----------------")

        url = base_url + "add_json/create"

        worker_1 = {"name": "Anna", "ID": "352", "title": "Designer"}
        worker_2 = {"name": "Boris", "ID": "451", "title": "Front-end Developer"}

        content = {"; select true;": [worker_1, worker_2]}

        TestJsonUpload.content = content

        response = requests.post(url, json=content)
        response_parsed = json.loads(response.content)

        assert response_parsed['error'] == "Can't create a new table - input is invalid",\
            "SQL injection in JSON file name wasn't blocked"

        print(f"-----------------Test '{test_name}' passed-----------------\n")





