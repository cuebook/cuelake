import logging
from io import BytesIO
import gzip
import os
from django.urls.conf import path
from rest_framework.response import Response
from rest_framework.request import Request
from django.http import HttpResponse
from django.conf import settings
from django.views.decorators.clickjacking import xframe_options_exempt
from rest_framework.decorators import api_view
import urllib3

logger = logging.getLogger(__name__)


@xframe_options_exempt
@api_view(["POST", "GET", "PUT", "DELETE"])
def main(request: Request):
    """
    main function - redirects the requests made to service on their url
    """
    workspaceName = request.path.split("/")[3]
    pathname = "/".join(request.get_full_path().split("/")[4:])

    def convert(string):
        string = string.replace("HTTP_", "", 1)
        string = string.replace("_", "-")
        return string

    requestHeaders = dict((convert(k), v) for k, v in request.META.items() if k.startswith("HTTP_"))
    # add content-type and and content-length
    requestHeaders["CONTENT-TYPE"] = request.META.get("CONTENT_TYPE", "")
    requestHeaders["CONTENT-LENGTH"] = request.META.get("CONTENT_LENGTH", "")
    if os.environ.get("ENVIRONMENT","") == "dev":
        url = "http://localhost:8080"
    else:
        url = f"http://spark-{workspaceName}:4040"

    if requestHeaders["CONTENT-TYPE"] == "text/plain" or not requestHeaders["CONTENT-TYPE"]:
        del requestHeaders["CONTENT-TYPE"]
        del requestHeaders["CONTENT-LENGTH"]
    elif requestHeaders["CONTENT-TYPE"] == "application/json" or not requestHeaders["CONTENT-TYPE"]:
        del requestHeaders["CONTENT-LENGTH"]
    if pathname:
        url = url + "/" + pathname
    http = urllib3.PoolManager()
    logger.info("Redirecting {}.".format(url))
    res = http.request(request.method, url, headers=requestHeaders, body=request.body)
    contentType = "text/html; charset=utf-8"
    if hasattr(res, "headers") and res.headers.get("Content-Type"):
        contentType = res.headers.get("Content-Type")

    zbuf = BytesIO()
    zfile = gzip.GzipFile(mode="wb", compresslevel=6, fileobj=zbuf)
    zfile.write(res.data)
    zfile.close()

    compressed_content = zbuf.getvalue()
    response = HttpResponse(compressed_content, content_type=contentType)
    response["Content-Encoding"] = "gzip"
    response["Content-Length"] = str(len(compressed_content))
    if pathname[-4:] == ".css" or pathname[-3:] == ".js":
        response["Cache-Control"] = "max-age=3600"
    return response