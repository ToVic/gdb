''' database connection object '''

from datetime import datetime
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

    @staticmethod
    def get_date(month: bool=False) -> str:
        ''' helper method for datetime '''
        format = '%Y-%m-%d' if not month else '%m'

        return datetime.now().strftime(format)


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
        try:
            result = tx.run(query, name=name, id=id, description=description)
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
                data = row.data()
                dept = data['d']
                director = data['e']
                dept['director'] = director
                depts.append(dept)
            
            for dept in depts:
                logger.critical(dept)
            return depts


    def _get_all_depts(self, tx) -> list:
        query = (
            "MATCH (d:Department)"
            "OPTIONAL MATCH (d:Department)<-[r:DIRECTS]-(e:Employee)"
            "RETURN d, e"
        )
        try:
            result = tx.run(query)
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

            projects = []

            for row in r:
                data = row.data()
                dept = data['d']
                projects.append(data['p'])
            
            dept['projects'] = projects
            
            return dept


    def _get_dept(self, tx, name: str):
        query = (
            '''
            MATCH (d:Department {name: $name})
            OPTIONAL MATCH (d)-[:OWNS]->(p:Project)
            RETURN d, p
            '''
        )
        try:
            result = tx.run(query, name=name)
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
            OPTIONAL MATCH (d:Department {name: $name})<-[r]-()
            DELETE r
            DELETE d
            '''
        )
        try:
            result = tx.run(query, name=name)
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
        try:
            result = tx.run(query, name=name, new_name=new_name, new_description=new_description)
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
        assigned = self.get_date()
        #stupid fckng neo4j driver syntax shenanigans
        if position=='director':
            query = (
                '''
                CREATE (e:Employee {name: $name, surname: $surname, position: $position, skills: $skills, note: $note, id:$id, started: $assigned})
                WITH e
                MATCH (d:Department {name: $department})
                MERGE (e)-[r:DIRECTS]->(d)
                WITH e, r
                SET r.assigned = date($assigned)
                RETURN e
                '''
            )
        else:
             query = (
                '''
                CREATE (e:Employee {name: $name, surname: $surname, position: $position, skills: $skills, note: $note, id:$id, started: $assigned})
                WITH e
                MATCH (d:Department {name: $department})
                MERGE (e)-[r:WORKS_IN]->(d)
                WITH e, r
                SET r.assigned = date($assigned)
                RETURN e
                '''
            )
        try:
            result = tx.run(query,
                        name=name, 
                        surname=surname,
                        position=position,
                        department=department,
                        skills=skills,
                        note=note,
                        id=id,
                        assigned=assigned)
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
        project = employee['project']

        with self.driver.session() as session:
            r = session.write_transaction(
                self._edit_employee,
                id=id, surname=surname, name=name, position=position, department=department, skills=skills, note=note, projname=project
            )
        if not r:
            logger.critical('Department editing failed miserably.')
            return False

        return True


    def _edit_employee(self, tx, id: str, surname: str, name: str, position: str, department: str, skills: str, note: str, projname: str):
        assigned = self.get_date()
        if position == 'director':
            query = (
                '''
                MATCH (e:Employee {id: $id})
                SET e += {name: $name, surname: $surname, position: $position, skills: $skills, note: $note, id:$id}
                WITH e
                OPTIONAL MATCH (e)-[r]-(:Department)
                DELETE r
                WITH e
                MATCH (dd:Department {name: $department})
                CREATE (e)-[rr:DIRECTS]->(dd)
                WITH e, rr
                SET rr.assigned = date($assigned)
                WITH e
                MATCH (p:Project {name: $projname})
                CREATE (e)-[a:ASSIGNED_TO]->(p)
                WITH e
                RETURN e
                '''
            )
        else:
            query = (
                '''
                MATCH (e:Employee {id: $id})
                SET e += {name: $name, surname: $surname, position: $position, skills: $skills, note: $note, id:$id}
                WITH e
                OPTIONAL MATCH (e)-[r]-(:Department)
                DELETE r
                WITH e
                MATCH (dd:Department {name: $department})
                CREATE (e)-[rr:WORKS_IN]->(dd)
                WITH e, rr
                SET rr.assigned = date($assigned)
                WITH e
                MATCH (p:Project {name: $projname})
                CREATE (e)-[a:ASSIGNED_TO]->(p)
                WITH e
                RETURN e
                '''
            )
        try:
            result = tx.run(query,
                            name=name, 
                            surname=surname,
                            position=position,
                            department=department,
                            skills=skills,
                            note=note,
                            id=id,
                            assigned=assigned,
                            projname=projname)
            return [record for record in result]
        except Exception as e:
            logger.critical('Failed to execute a query; %s, exception: %s', type(self).__name__, e)


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
                department = data.get('d')
                employee['department'] = department['name'] if department else 'N/A'
                employee['assigned'] = data.get('assigned', 'N/A')
                employee['project_id'] = data.get('pid', 'N/A')
                employee['project'] = data.get('pname', 'N/A')

            logger.critical(r)
            logger.critical(employee)
            return employee


    def _get_employee(self, tx, id: str):
        query = (
            '''
            MATCH (e:Employee {id: $id})
            OPTIONAL MATCH (e)-[r]->(d:Department)
            OPTIONAL MATCH (e)-[r]->(p:Project)
            RETURN e, r.assigned AS assigned, d, p.id AS pid, p.name as pname
            '''
        )
        try:
            result = tx.run(query, id=id)
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
            MATCH (e:Employee {id: $id})
            OPTIONAL MATCH (e:Employee {id: $id})-[r]-()
            DELETE r
            DELETE e
            '''
        )
        try:
            result = tx.run(query, id=id)
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
                department = data.get('d')
                project = data.get('p')
                employee['department'] = department['name'] if department else 'N/A'
                employee['project_id'] = project.get('id') if project else ''
                employee['project_name'] = project.get('name') if project else ''
                employees.append(employee)
            
            return employees


    def _get_all_employees(self, tx):
        query = (
            "MATCH (e:Employee)"
            "OPTIONAL MATCH (e)-->(d:Department)"
            "OPTIONAL MATCH (e)-->(p:Project)"
            "RETURN e, d, p"
        )
        try:
            result = tx.run(query)
            return [record for record in result]
        except Exception as e:
            logger.critical('Failed to execute a query; %s, exception: %s', type(self).__name__, e)

    
    def get_aggregates(self):
        ''' get aggregate stats for structure overview page '''
        with self.driver.session() as session:
            r = session.read_transaction(
                self._get_aggregates
            )
            rr = session.read_transaction(
                self._get_monthly_newbies
            )
            if not r or not rr:
                logger.critical('Employees overview lookup failed miserably.')
                return

            data = r[0].data()
            data['newbies'] = rr[0].data().get('rr', 999)
            data['terminated'] = 4 #TODO
            
            return data


    def _get_aggregates(self, tx):
        query = (
            '''
            MATCH (e:Employee), (d:Department), ()-[r:DIRECTS]-()
            RETURN count(DISTINCT e) as emp, count(DISTINCT d) as dep, count(DISTINCT r) as dir
            '''
        )
        try:
            result = tx.run(query)
            return [record for record in result]
        except Exception as e:
            logger.critical('Failed to execute a query; %s, exception: %s', type(self).__name__, e)

    
    def _get_monthly_newbies(self, tx):
        month = self.get_date(month=True)
        query = (
            '''
            MATCH (e:Employee)
            WITH  split(e.started,'-')[1] AS m, e
            WHERE m = $month
            return count(e) as rr
            '''
        )
        try:
            result = tx.run(query, month=month)
            return [record for record in result]
        except Exception as e:
            logger.critical('Failed to execute a query; %s, exception: %s', type(self).__name__, e)

### PROJECTS

    def create_project(self, proj: dict):
            ''' create department driver interaction '''
            name = proj.get('name')
            client = proj.get('client')
            description = proj.get('description')
            dept = proj.get('department')
            with self.driver.session() as session:
                r = session.write_transaction(
                    self._create_project, name, client, description, dept
                )
                if not r:
                    logger.critical('Project creation failed miserably.')
                    return False

            return True

        
    def _create_project(self, tx, name: str, client: str, description: str, dept: str):
        id = self.new_id(4)
        since = self.get_date()
        query = (
            '''
            CREATE (p:Project {name: $name, id: $id, description: $description, client: $client})
            WITH p
            MATCH (d:Department {name: $dept})
            WITH p, d
            CREATE (p)<-[:OWNS {since: $since}]-(d)
            RETURN p
            '''
        )
        try:
            result = tx.run(query, name=name, id=id, description=description, client=client, dept=dept, since=since)
            logger.info('Created project %s, id: %s', name, id)
            return result

        except Exception as e:
            logger.critical('Failed to execute a query; %s, exception: %s', type(self).__name__, e)

    
    def get_all_projects(self):
        ''' get a list of all departments '''

        projects = []
        with self.driver.session() as session:
            r = session.read_transaction(
                self._get_all_projects
            )
            if not r:
                logger.critical('Projects overview lookup failed miserably.')
                return 
            for row in r:
                data = row.data()
                project = data.get('p')
                owner = data.get('d')
                project['dept'] = owner
                projects.append(project)
            
            return projects

    def _get_all_projects(self, tx):
        query = (
            "MATCH (p:Project)"
            "OPTIONAL MATCH (p:Project)<-[:OWNS]-(d:Department)"
            "RETURN p, d"
        )
        try:
            result = tx.run(query)
            return [record for record in result]
        except Exception as e:
            logger.critical('Failed to execute a query; %s, exception: %s', type(self).__name__, e)


    def delete_project(self, id: str):
        '''
        project deletion
        '''
        with self.driver.session() as session:
            r = session.write_transaction(
                self._delete_project,
                id=id
            )
            if not r:
                logger.critical('Employee deletion failed miserably')
                return False
            return True


    def _delete_project(self, tx, id:str):
        query = (
            '''
            MATCH (p:Project {id: $id})
            OPTIONAL MATCH (p:Project {id: $id})-[r]-()
            DELETE r
            DELETE p
            '''
        )
        try:
            result = tx.run(query, id=id)
            return result
        except Exception as e:
            logger.critical('Failed to execute a query; %s, exception: %s', type(self).__name__, e)


    def get_project(self, id: str):
            '''returns project details'''
            with self.driver.session() as session:
                r = session.read_transaction(
                    self._get_project,
                    id
                )
                if not r:
                    logger.critical('Project overview lookup failed miserably OR no projects present..')
                    return 
                logger.critical(r)
                for row in r:
                    data = row.data()
                    project = data['p']
                    department = data.get('d')
                    employees = data.get('e')
                    project['department'] = department['name'] if department else 'N/A'
                    project['since'] = data.get('since', 'N/A')
                    project['employees'] = employees

                logger.critical(project)
                return project


    def _get_project(self, tx, id: str):
        query = (
            '''
            MATCH (p:Project {id: $id})
            OPTIONAL MATCH (p:Project {id: $id})<-[r:OWNS]-(d:Department)
            OPTIONAL MATCH (p:Project {id: $id})<-[:ASSIGNED_TO]-(e:Employee)
            return p, d, e, r.since AS since
            '''
        )
        try:
            result = tx.run(query, id=id)
            return [record for record in result]
        except Exception as e:
            logger.critical('Failed to execute a query; %s, exception: %s', type(self).__name__, e)