import boto3
from typing import List
from utils.apiResponse import ApiResponse
from django.conf import settings

S3_BUCKET_NAME = settings.S3_BUCKET_NAME
S3_FILES_PREFIX = settings.S3_FILES_PREFIX


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
		response = s3.list_objects_v2(Bucket=S3_BUCKET_NAME, Prefix=S3_FILES_PREFIX, Delimiter="/")
		contents: list = response['Contents']

		for content in contents:
			if 'ETag' in content:
				del content['ETag']
			if 'StorageClass' in content:
				del content['StorageClass']
			if 'Owner' in content:
				del content['Owner']

			content['Key'] = content['Key'][len(S3_FILES_PREFIX):]

		res.update(True, "Files retrieved successfully", contents)
		return res

	@staticmethod
	def uploadFile(file):
		"""
		Service to upload files to s3
		"""
		res = ApiResponse(message="Error uploading file")
		s3 = boto3.client("s3")
		s3.upload_fileobj(Fileobj=file, Bucket=S3_BUCKET_NAME, Key=S3_FILES_PREFIX+file.name)

		res.update(True, "Successfully uploaded file")
		return res

	@staticmethod
	def deleteFile(fileKey: str):
		"""
		Service to delete file in s3
		"""
		res = ApiResponse(message="Error uploading file")
		s3 = boto3.client("s3")
		s3.delete_object(Bucket=S3_BUCKET_NAME, Key=S3_FILES_PREFIX+fileKey)
		res.update(True, "Successfully uploaded file")
		return res
