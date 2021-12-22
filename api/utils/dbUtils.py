import os
import psycopg2

class DbUtils:
    
    """
    Class to interact into database for creating hive metastore
    """
    def __init__(self, message=None):
        """
        Response constructor with defaults
        :param message: Optional init message for the response
        """
        

    def createMetastoreDB(self, workspaceName: str):
        self.connection = psycopg2.connect(user=os.environ.get("POSTGRES_DB_USERNAME"), password = os.environ.get("POSTGRES_DB_PASSWORD"), host = os.environ.get("POSTGRES_DB_HOST"), port = os.environ.get("POSTGRES_DB_PORT"))
        self.connection.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        self.cursor = self.connection.cursor()
        self.cursor.execute(f"CREATE DATABASE {workspaceName}_metastore;")
        self.database = (f"{workspaceName}_metastore")

    def metastoreSchema(self):
        self.connection = psycopg2.connect(dbname = self.database,user=os.environ.get("POSTGRES_DB_USERNAME"), password = os.environ.get("POSTGRES_DB_PASSWORD"), host = os.environ.get("POSTGRES_DB_HOST"), port = os.environ.get("POSTGRES_DB_PORT"))
        self.connection.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        self.cursor = self.connection.cursor()
        self.cursor.execute(open("utils/schema/hive-schema-2.3.0.postgres.sql", "r").read())
            
