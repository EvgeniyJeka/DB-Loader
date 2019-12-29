# DB-Loader v1.0
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
http://*domain name*/*action*/*action type*

<img src="https://github.com/EvgeniyJeka/DB-Loader/blob/master/tests/samples/xlx_sending_sample.jpg" alt="Screenshot" width="600" />

Sample POSTMAN requests can be found in "tests/samples" folder.

# Actions - data upload and download. 
Data can be uploaded to SQL DB in several ways. Also the service 
is able to provide SQL table content as JSON.

1. "Add file" - used to upload files. 
Method: POST
Example: http://127.0.0.1:5000/add_file/create

Response on success: 
  		
    {
    "response": "DB was successfully updated"
     }			
	

2. "Add JSON" - used to upload data in JSON. 
Method:POST
Example: http://127.0.0.1:5000/add_json/create 

The provided JSON object must be a list of objects.
Each object in the list must be composed of simple "key" -"value" pairs,
so it can be parsed and placed in SQL table. 

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
	
Response on success: 
  		
    {
    "response": "DB was successfully updated"
     }		


3. "Table to JSON" - used to get SQL table content as JSON.
Table name must be added after the action name.

Method: GET
Example: http://127.0.0.1:5000/table_to_json/cities

Response on success - table content in JSON:

<img src="https://github.com/EvgeniyJeka/DB-Loader/blob/master/tests/samples/table_to_json_sample.jpg" alt="Screenshot" width="600" />


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

1. Enter the credentials to your MySQL DB to "config.ini" file - 
user must have sufficient permissions to create, read, update and delete 
tables.

2. Unless the service is running locally, enter the URL with hosting 
domain to "config.ini" file.

3. Run the file "Gateway.py"  to activate the service.  

# Tests

Automated API tests are placed in "tests" folder.
The tests cover all major user flows plus negative testing.
The tests are written in Python, PyTest framework is used. 

# Design and general flow:
1. The request is received by Gateway and parsed by one of the methods. The 
received file is saved. Gateway calls for Core instance to handle the request, 
passes it's content(if applicable), "action", "action type" and received 
file name and path(if applicable).

2. One of the Core methods is called, it opens the received file, 
reads it's content and passes it to Executer instance after 
it passes validation.

3. Executer is responsible for integration with MySQL DB.
The requested update is performed in the DB. If it fails because of
user input a relevant error message is provided to the user in response 
(as JSON).



  



