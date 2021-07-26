from django.db import models

class Workspace(models.Model):
	name = models.CharField(max_length=200)
	description = models.TextField(default="")

class WorkspaceConfig(models.Model):
	workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE)
	storage = models.CharField(max_length=100, blank=True, null=True) # GS/S3/AZFS/PV
	s3AccessKey = models.TextField(null=True, blank=True)
	s3SecretKey = models.TextField(null=True, blank=True)
	googleKey = models.TextField(null=True, blank=True)
	azureAccount = models.TextField(null=True, blank=True)
	azureKey = models.TextField(null=True, blank=True)
	inactivityTimeout = models.IntegerField(default=600) # Inactivity timeout in seconds, default 600 - 10 mins.
	zeppelinServerImage = models.CharField(max_length=200, blank=True, null=True)
	zeppelinInterpreterImage = models.CharField(max_length=200, blank=True, null=True)
	sparkImage = models.CharField(max_length=200, blank=True, null=True)
	acidProvider = models.CharField(max_length=100, blank=True, null=True) # Delta/Iceberg/None


class EnvironmentVariable(models.Model):
	workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE)
	name = models.TextField(null=True,blank=True)
	value = models.TextField(null=True, blank=True)

class KubernetesTemplate(models.Model):
	workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE)
	zeppelinServerTemplate = models.TextField(null=True, blank=True)
	zeppelinJobServerTemplate = models.TextField(null=True, blank=True)
	interpreterTemplate = models.TextField(null=True, blank=True)