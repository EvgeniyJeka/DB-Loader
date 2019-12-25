# DB-Loader
Web Service that receives data and loads it to SQL DB.
Also the service is able to return the content of SQL table as JSON.

Data that is needed to be saved can be provided as a file or 
as JSON object.

A POST request is sent to the service, the request is parsed
and its content is added to SQL DB.

Supported file extensions: CSV, XLSX, XLS.

# Expected request form.
To upload data to SQL server POST request must be used.
Uploaded file must be attached to request body.
If the uploaded data is JSON it must be contained in request body. 

The expected request URL must have the following structure:
http://<domain name>/<action>/<action type>

# Actions - data upload and download. 
Data can be uploaded to SQL DB in several ways. Also the service 
is able to provide SQL table content as JSON.

1. "Add file" - used to upload files. 
Method: POST
Example: http://127.0.0.1:5000/add_file/create

Response on success:
Response on failure:

2. "Add JSON" - used to upload data in JSON. 
Method:POST
Example: http://127.0.0.1:5000/add_json/create 

Expected JSON structure:


	
	"workers":[
		
		{
		
		"name":"Anna",
		"ID":351,
		"title":"Designer"
			
		},
		
		{
		"name":"John",
		"ID":293,
		"title":"Front-End Developer"
		}			
	]


3. "Table to JSON" - used to get SQL table content as JSON.
Table name must be added after the action name.

Method: GET
Example: http://127.0.0.1:5000/table_to_json/cities



# Action types
Several action types are supported.

1. "Create" - create a new table in SQL DB with the requested name 
and save the provided data.

2. "Overwrite" - overwrite an existing table if a table with such name 
already exists (otherwise a new table is created). Can be used to update
the SQL table after changes were made in CSV/XLSX/XLS file.

3. "Add data" - add additional row or column to an existing table.
Only the added content must be sent. To make a correction in a table that 
was previously uploaded it is better to use the "Overwrite" action type.


# How To

# Tests


