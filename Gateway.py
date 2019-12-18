import flask
import os
from flask import Flask, render_template
from flask import request
from Core import Core
import csv

app = Flask(__name__)


core = Core()


@app.route("/add_file", methods = ['POST'])
def receive_file():
    """
        Receiving CSV and XLSX files adding their content to DB.
        In this method  API request is processed, it's body is parsed and the content is passed to "add_file" method
        of Core class. If there is a table which name is identical to received file name, table content is
        appended to existing table. Otherwise a new table is created.

        :return: JSON - confirmation on success, error message otherwise.
    """

    # Saving the received file
    file = request.files['file']
    file_extension = file.filename.split('.')[1]
    file_path = f"./input/{file.filename}"
    file.save(file_path)

    if file_extension == 'xlsx' or file_extension == 'xls':
        result = core.add_xlsx(file.filename)
        return result

    elif file_extension == 'csv':
        result = core.add_csv(file.filename)
        return result

    return {"response": "Error - File extension must be CSV, XLS or XLSX."}



@app.route('/add_json', methods = ['POST'])
def receive_json():
    data = request.get_json()
    result = core.add_json(data)

    if result:
        return result

    else:
        return f"The requested operation has failed."




if __name__ == "__main__":
    app.run()