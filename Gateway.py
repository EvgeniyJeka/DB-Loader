from flask import Flask
from flask import request
from Core import Core


app = Flask(__name__)

core = Core()


@app.route("/add_file/<action_type>", methods=['POST'])
def receive_file(action_type):
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
        result = core.add_xlsx(file.filename, action_type)
        return result

    elif file_extension == 'csv':
        result = core.add_csv(file.filename, action_type)
        return result

    return {"error": "File extension must be CSV, XLS or XLSX."}


@app.route('/add_json/<action_type>', methods=['POST'])
def receive_json(action_type):
    """
    Receiving request that contains JSON. It's content is added to DB.
    In this method  API request is processed, it's body is parsed and the content is passed to "add_json" method
    of Core class. If there is a table which name is identical to received file name, table content is
    appended to existing table. Otherwise a new table is created.

    :return: JSON - confirmation on success, error message otherwise.
    """
    data = request.get_json()
    result = core.add_json(data, action_type)

    if result:
        return result

    else:
        return {"error": "The requested operation has failed."}


@app.route('/table_to_json/<table_name>', methods=['GET'])
def table_to_json(table_name):
    """
    This method is used to get the content of SQL table as JSON.
    :param table_name: String
    :return: Table content as JSON
    """
    if table_name:
        return core.table_as_json(table_name)

    else:
        return {"error": "Must enter valid table name."}


if __name__ == "__main__":
    app.run()
