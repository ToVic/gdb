''' database connection object '''

from secrets import randbelow
from argparse import PARSER
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
        id = self.new_id()
        description = dept.get('description')
        with self.driver.session() as session:
            r = session.write_transaction(
                self._create_and_return_dept, name, id, description
            )
            if not r:
                logger.critical('Department creation failed miserably.')
                return False

        logger.info('Created department %s with id %s', name, id)
        return True

    
    def _create_and_return_dept(self, tx, name: str, id: str, description: str):
        ''' create department query '''
        query = (
            '''
            CREATE (d:Department {name: $name, id: $id, description: $description})
            RETURN d
            '''
        )
        result = tx.run(query, name=name, id=id, description=description)
        try: 
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


    def get_dept(self, tx):
        ''' get details of a particular department '''
        pass


    def edit_dept(self):
        ''' edits department details '''
        pass


    def delete_dept(self):
        ''' 
        deletes an entire department
        UNSAFE
        '''
        pass


    def create_employee(self):
        ''' creates a new employee '''
        pass


    def edit_employee(self):
        ''' edits employee details '''
        pass


    def edit_employee_dept(self):
        ''' changes the employee relation vertex '''
        pass


    def get_employee(self):
        '''returns employee details'''
        pass
