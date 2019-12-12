import csv

class Core(object):

    # def __init__(self):
    #     executor = Executor()
    
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


        # Creating new table
        # executor.create_table(file_name, column_names)

        # Filling the table
        # executer.fill_table(file_name, rows)

        return data