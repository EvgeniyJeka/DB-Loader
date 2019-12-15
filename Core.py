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