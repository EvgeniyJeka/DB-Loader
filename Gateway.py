import flask
from flask import Flask, render_template
from flask import request
from Core import Core
import csv

app = Flask(__name__)


core = Core()



@app.route("/add_csv_file", methods = ['POST'])
def receive_csv():
    """
    Receiving CSV files adding their content to DB.
    In this method  API request is processed, it's body is parsed and the content is passed to "add_csv" method
    of Core class. If there is a table which name is identical to received file name, table content is
    appended to existing table. Otherwise a new table is created.

    :return:
    """
    data = request.files['file']

    # Verify csv extension
    file_extension = data.filename.split('.')[1]
    print(f"Log: file with extension {file_extension} was received")
    if not file_extension == 'csv':
        print(f"Log: Error - files with extension {file_extension} aren't processed by this method.")
        return f"Log: Error - files with extension {file_extension} aren't processed by this method."

    # Use "add_csv" method from the Core class to add the content of the received file to DB
    body_content = str(data.read(), 'utf-8')
    result = core.add_csv(body_content, data.filename)

    return result

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