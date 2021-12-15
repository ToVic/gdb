# graphr docs
v0.1
## LANGUAGE
- Python 3.9+
## FRAMEWORK
- Flask 2.x
## DATABASE
- Neo4j Aura
- you need to have the credentials stored in the env, use ```graphr -h``` for detail
## MODELS
### NODES
#### EMPLOYEE
- Label: ```Employee```
- Attributes: ```surname```, ```name```, ```position```,  ```skills```, ```note``` - strings; ```started``` - date
- all CRUD operations

#### DEPARTMENT
- Label: ```Department```
- Attributes: ```name```, ```description```
- all CRUD operations

### RELATIONSHIPS
- ```WORKS_IN``` - ```assigned``` - date (using the Cypher built-in ```date()``` function)
- ```DIRECTS``` - ```assigned``` - date

## APPLICATION
### NOTES
- the app takes the data necessary for the connection from the environment, the data can also be parsed as arguments upon starting.
### VIEWS
Each view has its corresponding methods in the NeoClient class object. The NeoClient class object is a wrapper for queries into the NEO4j database. See ```neo.py```  
Each corresponding query has its own internal method which gets executed by the driver. There is some basic error handling to ensure the app won't crash.  
The Flask framework uses Jinja templating system to render each corresponding page. Jinja is used for conditional rendering right in the templates.  
The forms implementation leverage the ```wtforms``` flask extension library. Due to its cumbersome architecture, the forms that are to be pre-filled with default data (while editing) need to be initialized right in the views. This is one of the design mistakes of this app.
### SERVER
The server is powered by ```gevent``` library which offers an easy and reliable setup for a WSGI server.
### CYPHER QUERIES
- the app leverages basic syntax while securing the CRUD operations on the Neo4j backend
- see ```neo.py```, the code is partially self-documented and the queries are visible nicely
- the longer ```_edit``` queries are not optimized  
**essential: optional matches**  
The application will not allow creation of an employee without assigning the employee to a department.
However, there are some workflows that can break this rule, typically upon deleting a department:
```
match department --> delete all department relationships --> delete department
```
The use of optional matches ensures that even department without any employees, and vice versa, get manipulated properly.  
**time-related queries**  
Due to some issues while trying to make the datetime supporting methods work, there is an 'engineered' string-manipulating, hacky solution for the query responsible for calculating the newbies coming in this month. See ```neo.py```, line 465 and further.
