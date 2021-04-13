---
layout: default
title: Overview
nav_order: 1
description: "CueLake does the EL in ELT (Extract, Load, Transform) pipelines to a data lakehouse"
permalink: /
---

# Overview
CueLake does the `EL` in `ELT` (Extract, Load, Transform) pipelines to a **data lakehouse**.

You write simple select statements to extract incremental data and schedule these statements. CueLake uses **Spark SQL** to execute these statements against your databases and then merges incremental data into your data lakehouse (powered by **Apache Iceberg**).

CueLake auto starts and stops the Spark cluster. For every scheduled run, CueLake starts the Spark cluster, loads incremental data into the lakehouse, and then shuts down the cluster.

#### What is a Lakehouse?
A lakehouse is a new, open architecture that combines the best elements of data lakes and data warehouses (see Databricks articles [here](https://databricks.com/blog/2020/01/30/what-is-a-data-lakehouse.html) and [here](https://databricks.com/research/lakehouse-a-new-generation-of-open-platforms-that-unify-data-warehousing-and-advanced-analytics)).

# Features

### Current Limitations
* Supports relational databases (Oracle, MySQL, Postgres) as data source. More sources will be added later.
* Supports AWS S3 as a destination. Support for ADLS and GCS is in the roadmap.
* Uses Apache Iceberg as an open table format. Delta support is in the roadmap.
* Uses AWS Glue as the catalog implementation. Hive support is in the roadmap.
* Uses Celery for scheduling jobs. Support for Airflow, Dagster and Prefect is in the roadmap.

# Support
For general help using CueLake, read the documentation, or go to [Github Discussions](https://github.com/cuebook/cuelake/discussions).

To report a bug or request a feature, open an [issue](https://github.com/cuebook/cuelake/issues).

## Contributors!

<ul class="list-style-none">
{% for contributor in site.github.contributors %}
  <li class="d-inline-block mr-1">
     <a href="{{ contributor.html_url }}"><img src="{{ contributor.avatar_url }}" width="32" height="32" alt="{{ contributor.login }}"/></a>
  </li>
{% endfor %}
</ul>


