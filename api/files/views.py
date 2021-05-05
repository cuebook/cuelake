from django.http import HttpRequest
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from files.services import FilesServices

class Files(APIView):
	"""
	Class to deal with multiple files
	"""
	def get(self, request, offset: int):
		"""Gets all workflows"""
		res = FilesServices.getFiles(offset)
		return Response(res.json())

class File(APIView):
	"""
	Class to deal with individual file
	"""
	def post(self, request):
		"""Uploads file"""
		fileName = list(request.data.keys())[0]
		file = request.data[fileName]
		res = FilesServices.uploadFile(file, fileName)
		return Response(res.json())

	def delete(self, request):
		"""
		deletes file
		"""
		res = None
		return Response(res.json())

