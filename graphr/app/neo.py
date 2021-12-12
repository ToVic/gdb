''' database connection object '''

from secrets import randbelow
from neo4j import GraphDatabase
from graphr.logger import logger
from graphr.argparser import Pars

NEO_URI = Pars.neo_uri
NEO_LOGIN = Pars.neo_login
NEO_PASSWORD = Pars.neo_password

class Neo_client:
    def __init__(self):
        self.driver = GraphDatabase.driver(uri=NEO_URI, auth=(NEO_LOGIN, NEO_PASSWORD))

    def close(self):
        self.driver.close()
    
    @staticmethod
    def new_id(length: int=3) -> str:
        ''' returns a pseudo-random ID '''
        id = ''
        for _ in range(length):
            num = str(randbelow(10))
            id = id+num
        
        return id


    def create_dept(self, dept: dict):
        ''' create department driver interaction '''
        name = dept.get('name')
        description = dept.get('description')
        with self.driver.session() as session:
            r = session.write_transaction(
                self._create_and_return_dept, name, description
            )
            if not r:
                logger.critical('Department creation failed miserably.')
                return False

        return True

    
    def _create_and_return_dept(self, tx, name: str, description: str):
        ''' create department query '''
        id = self.new_id()
        query = (
            '''
            CREATE (d:Department {name: $name, id: $id, description: $description})
            RETURN d
            '''
        )
        result = tx.run(query, name=name, id=id, description=description)
        try:
            logger.info('Created department %s, id: %s', name, id)
            return result

        except Exception as e:
            logger.critical('Failed to execute a query; %s, exception: %s', type(self).__name__, e)

    
    def get_all_depts(self):
        ''' get a list of all departments '''
        depts = []
        with self.driver.session() as session:
            r = session.read_transaction(
                self._get_all_depts
            )
            if not r:
                logger.critical('Departments overview lookup failed miserably.')
                return "internal server error"
            for row in r:
                dept = {}
                dept['name'] = row['d']['name']
                dept['description'] = row['d']['description']
                depts.append(dept)
            
            return depts


    def _get_all_depts(self, tx) -> list:
        query = (
            "MATCH (d:Department)"
            "RETURN d"
        )
        result = tx.run(query)
        try:
            return [record for record in result]
        except Exception as e:
            logger.critical('Failed to execute a query; %s, exception: %s', type(self).__name__, e)


    def get_dept(self, name: str):
        ''' get details of a particular department '''
        with self.driver.session() as session:
            r = session.read_transaction(
                self._get_dept,
                name
            )
            if not r:
                logger.critical('Department detail lookup failed miserably.')
                return 

            for row in r:
                data = row.data()['d']
                logger.critical(data)
                
            return data


    def _get_dept(self, tx, name: str):
        query = (
            '''MATCH (d:Department {name: $name})
            RETURN d'''
        )
        result = tx.run(query, name=name)
        try:
            return [record for record in result]
        except Exception as e:
            logger.critical('Failed to execute a query; %s, exception: %s', type(self).__name__, e)


    def delete_dept(self, name):
        '''
        department deletion
        '''
        with self.driver.session() as session:
            r = session.write_transaction(
                self._delete_dept,
                name
            )
            if not r:
                logger.critical('Department deletion failed miserably')
                return False
            return True


    def _delete_dept(self, tx, name: str):
        query = (
            '''
            MATCH (d:Department {name: $name})
            DELETE d
            '''
        )
        result = tx.run(query, name=name)
        try:
            return result
        except Exception as e:
            logger.critical('Failed to execute a query; %s, exception: %s', type(self).__name__, e)


    def edit_dept(self, dept, name):
        ''' edits department details '''

        new_name = dept['name']
        new_description = dept['description']
        with self.driver.session() as session:
            r = session.write_transaction(
                self._edit_dept,
                name, new_name, new_description
            )
        if not r:
            logger.critical('Department editing failed miserably.')
            return False

        return True


    def _edit_dept(self, tx, name, new_name, new_description):
        query = (
            "MATCH (d:Department {name: $name})"
            "SET d += {name: $new_name, description: $new_description}"
            "RETURN d"
        )
        result = tx.run(query, name=name, new_name=new_name, new_description=new_description)
        try:
            return [record for record in result]
        except Exception as e:
            logger.critical('Failed to execute a query; %s, exception: %s', type(self).__name__, e)


    def add_employee(self, employee):
        ''' adds a new employee '''

        name = employee['name']
        surname = employee['surname']
        position = employee['position']
        department = employee['department']
        skills = employee['skills']
        note = employee['note']

        with self.driver.session() as session:
            r = session.write_transaction(
                self._add_employee,
                surname=surname, name=name, position=position, department=department, skills=skills, note=note
            )
        if not r:
            logger.critical('Employee addition failed miserably.')
            return False

        return True


    def _add_employee(self, tx, surname: str, name: str, position: str, department: str, skills: str, note: str):
        id = self.new_id(6)
        #stupid fckng neo4j driver syntax shenanigans
        if position=='director':
            query = (
                '''
                CREATE (e:Employee {name: $name, surname: $surname, position: $position, skills: $skills, note: $note, id:$id})
                WITH e
                MATCH (d:Department {name: $department})
                MERGE (e)-[:DIRECTS]->(d)
                RETURN e
                '''
            )
        else:
             query = (
                '''
                CREATE (e:Employee {name: $name, surname: $surname, position: $position, skills: $skills, note: $note, id:$id})
                WITH e
                MATCH (d:Department {name: $department})
                MERGE (e)-[:WORKS_IN]->(d)
                RETURN e
                '''
            )
        result = tx.run(query,
                        name=name, 
                        surname=surname,
                        position=position,
                        department=department,
                        skills=skills,
                        note=note,
                        id=id)
        try:
            return [record for record in result]
        except Exception as e:
            logger.critical('Failed to execute a query; %s, exception: %s', type(self).__name__, e)


    def edit_employee(self, id:str, employee: dict):
        ''' 
        edits employee details
        '''
        name = employee['name']
        surname = employee['surname']
        position = employee['position']
        department = employee['department']
        skills = employee['skills']
        note = employee['note']

        with self.driver.session() as session:
            r = session.write_transaction(
                self._edit_employee,
                id=id, surname=surname, name=name, position=position, department=department, skills=skills, note=note
            )
        if not r:
            logger.critical('Department editing failed miserably.')
            return False

        return True


    def _edit_employee(self, tx, id: str, surname: str, name: str, position: str, department: str, skills: str, note: str):
        if position == 'director':
            query = (
                '''
                MATCH (e:Employee {id: $id})-[r]-(d:Department)
                SET e += {name: $name, surname: $surname, position: $position, skills: $skills, note: $note, id:$id}
                DELETE r
                MERGE (e)-[:DIRECTS]->(d)
                RETURN e
                '''
            )
        else:
            query = (
                '''
                MATCH (e:Employee {id: $id})-[r]-(d:Department)
                SET e += {name: $name, surname: $surname, position: $position, skills: $skills, note: $note, id:$id}
                DELETE r
                MERGE (e)-[:WORKS_IN]->(d)
                RETURN e
                '''
            )

        result = tx.run(query,
                        name=name, 
                        surname=surname,
                        position=position,
                        department=department,
                        skills=skills,
                        note=note,
                        id=id)
        try:
            return [record for record in result]
        except Exception as e:
            logger.critical('Failed to execute a query; %s, exception: %s', type(self).__name__, e)
        pass


    def get_employee(self, id: str):
        '''returns employee details'''
        with self.driver.session() as session:
            r = session.read_transaction(
                self._get_employee,
                id
            )
            if not r:
                logger.critical('Employee overview lookup failed miserably OR no employees present..')
                return 
            logger.critical(r)
            for row in r:
                data = row.data()
                employee = data['e']
                department = data['d']
                employee['department'] = department['name'] or 'N/A'
            return employee


    def _get_employee(self, tx, id: str):
        query = (
            '''
            MATCH (e:Employee {id: $id})-[]->(d:Department)
            RETURN e, d
            '''
        )
        result = tx.run(query, id=id)
        try:
            return [record for record in result]
        except Exception as e:
            logger.critical('Failed to execute a query; %s, exception: %s', type(self).__name__, e)


    def delete_employee(self, id: str):
        '''
        employee deletion
        '''
        with self.driver.session() as session:
            r = session.write_transaction(
                self._delete_employee,
                id=id
            )
            if not r:
                logger.critical('Employee deletion failed miserably')
                return False
            return True


    def _delete_employee(self, tx, id:str):
        query = (
            '''
            MATCH (e:Employee {id: $id})-[r]-()
            DELETE r
            DELETE e
            '''
        )
        result = tx.run(query, id=id)
        try:
            return result
        except Exception as e:
            logger.critical('Failed to execute a query; %s, exception: %s', type(self).__name__, e)


    def get_all_employees(self):
        ''' returns all employees and their data '''
        employees = []
        with self.driver.session() as session:
            r = session.read_transaction(
                self._get_all_employees
            )
            if not r:
                logger.critical('Employees overview lookup failed miserably.')
                return "internal server error"
            for row in r:
                data = row.data()
                employee = data['e']
                department = data['d']
                employee['department'] = department['name'] or 'N/A'
                employees.append(employee)
            
            return employees


    def _get_all_employees(self, tx):
        query = (
            "MATCH (e:Employee)-[]->(d:Department)"
            "RETURN e, d"
        )
        result = tx.run(query)
        try:
            return [record for record in result]
        except Exception as e:
            logger.critical('Failed to execute a query; %s, exception: %s', type(self).__name__, e)
