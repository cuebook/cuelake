# CueLake
CueLake does the `EL` in `ELT` (Extract, Load, Transform) pipelines to a **data lakehouse**.

You write simple select statements to extract incremental data and schedule these statements. CueLake uses Spark SQL to execute these statements against your databases and then merges incremental data into your data lakehouse (powered by Apache Iceberg).

CueLake auto starts and stops the Spark cluster. For every scheduled run, CueLake starts the Spark cluster, loads incremental data into the lakehouse, and then shuts down the cluster.

# Getting started

# Features

# Current Limitations

# Support
