---
layout: default
title: Installation
nav_order: 5
permalink: /installation
---

# Installation

## Install via helm chart

### Add Cuebook helm repo

```bash
helm repo add cuebook https://cuebook.github.io/helm-charts/ 
helm repo update
```

### Install CueLake
Install CueLake with default configuration:

```bash
helm install cuelake cuelake/cuelake
```

Install CueLake in a specific namespace:

```bash
helm install cuelake cuelake/cuelake -n <NAMESPACE>
```

To install CueLake with custom configuration, download the values.yaml file for CueLake.

```bash
wget https://raw.githubusercontent.com/cuebook/helm-charts/main/helm-chart-sources/cuelake/values.yaml
```

Edit the file and install CueLake:

```bash
helm install cuelake cuelake/cuelake -f values.yaml
```

After installation is complete, CueLake UI can be acceseed via port forward:

```bash
kubectl port-forward services/lakehouse 8080:80 -n <NAMESPACE>
```

## Install via Kubectl

```bash
kubectl create namespace cuelake
kubectl apply -f https://raw.githubusercontent.com/cuebook/cuelake/main/cuelake.yaml -n cuelake
kubectl port-forward services/lakehouse 8080:80 -n cuelake
```

To install CueLake with custom configuration, download the cuelake.yaml file and edit the properties for resource cuelake-conf config map.

```bash
wget https://raw.githubusercontent.com/cuebook/cuelake/main/cuelake.yaml
```

Edit the properties in cuelake-conf and apply the changes via kubectl.

```bash
kubectl apply -f cuelake.yaml
```

## Properties
Below properties can be set in both cuelake.yaml (kubectl installation) and values.yaml (helm installation).

### CueLake DB Properties (Optional)
If below properties are not set, sqlite db is used as CueLake database.

```yaml
POSTGRES_DB_HOST="localhost"
POSTGRES_DB_USERNAME="postgres"
POSTGRES_DB_PASSWORD="postgres"
POSTGRES_DB_SCHEMA="cuelake_db"
POSTGRES_DB_PORT=5432
```

### S3 Settings
Name of the S3 bucket being used as your data warehouse location. This will be also used for uploading files via CueLake.

```yaml
S3_BUCKET_NAME="YourBucketName"
```

Default directory for uplaoding files is s3://<YourBucketName>/files. If you wish to change it you can do so by setting S3_FILES_PREFIX property.

```yaml
S3_FILES_PREFIX="files/"
```

Default directory for iceberg tables (hadoop catalog) is s3://<YourBucketName>/cuelake. If you wish to change it you can do so by setting HADOOP_S3_PREFIX property.

```yaml
HADOOP_S3_PREFIX="cuelake/"
```

If you change HADOOP_S3_PREFIX, please change the spark interpreter setting `spark.sql.catalog.cuelake.warehouse` accordingly. 

### Metastore DB Settings
We currently support Postgres as spark metastore database. Information related to saved spark tables and views get stored here. If not set the tables and views will be destroyed on every interpreter restart.

```yaml
METASTORE_POSTGRES_HOST="localhost"
METASORE_POSTGRES_PORT=5432
METASORE_POSTGRES_USERNAME="postgres"
METASORE_POSTGRES_PASSWORD="postgres"
METASORE_POSTGRES_DATABASE="cuelake_metastore"
```


# Spark Interpreter Settings

## To enable hive metastore

```yaml
spark.sql.catalogImplementation	                        hive	
spark.sql.warehouse.dir	                                s3a://<BUCKET_NAME>/warehouse	
spark.sql.catalog.spark_catalog.type	                hive	
spark.sql.catalog.spark_catalog	                        org.apache.iceberg.spark.SparkSessionCatalog
spark.hadoop.javax.jdo.option.ConnectionURL	            jdbc:postgresql://<POSTGRES_HOST>:5432/<DATABASE_NAME>	
spark.hadoop.javax.jdo.option.ConnectionUserName	    username	
spark.hadoop.javax.jdo.option.ConnectionPassword	    password
spark.hadoop.javax.jdo.option.ConnectionDriverName	    org.postgresql.Driver
```

## To enable hadoop metastore for iceberg tables

```yaml
spark.sql.catalog.cuelake	                            org.apache.iceberg.spark.SparkCatalog	
spark.sql.catalog.cuelake.type	                        hadoop	
spark.sql.catalog.cuelake.warehouse	                    s3a://<BUCKET_NAME>/cuelake	
```