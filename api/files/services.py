import boto3
from typing import List
from utils.apiResponse import ApiResponse
from django.conf import settings

BUCKET_NAME = settings.BUCKET_NAME
PREFIX = settings.PREFIX


class FilesServices:
	"""
	Deals with Files in s3
	"""

	@staticmethod
	def getFiles(offset: int = 0):
		"""
		Service to fetch files from s3
		"""
		res = ApiResponse(message="Error retrieving files")
		s3 = boto3.client("s3")
		response = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix=PREFIX, Delimiter="/")
		contents: list = response['Contents']

		for content in contents:
			if 'ETag' in content:
				del content['ETag']
			if 'StorageClass' in content:
				del content['StorageClass']
			if 'Owner' in content:
				del content['Owner']

			content['Key'] = content['Key'][len(PREFIX):]

		res.update(True, "Files retrieved successfully", contents)
		return res

	@staticmethod
	def uploadFile(file, fileName):
		"""
		Service to upload files to s3
		"""
		res = ApiResponse(message="Error uploading file")
		s3 = boto3.client("s3")
		s3.upload_fileobj(Fileobj=file, Bucket=BUCKET_NAME, Key=PREFIX+fileName)

		res.update(True, "Successfully uploaded file")
		return res
