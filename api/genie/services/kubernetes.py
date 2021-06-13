import os
import datetime as dt
from typing import List
from utils.apiResponse import ApiResponse
from kubernetes import config, client

class KubernetesServices:

    @staticmethod
    def getDriversCount():
        """
        Gets Driver and executors count
        """
        res = ApiResponse()
        if os.environ.get("POSTGRES_DB_HOST","") == "localhost":
            config.load_kube_config()
        else:
            config.load_incluster_config()
        runningDrivers = 0
        runningExecutors = 0
        pendingDrivers = 0
        pendingExecutors = 0
        v1 = client.CoreV1Api()
        POD_NAMESPACE = os.environ.get("POD_NAMESPACE","cuelake")
        ret = v1.list_namespaced_pod(POD_NAMESPACE, watch=False)
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
        res.update(True, "Pods status retrieved successfully", data)
        return res
