import csv
from Executer import Executer


# # This info must be taken from config file when an instance of this class is created.
# hst = '127.0.0.1'
# usr = 'root'
# pwd = '7417418'
# db_name = 'play'

class Core(object):

    def __init__(self):
        self.executor = Executer()
        # self.cursor = self.executor.connect_me(hst, usr, pwd, db_name)
    
    def add_csv(self, data, file_name):
        
        # Saving the received file
        received_file = open(f"./input/{file_name}", "w+")
        received_file.write(data)
        received_file.close


        # Extracting data
        received_file = open(f"./input/{file_name}", "r")
        line_count = 0
        csv_reader = csv.reader(received_file, delimiter=',')

        rows = []

        for row in csv_reader:
            if line_count == 0:
                column_names = row
                line_count += 1
            else:
                if row != []:
                    rows.append(row)
                    print(row)


        result = self.executor.create_fill_table(file_name.split('.')[0], column_names, rows)

        return data

    def add_json(self, data):
        table_names = [x for x in data.keys()]

        for table_name in table_names:
            table_json_content = data[table_name]

            try:
                table_columns = [x for x in table_json_content[0].keys()]
                table_rows_value = []
                single_row = []

            except (IndexError, TypeError, AttributeError):
                print(f"Log: Data is missing or corrupted in provided JSON object. Can't fill the table.")
                return False

            # Each JSON key represents a table column. Therefore all JSON objects
            # must have identical keys to fit the table.
            try:
                for element in table_json_content:
                    for column in table_columns:
                        single_row.append(str(element[column]))

                    table_rows_value.append(single_row)
                    single_row = []

            except KeyError as e:
                print(f"Log: Error - the key {e} is missing in one of the JSON objects in the list.")
                return False

            result = self.executor.create_fill_table(table_name, table_columns, table_rows_value)

            if result:
                return f"DB was successfully updated. Table names: {table_names}"

        return False




        #for table in table_names:
