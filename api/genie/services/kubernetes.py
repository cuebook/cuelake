import os
import datetime as dt
from typing import List
from utils.apiResponse import ApiResponse
from kubernetes import config, client
from utils.kubernetesAPI import Kubernetes

class KubernetesServices:

    @staticmethod
    def getDriversCount():
        """
        Gets Driver and executors count
        """
        res = ApiResponse()
        data = Kubernetes.getDriversCount()
        res.update(True, "Pods status retrieved successfully", data)
        return res
