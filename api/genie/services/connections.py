from genie.models import Connection, ConnectionType, ConnectionParam, ConnectionParamValue
from genie.serializers import ConnectionSerializer, ConnectionDetailSerializer, ConnectionTypeSerializer
from utils.apiResponse import ApiResponse

class Connections:

    @staticmethod
    def getConnections(workspaceId):
        res = ApiResponse()
        connections = Connection.objects.filter(workspace=workspaceId)
        serializer = ConnectionSerializer(connections, many=True)
        res.update(True, "Connections retrieved successfully", serializer.data)
        return res

    @staticmethod
    def getConnection(connection_id):
        res = ApiResponse()
        connections = Connection.objects.get(id=connection_id)
        serializer = ConnectionDetailSerializer(connections)
        res.update(True, "Connection retrieved successfully", serializer.data)
        return res

    @staticmethod
    def addConnection(payload, workspaceId):
        res = ApiResponse()
        connectionType = ConnectionType.objects.get(id=payload["connectionType_id"])
        connection = Connection.objects.create(
            name=payload["name"], description=payload["description"], connectionType=connectionType, workspace_id = workspaceId
        )
        for param in payload["params"]:
            cp = ConnectionParam.objects.get(name=param, connectionType=connectionType)
            ConnectionParamValue.objects.create(
                connectionParam=cp, value=payload["params"][param], connection=connection
            )
        res.update(True, "Connection added successfully")
        return res

    @staticmethod
    def removeConnection(connection_id):
        res = ApiResponse()
        connection = Connection.objects.get(id=connection_id)
        if connection.notebookobject_set.count() == 0:
            Connection.objects.get(id=connection_id).delete()
            res.update(True, "Connection deleted successfully")
        else:
            res.update(False, "Cannot delete connection because of dependent notebook")
        return res

    @staticmethod
    def updateConnection(connection_id, payload):
        res = ApiResponse()
        Connection.objects.filter(id=connection_id).update(
            name=payload.get("name", ""),
            description=payload.get("description", ""),
            connectionType=ConnectionType.objects.get(id=payload["connectionType_id"]),
        )
        connection = Connection.objects.get(id=connection_id)
        # TODO: delete params related to this & then update
        for param in payload["params"]:
            cp = ConnectionParam.objects.get(id=param["paramId"])
            # if cp.isEncrypted:
            #     encryptionObject= AESCipher()
            #     param['paramValue'] = encryptionObject.encrypt(param['paramValue'])
            ConnectionParamValue.objects.create(
                connectionParam=cp, value=param["paramValue"], connection=connection
            )

        res.update(True, "Connection updated successfully")
        return res

    @staticmethod
    def getConnectionTypes():
        res = ApiResponse()
        connectionTypes = ConnectionType.objects.all()
        serializer = ConnectionTypeSerializer(connectionTypes, many=True)
        res.update(True, "Successfully retrieved connection types", serializer.data)
        return res

