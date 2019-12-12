import flask
from flask import Flask, render_template
from flask import request
from Core import Core
import csv

app = Flask(__name__)


core = Core()


@app.route('/index')
def index():

    return render_template("verticalAccordion.html")

@app.route('/txt_file', methods = ['POST'])
def receive_txt():

    data = request.files['file']
    a = str(data.read(),'utf-8')
    print(a)
    return data.filename

@app.route('/add_csv_file', methods = ['POST'])
def receive_csv():
    data = request.files['file']

    # Verify csv extension
    file_extension = data.filename.split('.')[1]
    print(f"Log: file with extension {file_extension} was received")
    if not file_extension == 'csv':
        print(f"Log: Error - files with extension {file_extension} aren't processed by this method.")
        return f"Log: Error - files with extension {file_extension} aren't processed by this method."

    body_content = str(data.read(), 'utf-8')
    result = core.add_csv(body_content, data.filename)

    return result

@app.route('/add_json', methods = ['POST'])
def receive_json():
    pass






if __name__ == "__main__":
    app.run()