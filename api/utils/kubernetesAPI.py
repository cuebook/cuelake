import os
import yaml
import logging
from django.conf import settings
from kubernetes import config, client
from utils.safeDict import SafeDict

# Get an instance of a logger
logger = logging.getLogger(__name__)


class KubernetesAPI:
    """
    Functionalities around zeppelin APIs
    """
    if os.environ.get("ENVIRONMENT","") == "dev":
        config.load_kube_config()
    else:
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

    def addZeppelinServer(self, podId):
        v1 = client.CoreV1Api()
        podTemplateFile = open("utils/kubernetesTemplates/zeppelinServer.yaml", "r")
        podBody = podTemplateFile.read()
        podBody = podBody.format_map(SafeDict(podId=podId, podNamespace=self.POD_NAMESPACE))
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

    def getPodStatus(self, podId):
        v1 = client.CoreV1Api()
        podResponse = v1.read_namespaced_pod(name=podId, namespace=self.POD_NAMESPACE)
        return podResponse.status.phase

    def getPods(self):
        v1 = client.CoreV1Api()
        pods = v1.list_namespaced_pod(namespace=self.POD_NAMESPACE)
        return pods.items
        

# Export initalized class
Kubernetes = KubernetesAPI()