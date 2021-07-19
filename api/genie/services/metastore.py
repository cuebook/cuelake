from typing import List
import psycopg2 as pg
import psycopg2.extras
from django.conf import settings
from utils.apiResponse import ApiResponse


class Metastore:

    def __init__(self):
        self.connection = pg.connect(
            user=settings.METASORE_POSTGRES_USERNAME, 
            password=settings.METASORE_POSTGRES_PASSWORD, 
            host=settings.METASTORE_POSTGRES_HOST, 
            port=settings.METASORE_POSTGRES_PORT, 
            database=settings.METASORE_POSTGRES_DATABASE
        )

    def getTables(self):
        res = ApiResponse(message="Error retrieving tables")
        tableSQL = """
            SELECT 
                "TBLS"."TBL_ID" as "id", 
                "TBLS"."TBL_NAME" as "table", 
                "TBLS"."TBL_TYPE" as "type", 
                "DBS"."NAME" as "database",
				"size"."PARAM_VALUE" as "size",
				"last_updated"."PARAM_VALUE" as "last_updated"
            FROM "TBLS" 
            LEFT JOIN "DBS" ON "TBLS"."DB_ID" = "DBS"."DB_ID"
			LEFT JOIN "TABLE_PARAMS" as "size" ON "TBLS"."TBL_ID" = "size"."TBL_ID" AND "size"."PARAM_KEY" = 'totalSize'
			LEFT JOIN "TABLE_PARAMS" as "last_updated" ON "TBLS"."TBL_ID" = "last_updated"."TBL_ID" AND "last_updated"."PARAM_KEY" = 'transient_lastDdlTime'
            """
        response = self.executeSQL(tableSQL)
        tablesData = self.__convertTablesToTreeStructure(response)
        res.update(True, "Tables retrieved successfully", tablesData)
        return res

    def getColumns(self, tableId: int):
        res = ApiResponse(message="Error retrieving columns")
        columnSQL = f"""
            SELECT "CD_ID" as "tableId", "COLUMN_NAME" as "name", "TYPE_NAME" as "type" FROM "COLUMNS_V2" WHERE "CD_ID"={tableId}
        """
        response = self.executeSQL(columnSQL)
        res.update(True, "Columns retrieved successfully", response)
        return res

    def executeSQL(self, sql: str):
        cur = self.connection.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
        cur.execute(sql)
        response = cur.fetchall()
        cur.close()
        return response

    def __convertTablesToTreeStructure(self, tables: List):
        treeStructure = {}
        for table in tables:
            if table["database"] not in treeStructure:
                treeStructure[table["database"]] = {"views": [], "tables": []}
            if table["type"] == "VIRTUAL_VIEW":
                treeStructure[table["database"]]["views"].append(table)
            else:
                treeStructure[table["database"]]["tables"].append(table)
        return treeStructure