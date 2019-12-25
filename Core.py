import csv
from Executer import Executer
import xlrd
import json
import pymysql


class Core(object):

    def __init__(self):
        self.executor = Executer("config.ini")

    def add_csv(self, file_name, action_type):

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
                if row:
                    rows.append(row)
                    print(row)

        result = self.executor.create_fill_table(file_name.split('.')[0], column_names, rows, action_type)

        return result

    def add_xlsx(self, file_name, action_type):

        table_columns = []
        table_rows = []

        wb = xlrd.open_workbook(f"./input/{file_name}")
        sheet = wb.sheet_by_index(0)

        for i in range(sheet.ncols):
            table_columns.append(sheet.cell_value(0, i))

        print(f"Log: Table columns - {table_columns}")

        for i in range(1, sheet.nrows):
            table_rows.append([str(x) for x in sheet.row_values(i)])

        print(f"Log: Table rows - {table_rows}")

        result = self.executor.create_fill_table(file_name.split('.')[0], table_columns, table_rows, action_type)

        return result

    def add_json(self, data, action_type):
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

            result = self.executor.create_fill_table(table_name, table_columns, table_rows_value, action_type)

            if result:
                return f"DB was successfully updated. Table names: {table_names}"

        return False

    def table_as_json(self, table_name):
        """
        Returns table content as a list of JSON objects.
        Each JSON object represents one table record.

        :param table_name: String
        :return: list of JSON objects. The list is empty if there is no records in the table.
        """
        try:
            columns = self.executor.get_columns(table_name)
            records = self.executor.get_table_content(table_name)

        except pymysql.err.ProgrammingError:
            return {"error": "There is no tables with such name in this DB."}

        result = []

        for record in records:
            table_record_json = {}
            cnt = 0
            for column in columns:
                table_record_json[column] = record[cnt]
                cnt += 1
            result.append(table_record_json)

        return json.dumps(result)


if __name__ == "__main__":
    core_test = Core()
    b = core_test.table_as_json("cities")
    c = json.loads(b)
    print(c[0]['City'])

    # a = json.loads(core_test.table_as_json("cities")[0])
    # print(a["City"])
