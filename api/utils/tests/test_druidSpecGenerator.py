import pytest
import unittest
import os
from unittest import mock
from django.test import TestCase
from django.urls import reverse
from mixer.backend.django import mixer
import pyarrow.parquet as pq
import pandas as pd
import numpy as np
from pandas._libs.tslibs.timestamps import Timestamp
from decimal import Decimal

from utils.druidSpecGenerator import DruidIngestionSpecGenerator


def test_getIngestionSpec():
    nan = np.nan
    df = pd.DataFrame([{'CREATEDTS': Timestamp('2016-02-25 17:39:37.925000'),
        'P_BASEPRICE': Decimal('0E-8'),
        'P_QUANTITY': Decimal('1.00000000'),
        'P_TOTALPRICE': Decimal('0E-8'),
        'UserType': None,
        'UserGender': None,
        'UserPostalCode': None,
        'UserCity': None,
        'UserRegionCode': None,
        'UserRegion': None,
        'UserLTOrderCount': nan,
        'UserLTV': None,
        'UserCSTickets': nan,
        'UserAvgRating': nan,
        'UserReturnRequests': nan,
        'UserReturnQty': None,
        'UserRefundAmount': None,
        'UserOrderEntryCount': nan,
        'UserOrderQty': None,
        'UserCanceledQty': None,
        'P_STYLECODE': 'S15370SWKU310S',
        'P_BRANDCODE': 'STOP',
        'P_SEASONCODE': 'S15',
        'P_DEPARTMENTCODE': '451',
        'P_SUBDEPARTMENTCODE': '101',
        'P_CLASSCODE': '201',
        'P_SUBCLASSCODE': '101',
        'P_ISAVAILABLE': Decimal('1'),
        'P_COLOURCODE': 'BLUE',
        'P_SIZECODE': None,
        'P_NEWARRIVAL': None,
        'P_MMSBRANDCODE': None,
        'P_STOCKSTATUS': None,
        'P_MMSSIZECODE': None},
        {'CREATEDTS': Timestamp('2016-02-26 08:42:19.379000'),
        'P_BASEPRICE': Decimal('0E-8'),
        'P_QUANTITY': Decimal('1.00000000'),
        'P_TOTALPRICE': Decimal('0E-8'),
        'UserType': None,
        'UserGender': None,
        'UserPostalCode': None,
        'UserCity': None,
        'UserRegionCode': None,
        'UserRegion': None,
        'UserLTOrderCount': nan,
        'UserLTV': None,
        'UserCSTickets': nan,
        'UserAvgRating': nan,
        'UserReturnRequests': nan,
        'UserReturnQty': None,
        'UserRefundAmount': None,
        'UserOrderEntryCount': nan,
        'UserOrderQty': None,
        'UserCanceledQty': None,
        'P_STYLECODE': 'Y12FNS5168300',
        'P_BRANDCODE': 'FUNSKOOL',
        'P_SEASONCODE': 'FA8',
        'P_DEPARTMENTCODE': 'NB10',
        'P_SUBDEPARTMENTCODE': 'NB10C041',
        'P_CLASSCODE': 'NB10C041D0253',
        'P_SUBCLASSCODE': 'NB10C041D0253E178',
        'P_ISAVAILABLE': Decimal('1'),
        'P_COLOURCODE': 'MULTI',
        'P_SIZECODE': 'FRSZ',
        'P_NEWARRIVAL': None,
        'P_MMSBRANDCODE': None,
        'P_STOCKSTATUS': None,
        'P_MMSSIZECODE': 'FRSZ'}])

    df.to_parquet("test.parquet")
    schema = pq.ParquetDataset("test.parquet").schema

    os.remove("test.parquet")

    datasetLocation = 's3://test-bucket/druid/CARTENTRIES/'

    print(DruidIngestionSpecGenerator.getIngestionSpec(datasetLocation=datasetLocation, datasetSchema=schema))

    ingestionSpec = '{"type": "index", "spec": {"dataSchema": {"dataSource": "CARTENTRIES", "timestampSpec": {"column": "CREATEDTS", "format": "millis", "missingValue": null}, "dimensionsSpec": {"dimensions": [{"type": "string", "name": "P_STYLECODE", "multiValueHandling": "SORTED_ARRAY", "createBitmapIndex": true}, {"type": "string", "name": "P_BRANDCODE", "multiValueHandling": "SORTED_ARRAY", "createBitmapIndex": true}, {"type": "string", "name": "P_SEASONCODE", "multiValueHandling": "SORTED_ARRAY", "createBitmapIndex": true}, {"type": "string", "name": "P_DEPARTMENTCODE", "multiValueHandling": "SORTED_ARRAY", "createBitmapIndex": true}, {"type": "string", "name": "P_SUBDEPARTMENTCODE", "multiValueHandling": "SORTED_ARRAY", "createBitmapIndex": true}, {"type": "string", "name": "P_CLASSCODE", "multiValueHandling": "SORTED_ARRAY", "createBitmapIndex": true}, {"type": "string", "name": "P_SUBCLASSCODE", "multiValueHandling": "SORTED_ARRAY", "createBitmapIndex": true}, {"type": "string", "name": "P_COLOURCODE", "multiValueHandling": "SORTED_ARRAY", "createBitmapIndex": true}, {"type": "string", "name": "P_SIZECODE", "multiValueHandling": "SORTED_ARRAY", "createBitmapIndex": true}, {"type": "string", "name": "P_MMSSIZECODE", "multiValueHandling": "SORTED_ARRAY", "createBitmapIndex": true}]}, "metricsSpec": [{"type": "count", "name": "count"}, {"type": "doubleSum", "name": "P_BASEPRICE", "fieldName": "P_BASEPRICE", "expression": null}, {"type": "doubleSum", "name": "P_QUANTITY", "fieldName": "P_QUANTITY", "expression": null}, {"type": "doubleSum", "name": "P_TOTALPRICE", "fieldName": "P_TOTALPRICE", "expression": null}, {"type": "doubleSum", "name": "P_ISAVAILABLE", "fieldName": "P_ISAVAILABLE", "expression": null}], "granularitySpec": {"type": "uniform", "segmentGranularity": "MONTH", "queryGranularity": "MINUTE", "rollup": true, "intervals": null}, "transformSpec": {"filter": null, "transforms": []}}, "ioConfig": {"type": "index", "inputSource": {"type": "s3", "uris": null, "prefixes": ["s3://test-bucket/druid/CARTENTRIES/"], "objects": null}, "inputFormat": {"type": "parquet", "flattenSpec": {"useFieldDiscovery": true, "fields": []}, "binaryAsString": false}, "appendToExisting": false}, "tuningConfig": {"type": "index_parallel", "maxRowsPerSegment": 5000000, "maxRowsInMemory": 1000000, "maxBytesInMemory": 0, "maxTotalRows": null, "numShards": null, "splitHintSpec": null, "partitionsSpec": {"type": "dynamic", "maxRowsPerSegment": 5000000, "maxTotalRows": null}, "indexSpec": {"bitmap": {"type": "concise"}, "dimensionCompression": "lz4", "metricCompression": "lz4", "longEncoding": "longs"}, "indexSpecForIntermediatePersists": {"bitmap": {"type": "concise"}, "dimensionCompression": "lz4", "metricCompression": "lz4", "longEncoding": "longs"}, "maxPendingPersists": 0, "forceGuaranteedRollup": false, "reportParseExceptions": false, "pushTimeout": 0, "segmentWriteOutMediumFactory": null, "maxNumConcurrentSubTasks": 1, "maxRetry": 3, "taskStatusCheckPeriodMs": 1000, "chatHandlerTimeout": "PT10S", "chatHandlerNumRetries": 5, "maxNumSegmentsToMerge": 100, "totalNumMergeTasks": 10, "logParseExceptions": false, "maxParseExceptions": 2147483647, "maxSavedParseExceptions": 0, "buildV9Directly": true, "partitionDimensions": []}}, "context": {"forceTimeChunkLock": true}, "dataSource": "CARTENTRIES"}'
    assert DruidIngestionSpecGenerator.getIngestionSpec(datasetLocation=datasetLocation, datasetSchema=schema) == ingestionSpec

