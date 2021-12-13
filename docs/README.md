# graphr docs
v0.1

## DATABASE
- Neo4j Aura
### NODES
#### EMPLOYEE
- Label: ```Employee```
- Attributes: ```surname```, ```name```, ```position```,  ```skills```, ```note```

#### DEPARTMENT
- Label: ```Department```
- Attributes: ```name```, ```description```

### RELATIONSHIPS
- ```WORKS_IN``` - no attributes yet
- ```DIRECTS``` - no attributes yet

## APPLICATION

### LANGUAGE
- Python 3.9+
### FRAMEWORK
- Flask 2.x
### NOTES
- the app takes the data necessary for the connection from the environment, the data can also be parsed as arguments upon starting.
### VIEWS
Each view has its corresponding methods in the NeoClient class object. The NeoClient class object is a wrapper for queries into the NEO4j database. See ```neo.py```  
Each corresponding query has its own internal method which gets executed by the driver. There is some basic error handling to ensure the app won't crash.  
The Flask framework uses Jinja templating system to render each corresponding page. Jinja is used for conditional rendering in the very templates.  