import boto3
import psycopg2 as pg
import pandas as pd
from django.conf import settings
from utils.apiResponse import ApiResponse


SQL_ROWS_LIMIT = 50

class Postgres():
    """
    Class for a Postgres DB connection.
    """

    def __init__(self, params):
        """
        Constructor for the Postgres class.
        Initializes params and instantiates a connection.
        :param params: Contains params like Postgres host, port and credentials
        """
        try:
            username = params["username"]
            password = params["password"]
            host = params["host"]
            port = params["port"]
            database = params["database"]

            self.connection = pg.connect(
                user=username, password=password, host=host, port=port, database=database
            )

        except Exception as error:
            raise(error)
            pass
            # logger.error(str(error))


    def testConnection(self):
        """
        Tests connection and then closes it.
        """
        if self.connection:
            try:
                # logger.info("Testing and closing DB connection")
                self.connection.close()
                return True
            except (Exception) as error:
                # logger.error(str(error))
                return False
        else:
            return False

    def runQuery(self, query, isTable, limitResults: bool = True):
        """
        Run query and fetch data from connection with provided credentials and closes the connection.
        :param query: SQL query to be executed
        :param isTable: boolean if table
        :param limitResults: bool if want to limit results
        """
        if self.connection:
            dataframe = self.fetchData(query)
            dataframe = dataframe.fillna("")
            metaData = {}
            data = []
            if not isTable:
                dataframe = dataframe.melt(dataframe.columns[0])
                isXColumnTime, newDataframe = checkIfColumnIsTime(dataframe, dataframe.columns[0])
                if isXColumnTime:
                    dataframe = newDataframe
                metaData = self.getMetaDataForChart(dataframe, isXColumnTime)
            data = dataframe.to_dict("records")
            # logger.info("Closing DB connection")
            self.connection.close()
            return {"data": data, "metaData": metaData}
        else:
            # logger.info("DB connection inactive")
            return False

    def fetchData(self, query, limitResults: bool = True):
        """
        Fetch data for query from self.connection
        :param query: str
        :param limitResults: bool if true will limit results to SQL_ROWS_LIMIT
        """
        if self.connection:
            chunksize = SQL_ROWS_LIMIT if limitResults else None
            dataframe = pd.read_sql(query, self.connection, chunksize=chunksize)
            if limitResults:
                for df in dataframe:
                    return df
                    break
            else:
                return dataframe
        else:
            # logger.info("DB connection inactive")
            return

    def fetchCompleteData(self, query):
        """
        Run query and fetch data from connection with provided credentials and closes the connection.
        :param query: SQL query to be executed
        """
        if self.connection:
            try:
                dataframe = pd.read_sql(query, self.connection)
                return dataframe
            except Exception as error:
                # logger.error(str(error))
                return
        else:
            # logger.info("DB connection inactive")
            return




class Schemas:
    """ Class to get schemas of catalougues """

    @staticmethod
    def getSchemas():
        """ Gets schemas"""
        res = ApiResponse(message="Error retrieving schemas")
        connectionParams = {
            "host": settings.METASTORE_POSTGRES_HOST,
            "port": settings.METASORE_POSTGRES_PORT,
            "username": settings.METASORE_POSTGRES_USERNAME,
            "password": settings.METASORE_POSTGRES_PASSWORD,
            "database": settings.METASORE_POSTGRES_DATABASE}

        tableParamsQuery = 'SELECT * FROM public."TABLE_PARAMS" WHERE "PARAM_KEY" = \'transient_lastDdlTime\' OR "PARAM_KEY" = \'totalSize\' ORDER BY "TBL_ID" ASC, "PARAM_KEY" ASC '
        tableParamsDf = Postgres(connectionParams).fetchCompleteData(tableParamsQuery)
        tableParamsDf = tableParamsDf.pivot(columns='PARAM_KEY', index='TBL_ID', values='PARAM_VALUE')


        tablesQuery = 'SELECT "TBLS"."TBL_ID", "TBLS"."TBL_NAME", "TBLS"."TBL_TYPE", "TBLS"."VIEW_ORIGINAL_TEXT", "DBS"."NAME" FROM "TBLS" INNER JOIN "DBS" ON "TBLS"."DB_ID" = "DBS"."DB_ID"'
        tablesDf = Postgres(connectionParams).fetchCompleteData(tablesQuery)
        tablesDf = tablesDf.merge(tableParamsDf, how="left", on="TBL_ID")

        # getting & merging iceberg tables
        s3Df = pd.DataFrame(data=Schemas.getS3FileNames())
        s3Df.rename(columns={'Key': 'TBL_NAME', 'Size': 'totalSize'}, inplace=True)
        s3Df['NAME'] = "Iceberg Tables"
        tablesDf = tablesDf.append(s3Df, ignore_index=True)
        
        tablesDf = tablesDf.fillna(value="NULL")
        databasesDf = tablesDf.groupby("NAME").apply(lambda grp: grp.to_dict("records")).reset_index(name="tables")
        databasesDf.columns = ["database", "tables"]

        columnsQuery = 'SELECT "CD_ID", "COLUMN_NAME", "TYPE_NAME" FROM "COLUMNS_V2"'
        columnsDf = Postgres(connectionParams).fetchCompleteData(columnsQuery)
        columnsDf = columnsDf.groupby("CD_ID").apply(lambda grp: grp.to_dict("records")).reset_index(name="columns")
        columnsDf.set_index('CD_ID', inplace=True)


        data = {"databases": databasesDf.to_dict("records"), "columns": columnsDf.to_dict()["columns"]}
        res.update(True, "Schemas retrieved successfully", data)
        return res


    def getS3FileNames():
        """ S3 file names"""

        # s3 = boto3.client("s3")
        # response = s3.list_objects_v2(Bucket=settings.S3_BUCKET_NAME, Prefix=settings.HADOOP_S3_PREFIX, Delimiter="/")
        # contents: list = response['Contents']

        # for content in contents:
        #     if 'ETag' in content:
        #         del content['ETag']
        #     if 'StorageClass' in content:
        #         del content['StorageClass']
        #     if 'Owner' in content:
        #         del content['Owner']

        #     content['Key'] = content['Key'][len(S3_FILES_PREFIX):]

        contents = [{"Key": "Zones.csv", "LastModified": "2021-05-11T12:07:07Z", "Size": 2006}]
        return contents



