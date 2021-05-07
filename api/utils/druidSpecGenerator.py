# Class to generate Druid ingestion spec
import json
import os
import logging
from typing import List

from urllib.parse import urlparse
import boto3
import pyarrow.parquet as pq
import s3fs


PARQUET_STRING = ["STRING", "ENUM", "UUID"]
PARQUET_COMPLEX_TYPE = ["LIST", "STRUCT"]
PARQUET_INTEGER = ["INT"]
PARQUET_TIMESTAMP = ["TIME", "TIMESTAMP", "DATE"]
PARQUET_DECIMAL = ["DECIMAL"]

logger = logging.getLogger(__name__)


class DruidIngestionSpecGenerator:
    """
    Class to handle functionality around Druid ingestion spec generation
    """

    @staticmethod
    def getIngestionSpec(datasetLocation, datasetSchema):
        """
        Method to generate Druid ingestion spec
        Method doesn't support complex druid data types right now.
        :param datasetLocation: S3 location of the dataset
        :param datasetSchema The schema of the dataset
        :returns DruidSpec
        """
        logger.info("Generating Druid spec for dataset at: %s", datasetLocation)
        logger.info("Schema for dataset: %s", datasetSchema)

        datasetLocationSplit = datasetLocation.split('/')
        datasourceName = datasetLocationSplit[-1] if datasetLocationSplit[-1] else datasetLocationSplit[-2]

        return json.dumps(
            {
                "type": "index",
                "spec": {
                    "dataSchema": {
                        "dataSource": datasourceName,
                        "timestampSpec": {
                            "column": DruidIngestionSpecGenerator._getTimestampColumn(datasetSchema),
                            "format": "millis",
                            "missingValue": None,
                        },
                        "dimensionsSpec": {
                            "dimensions": DruidIngestionSpecGenerator._getDimensions(datasetSchema)
                        },
                        "metricsSpec": DruidIngestionSpecGenerator._getMetrics(datasetSchema),
                        "granularitySpec": {
                            "type": "uniform",
                            "segmentGranularity": "MONTH",
                            "queryGranularity": "MINUTE",
                            "rollup": True,
                            "intervals": None,
                        },
                        "transformSpec": {"filter": None, "transforms": []},
                    },
                    "ioConfig": {
                        "type": "index",
                        "inputSource": {
                            "type": "s3",
                            "uris": None,
                            "prefixes": [datasetLocation],
                            "objects": None,
                        },
                        "inputFormat": {
                            "type": "parquet",
                            "flattenSpec": {"useFieldDiscovery": True, "fields": []},
                            "binaryAsString": False,
                        },
                        "appendToExisting": False,
                    },
                    "tuningConfig": {
                        "type": "index_parallel",
                        "maxRowsPerSegment": 5000000,
                        "maxRowsInMemory": 1000000,
                        "maxBytesInMemory": 0,
                        "maxTotalRows": None,
                        "numShards": None,
                        "splitHintSpec": None,
                        "partitionsSpec": {
                            "type": "dynamic",
                            "maxRowsPerSegment": 5000000,
                            "maxTotalRows": None,
                        },
                        "indexSpec": {
                            "bitmap": {"type": "concise"},
                            "dimensionCompression": "lz4",
                            "metricCompression": "lz4",
                            "longEncoding": "longs",
                        },
                        "indexSpecForIntermediatePersists": {
                            "bitmap": {"type": "concise"},
                            "dimensionCompression": "lz4",
                            "metricCompression": "lz4",
                            "longEncoding": "longs",
                        },
                        "maxPendingPersists": 0,
                        "forceGuaranteedRollup": False,
                        "reportParseExceptions": False,
                        "pushTimeout": 0,
                        "segmentWriteOutMediumFactory": None,
                        "maxNumConcurrentSubTasks": 1,
                        "maxRetry": 3,
                        "taskStatusCheckPeriodMs": 1000,
                        "chatHandlerTimeout": "PT10S",
                        "chatHandlerNumRetries": 5,
                        "maxNumSegmentsToMerge": 100,
                        "totalNumMergeTasks": 10,
                        "logParseExceptions": False,
                        "maxParseExceptions": 2147483647,
                        "maxSavedParseExceptions": 0,
                        "buildV9Directly": True,
                        "partitionDimensions": [],
                    },
                },
                "context": {"forceTimeChunkLock": True},
                "dataSource": datasourceName,
            }
        )

    @staticmethod
    def _getTimestampColumn(datasetSchema) -> str:
        """
        Method to extract the timestamp column from the spec.
        In case of multiple timestamp columns in the spec, any of the
        random timestamp columns will be returned.
        :param datasetSchema Schema of the dataset
        :returns Name of the timestamp column
        """
        logger.info("Fetching the timestamp column from the schema")

        timestampColumn = None
        for obj in datasetSchema:
            if obj.logical_type.type.upper() in PARQUET_TIMESTAMP:
                timestampColumn = obj.name
                break
        return timestampColumn

    @staticmethod
    def _getMetrics(datasetSchema):
        """
        Method to fetch the metrics from the dremio schema
        :param datasetSchema Scheme of the dataset
        """
        logger.info("Fetching all the metrics from the schema")

        metrics = [{"type": "count", "name": "count"}]
        for obj in datasetSchema:

            metric = None
            if obj.logical_type.type.upper() in PARQUET_INTEGER:
                typeMetric = "longSum"
                metric = {
                    "type": typeMetric,
                    "name": obj.name,
                    "fieldName": obj.name,
                    "expression": None,
                }

            elif obj.logical_type.type.upper() in PARQUET_DECIMAL:
                typeMetric = "doubleSum"
                metric = {
                    "type": typeMetric,
                    "name": obj.name,
                    "fieldName": obj.name,
                    "expression": None,
                }

            if metric is not None:
                metrics.append(metric)

        return metrics

    @staticmethod
    def _getDimensions(datasetSchema):
        """
        Method to fetch the metrics from the dremio schema
        :param datasetSchema Scheme of the dataset
        """
        logger.info("Fetching all the dimensions from the schema")

        dimensions = []
        timestampColumns = []
        for obj in datasetSchema:
            if obj.logical_type.type.upper() in PARQUET_STRING:
                dimension = {
                    "type": "string",
                    "name": obj.name,
                    "multiValueHandling": "SORTED_ARRAY",
                    "createBitmapIndex": True,
                }
                dimensions.append(dimension)

            elif obj.logical_type.type.upper() in PARQUET_TIMESTAMP:
                dimension = {
                    "type": "string",
                    "name": obj.name,
                    "multiValueHandling": "SORTED_ARRAY",
                    "createBitmapIndex": True,
                }
                timestampColumns.append(dimension)

        # the rest of the timestamp columns are being ingnored. Add those to the dim list
        dimensions.extend(timestampColumns[1:])
        return dimensions

    @staticmethod
    def _getSchemaForDatasourceInS3(datasetLocation: str):
        """
        Gets schema for a datasource in S3 bucket at staging location
        """
        parsedInfo = urlparse(datasetLocation)
        bucket = parsedInfo.netloc
        key = parsedInfo.path
        s3 = boto3.client("s3")
        files = s3.list_objects(
            Bucket=bucket, Prefix=key.lstrip('/')
        )
        if len(files["Contents"]) > 0:
            try:
                fileName = files["Contents"][-1]["Key"]
                schema = pq.ParquetDataset(
                    bucket + "/" + fileName,
                    filesystem=s3fs.S3FileSystem(
                        anon=False
                    ),
                ).schema
                return schema
            except Exception as ex:
                logger.error(str(ex))
                return []
        else:
            return []
