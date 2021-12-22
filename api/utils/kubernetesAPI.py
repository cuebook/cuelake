from utils.helperFunctions import helperFunctions
from utils.dbUtils import DbUtils
import os
from time import sleep
import time
import yaml
import logging
from django.conf import settings
from kubernetes import config, client
from workspace.models import (
    Workspace,
    WorkspaceConfig
)
from utils.safeDict import SafeDict
import random
import subprocess
from pathlib import Path

# Get an instance of a logger
logger = logging.getLogger(__name__)

ICEBERG = "iceberg"
DELTA = "delta"

class KubernetesAPI:
    """
    Functionalities around zeppelin APIs
    """
    if os.environ.get("ENVIRONMENT","") == "dev":
        config.load_kube_config()
    elif os.environ.get("ENVIRONMENT","") != "test":
        config.load_incluster_config()

    POD_NAMESPACE = os.environ.get("POD_NAMESPACE", "default")

    def getDriversCount(self):
        """
        Gets Driver and executors count
        """
        runningDrivers = 0
        runningExecutors = 0
        pendingDrivers = 0
        pendingExecutors = 0
        v1 = client.CoreV1Api()
        ret = v1.list_namespaced_pod(self.POD_NAMESPACE, watch=False)
        pods = ret.items
        pods_name = [pod.metadata.name for pod in pods]
        podLabels = [[pod.metadata.labels, pod.status.phase] for pod in pods] # list
        podStatus = [pod.status for pod in pods]

        for label in podLabels:
            if "interpreterSettingName" in label[0] and label[0]["interpreterSettingName"] == "spark" and label[1]=="Running":
                runningDrivers += 1
            
            if "interpreterSettingName" in label[0] and label[0]["interpreterSettingName"] == "spark" and label[1]=="Pending":
                pendingDrivers += 1
            if "spark-role" in label[0] and label[0]["spark-role"] == "executor" and label[1]=="Running":
                runningExecutors += 1
            
            if "spark-role" in label[0] and label[0]["spark-role"] == "executor" and label[1]=="Pending":
                pendingExecutors += 1
        data = {"runningDrivers":runningDrivers,
                "pendingDrivers":pendingDrivers,
                "runningExecutors":runningExecutors,
                "pendingExecutors":pendingExecutors
                }
        return data

    def addZeppelinServer(self, workspaceName: str, workspaceConfig: dict, isNew: bool = False):
        sparkConfigJSON = ""
        if isNew:
            try:
                db = DbUtils()
                db.createMetastoreDB(workspaceName)
                db.metastoreSchema()
            except:
                pass
        if(workspaceConfig['storage'] == "S3"):
            if(workspaceConfig['acidProvider'] == DELTA):
                sparkConfigJSON = """
                "AWS_ACCESS_KEY_ID": {
                    "name": "AWS_ACCESS_KEY_ID",
                    "value": "S3ACCESSKEY",
                    "type": "textarea"
                },
                "AWS_SECRET_ACCESS_KEY": {
                    "name": "AWS_SECRET_ACCESS_KEY",
                    "value": "S3SECRETKEY",
                    "type": "textarea"
                },
                "spark.sql.warehouse.dir":{
                    "name": "spark.sql.warehouse.dir",
                    "value": "WAREHOUSELOCATION",
                    "type": "textarea"
                },
                 "spark.sql.extensions":{
                    "name": "spark.sql.extensions",
                    "value": "io.delta.sql.DeltaSparkSessionExtension",
                    "type": "textarea"
                },
                 "spark.sql.catalog.spark_catalog":{
                    "name": "spark.sql.catalog.spark_catalog",
                    "value": "org.apache.spark.sql.delta.catalog.DeltaCatalog",
                    "type": "textarea"
                }
                """
                sparkConfigJSON = sparkConfigJSON.replace('S3ACCESSKEY', workspaceConfig['s3AccessKey']).replace('S3SECRETKEY', workspaceConfig['s3SecretKey']).replace('WAREHOUSELOCATION', workspaceConfig['warehouseLocation'])
            elif(workspaceConfig['acidProvider'] == ICEBERG):
                sparkConfigJSON = """"AWS_ACCESS_KEY_ID": {
                    "name": "AWS_ACCESS_KEY_ID",
                    "value": "S3ACCESSKEY",
                    "type": "textarea"
                },
                "AWS_SECRET_ACCESS_KEY": {
                    "name": "AWS_SECRET_ACCESS_KEY",
                    "value": "s3SecretKey",
                    "type": "textarea"
                },
                "spark.sql.warehouse.dir":{
                    "name": "spark.sql.warehouse.dir",
                    "value": "WAREHOUSELOCATION",
                    "type": "textarea"
                },
                 "spark.sql.extensions":{
                    "name": "spark.sql.extensions",
                    "value": "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtension",
                    "type": "textarea"
                },
                 "spark.sql.catalog.spark_catalog":{
                    "name": "spark.sql.catalog.spark_catalog",
                    "value": "org.apache.iceberg.spark.SparkSessionCatalog",
                    "type": "textarea"
                }
                """
                sparkConfigJSON = sparkConfigJSON.replace('S3ACCESSKEY', workspaceConfig['s3AccessKey']).replace('S3SECRETKEY', workspaceConfig['s3SecretKey']).replace('WAREHOUSELOCATION', workspaceConfig['warehouseLocation'])
        elif(workspaceConfig['storage'] == "AZFS"):
            if(workspaceConfig['acidProvider'] == DELTA):
                sparkConfigJSON = """"spark.hadoop.fs.azure.account.key.AZUREACCOUNT.blob.core.windows.net": {
                    "name": "spark.hadoop.fs.azure.account.key.AZUREACCOUNT.blob.core.windows.net",
                    "value": "AZUREKEY",
                    "type": "textarea"
                },
                "spark.sql.warehouse.dir":{
                    "name": "spark.sql.warehouse.dir",
                    "value": "WAREHOUSELOCATION",
                    "type": "textarea"
                },
                 "spark.sql.extensions":{
                    "name": "spark.sql.extensions",
                    "value": "io.delta.sql.DeltaSparkSessionExtension",
                    "type": "textarea"
                },
                 "spark.sql.catalog.spark_catalog":{
                    "name": "spark.sql.catalog.spark_catalog",
                    "value": "org.apache.spark.sql.delta.catalog.DeltaCatalog",
                    "type": "textarea"
                }
                """
                sparkConfigJSON = sparkConfigJSON.replace('AZUREKEY', workspaceConfig['azureKey']).replace('AZUREACCOUNT', workspaceConfig['azureAccount']).replace('WAREHOUSELOCATION', workspaceConfig['warehouseLocation'])
            elif(workspaceConfig['acidProvider'] == ICEBERG):
                sparkConfigJSON = """"spark.hadoop.fs.azure.account.key.AZUREACCOUNT.blob.core.windows.net": {
                    "name": "spark.hadoop.fs.azure.account.key.AZUREACCOUNT.blob.core.windows.net",
                    "value": "AZUREKEY",
                    "type": "textarea"
                },
                "spark.sql.warehouse.dir":{
                    "name": "spark.sql.warehouse.dir",
                    "value": "WAREHOUSELOCATION",
                    "type": "textarea"
                },
                  "spark.sql.extensions":{
                    "name": "spark.sql.extensions",
                    "value": "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtension",
                    "type": "textarea"
                },
                 "spark.sql.catalog.spark_catalog":{
                    "name": "spark.sql.catalog.spark_catalog",
                    "value": "org.apache.iceberg.spark.SparkSessionCatalog",
                    "type": "textarea"
                }
                """
                sparkConfigJSON = sparkConfigJSON.replace('AZUREKEY', workspaceConfig['azureKey']).replace('AZUREACCOUNT', workspaceConfig['azureAccount']).replace('WAREHOUSELOCATION', workspaceConfig['warehouseLocation'])
        elif(workspaceConfig['storage'] == "GS"):
            if(workspaceConfig['acidProvider'] == DELTA):
                sparkConfigJSON = """spark.kubernetes.driver.secrets.cuelake-bucket-key": {
                    "name": "spark.kubernetes.driver.secrets.cuelake-bucket-key",
                    "value": "GOOGLEKEY",
                    "type": "textarea"
                },
                "spark.sql.warehouse.dir":{
                    "name": "spark.sql.warehouse.dir",
                    "value": "WAREHOUSELOCATION",
                    "type": "textarea"
                },
                "spark.hadoop.fs.AbstractFileSystem.gs.impl":{
                    "name": "spark.hadoop.fs.AbstractFileSystem.gs.impl",
                    "value": "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFS",
                    "type": "textarea"
                },
                "spark.hadoop.google.cloud.auth.service.account.enable":{
                    "name": "spark.hadoop.google.cloud.auth.service.account.enable",
                    "value": "true",
                    "type": "textarea"
                },
                "spark.delta.logStore.gs.impl":{
                    "name": "spark.delta.logStore.gs.impl",
                    "value": "io.delta.storage.GCSLogStore",
                    "type": "textarea"
                },
                "spark.hadoop.fs.gs.impl":{
                    "name": "spark.hadoop.fs.gs.impl",
                    "value": "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFileSystem",
                    "type": "textarea"
                },
                "spark.sql.extensions":{
                    "name": "spark.sql.extensions",
                    "value": "io.delta.sql.DeltaSparkSessionExtension",
                    "type": "textarea"
                },
                 "spark.sql.catalog.spark_catalog":{
                    "name": "spark.sql.catalog.spark_catalog",
                    "value": "org.apache.spark.sql.delta.catalog.DeltaCatalog",
                    "type": "textarea"
                }
                """
                sparkConfigJSON = sparkConfigJSON.replace('GOOGLEKEY', workspaceConfig['googleKey']).replace('WAREHOUSELOCATION', workspaceConfig['warehouseLocation'])
            elif(workspaceConfig['acidProvider'] == ICEBERG):
                sparkConfigJSON = """spark.kubernetes.driver.secrets.cuelake-bucket-key": {
                    "name": "spark.kubernetes.driver.secrets.cuelake-bucket-key",
                    "value": "GOOGLEKEY",
                    "type": "textarea"
                },
                "spark.kubernetes.authenticate.driver.serviceAccountName": {
                    "name": "spark.kubernetes.authenticate.driver.serviceAccountName",
                    "value": "{workspaceConfig['azureAccount']}",
                    "type": "textarea"
                },
                "spark.sql.warehouse.dir":{
                    "name": "spark.sql.warehouse.dir",
                    "value": "WAREHOUSELOCATION",
                    "type": "textarea"
                },
                "spark.hadoop.fs.AbstractFileSystem.gs.impl":{
                    "name": "spark.hadoop.fs.AbstractFileSystem.gs.impl",
                    "value": "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFS",
                    "type": "textarea"
                },
                "spark.hadoop.google.cloud.auth.service.account.enable":{
                    "name": "spark.hadoop.google.cloud.auth.service.account.enable",
                    "value": "true",
                    "type": "textarea"
                },
                "spark.delta.logStore.gs.impl":{
                    "name": "spark.delta.logStore.gs.impl",
                    "value": "io.delta.storage.GCSLogStore",
                    "type": "textarea"
                },
                "spark.hadoop.fs.gs.impl":{
                    "name": "spark.hadoop.fs.gs.impl",
                    "value": "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFileSystem",
                    "type": "textarea"
                },
                 "spark.sql.extensions":{
                    "name": "spark.sql.extensions",
                    "value": "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtension",
                    "type": "textarea"
                },
                 "spark.sql.catalog.spark_catalog":{
                    "name": "spark.sql.catalog.spark_catalog",
                    "value": "org.apache.iceberg.spark.SparkSessionCatalog",
                    "type": "textarea"
                }
                """
                sparkConfigJSON = sparkConfigJSON.replace('GOOGLEKEY', workspaceConfig['googleKey']).replace('WAREHOUSELOCATION', workspaceConfig['warehouseLocation'])
        with open("workspace/services/templates/conf/interpreter.json", "r") as file:
            zeppelinInterpreterTemplate = file.read()
            zeppelinInterpreterTemplate = zeppelinInterpreterTemplate.replace('sparkConfigJSON', sparkConfigJSON)
            zeppelinInterpreterTemplate = zeppelinInterpreterTemplate.replace('_HOST', os.environ.get("POSTGRES_DB_HOST")).replace('_PORT', os.environ.get("POSTGRES_DB_PORT")).replace('_USERNAME', os.environ.get("POSTGRES_DB_USERNAME")).replace('_PASSWORD', os.environ.get("POSTGRES_DB_PASSWORD")).replace('_DBNAME', (f"{workspaceName}_metastore"))
            
        Path(f"data/{workspaceName}/conf").mkdir(parents=True, exist_ok=True)
        with open(f"data/{workspaceName}/conf/interpreter.json", "w") as file:
            file.write(zeppelinInterpreterTemplate)

        zeppelinEnvTemplate = open("workspace/services/templates/conf/zeppelin-env.sh", "r")
        zeppelinEnvTemplate = zeppelinEnvTemplate.read()
        zeppelinEnvTemplate = zeppelinEnvTemplate.format_map(SafeDict(inactivityTimeout=workspaceConfig['inactivityTimeout']))
        Path(f"data/{workspaceName}/conf").mkdir(parents=True, exist_ok=True)
        zeppelinEnvFile = open(f"data/{workspaceName}/conf/zeppelin-env.sh", "w")
        zeppelinEnvFile.write(zeppelinEnvTemplate)

        interpreterSpecTemplate = open("workspace/services/templates/zeppelinInterpreter.yaml", "r")
        interpreterSpecTemplate = interpreterSpecTemplate.read()
        interpreterSpecTemplate = interpreterSpecTemplate.replace('WORKSPACE_NAME', workspaceName)
        Path(f"data/{workspaceName}/k8s/interpreter").mkdir(parents=True, exist_ok=True)
        interpreterSpecFile = open(f"data/{workspaceName}/k8s/interpreter/100-interpreter-spec.yaml", "w")
        interpreterSpecFile.write(interpreterSpecTemplate)

        jobInterpreterSpecTemplate = open("workspace/services/templates/zeppelinJobServerInterpreter.yaml", "r")
        jobInterpreterSpecTemplate = jobInterpreterSpecTemplate.read()
        jobInterpreterSpecTemplate = jobInterpreterSpecTemplate.replace('WORKSPACE_NAME', workspaceName)
        Path(f"data/{workspaceName}/jobk8s/interpreter").mkdir(parents=True, exist_ok=True)
        jobInterpreterSpecFile = open(f"data/{workspaceName}/jobk8s/interpreter/100-interpreter-spec.yaml", "w")
        jobInterpreterSpecFile.write(jobInterpreterSpecTemplate)

        if os.environ.get("ENVIRONMENT","") == "dev":
            subprocess.Popen([
                "kubectl cp data/WORKSPACE_NAME POD_NAMESPACE/$(kubectl get pods -n POD_NAMESPACE | grep lakehouse | awk '{print $1}'):/code/data/WORKSPACE_NAME".replace('POD_NAMESPACE', self.POD_NAMESPACE).replace("WORKSPACE_NAME", workspaceName)],shell=True)
        
        v1Core = client.CoreV1Api()
        v1App = client.AppsV1Api()
        deploymentTemplateFile = open("workspace/services/templates/zeppelinServer.yaml", "r")
        deploymentBody = deploymentTemplateFile.read()
        deploymentBody = deploymentBody.format_map(SafeDict(workspaceName=workspaceName, podNamespace=self.POD_NAMESPACE))
        deploymentBody = yaml.safe_load(deploymentBody)
        v1App.create_namespaced_deployment(namespace=self.POD_NAMESPACE, body=deploymentBody)
        serviceTemplateFile = open("workspace/services/templates/zeppelinService.yaml", "r")
        serviceBody = serviceTemplateFile.read()
        serviceBody = serviceBody.format_map(SafeDict(workspaceName=workspaceName, podNamespace=self.POD_NAMESPACE))
        serviceBody = yaml.safe_load(serviceBody)
        v1Core.create_namespaced_service(namespace=self.POD_NAMESPACE, body=serviceBody)
        pvcTemplateFile = open("workspace/services/templates/zeppelinPVC.yaml", "r")
        pvcBody = pvcTemplateFile.read()
        pvcBody = pvcBody.format_map(SafeDict(workspaceName=workspaceName, podNamespace=self.POD_NAMESPACE))
        pvcBody = yaml.safe_load(pvcBody)
        sparkServiceSpecTemplate = open("workspace/services/templates/sparkService.yaml", "r")
        sparkServiceSpecTemplate = sparkServiceSpecTemplate.read()
        sparkServiceSpecTemplate = sparkServiceSpecTemplate.replace('WORKSPACE_NAME', workspaceName)
        sparkServiceBody = yaml.safe_load(sparkServiceSpecTemplate)
        v1Core.create_namespaced_service(namespace=self.POD_NAMESPACE, body=sparkServiceBody)
       
        # try:
        v1Core.create_namespaced_persistent_volume_claim(namespace=self.POD_NAMESPACE, body=pvcBody)
        
        # except:
        #     pass

    def addZeppelinJobServer(self, podId, workspaceId):
        v1 = client.CoreV1Api()
        podTemplateFile = open("utils/kubernetesTemplates/zeppelinServer.yaml", "r")
        podBody = podTemplateFile.read()
        workspaceName = "zeppelin-server-" + Workspace.objects.get(pk=workspaceId).name 
        podBody = podBody.format_map(SafeDict(podId=podId, podNamespace=self.POD_NAMESPACE, workspace=workspaceName))
        podBody = yaml.safe_load(podBody)
        v1.create_namespaced_pod(namespace=self.POD_NAMESPACE, body=podBody)
        serviceTemplateFile = open("utils/kubernetesTemplates/zeppelinService.yaml", "r")
        serviceBody = serviceTemplateFile.read()
        serviceBody = serviceBody.format_map(SafeDict(podId=podId, podNamespace=self.POD_NAMESPACE))
        serviceBody = yaml.safe_load(serviceBody)
        v1.create_namespaced_service(namespace=self.POD_NAMESPACE, body=serviceBody)

    def removeZeppelinServer(self, podId):
        v1 = client.CoreV1Api()
        try:
            v1.delete_namespaced_pod(name=podId, namespace=self.POD_NAMESPACE)
            v1.delete_namespaced_service(name=podId, namespace=self.POD_NAMESPACE)
        except Exception as ex:
            logger.error(f"Error removing zeppelin server: {podId}. Error: {str(ex)}")

    def removeWorkspace(self, podId):
        v1App = client.AppsV1Api()
        v1 = client.CoreV1Api()
        serverName = "zeppelin-server-" + podId
        try:
            v1App.delete_namespaced_deployment(name=serverName, namespace=self.POD_NAMESPACE)
            v1.delete_namespaced_service(name=serverName, namespace=self.POD_NAMESPACE)
        except Exception as ex:
            logger.error(f"Error removing zeppelin workspace: {serverName}. Error: {str(ex)}")
    
    def switchWorkspaceServer(self, workspaceId: int):
        workspaceName = Workspace.objects.get(pk=workspaceId).name
        if os.environ.get("ENVIRONMENT","") == "dev":
            os.system("kill -9 $(lsof -t -i:8080)")
            subprocess.Popen(["kubectl", "port-forward", "services/zeppelin-server-" + workspaceName, "8080:80", "-n", self.POD_NAMESPACE])

    def getPodStatus(self, podId):
        v1 = client.CoreV1Api()
        podResponse = v1.read_namespaced_pod(name=podId, namespace=self.POD_NAMESPACE)
        return podResponse.status.phase

    def getPods(self):
        v1 = client.CoreV1Api()
        pods = v1.list_namespaced_pod(namespace=self.POD_NAMESPACE)
        return pods.items

    def getDeployments(self):
        v1App = client.AppsV1Api()
        deployments = v1App.list_namespaced_deployment(namespace=self.POD_NAMESPACE)
        return deployments.items
        
    def portForward(self, zeppelinServerId):
        port = str(random.randint(10000,65000))
        time.sleep(3) 
        subprocess.Popen(["kubectl", "port-forward", "pod/" + zeppelinServerId, port + ":8080", "-n", self.POD_NAMESPACE])
        return port

# Export initalized class
Kubernetes = KubernetesAPI()