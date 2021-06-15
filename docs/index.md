---
layout: default
title: Overview
nav_order: 1
description: "With CueLake, you can use SQL to build ELT (Extract, Load, Transform) pipelines on a data lakehouse"
permalink: /
---

<p align="center">
  <a href="https://cuelake.cuebook.ai" target="_blank">
    <img alt="Cuelake Logo" width="220" src="images/cuelake.png">
  </a>
</p>
<p align="center">
  <a href="https://codeclimate.com/github/cuebook/cuelake/maintainability">
    <img src="https://api.codeclimate.com/v1/badges/db3c4c0355e11d23bb66/maintainability" alt="Maintainability">
  </a>
  <a href="https://codeclimate.com/github/cuebook/cuelake/test_coverage">
    <img src="https://api.codeclimate.com/v1/badges/db3c4c0355e11d23bb66/test_coverage" alt="Test Coverage">
  </a>
  <a href="https://github.com/cuebook/cuelake/actions/workflows/pr_checks.yml">
    <img src="https://github.com/cuebook/cuelake/actions/workflows/pr_checks.yml/badge.svg" alt="Test Coverage">
  </a>
  <br>
  <a href="https://github.com/cuebook/cuelake/blob/main/LICENSE.md">
    <img src="https://img.shields.io/github/license/cuebook/cuelake" alt="License">
  </a>
  <a href="https://discord.gg/R7EABXwUnv">
    <img src="https://discordapp.com/api/guilds/854395659431182366/widget.png" alt="Discord">
  </a>
</p>
<br>
<br>

# Overview

With CueLake, you can use SQL to build `ELT` (Extract, Load, Transform) pipelines on a **data lakehouse**.

You write **Spark SQL** statements in **Zeppelin** notebooks. You then schedule these notebooks using workflows (DAGs).

To extract and load incremental data, you write simple select statements. CueLake executes these statements against your databases and then merges incremental data into your data lakehouse (powered by **Apache Iceberg**).

To transform data, you write SQL statements to create views and tables in your data lakehouse. 

CueLake uses Celery as the executor and celery-beat as the scheduler. Celery jobs trigger **Zeppelin** notebooks. Zeppelin auto-starts and stops the Spark cluster for every scheduled run of notebooks.

To know why we are building CueLake, read our [viewpoint](https://cuelake.cuebook.ai/viewpoint).


![CueLake](images/CueLake.gif)

### What is a Lakehouse?
A lakehouse is a new, open architecture that combines the best elements of data lakes and data warehouses (see Databricks articles [here](https://databricks.com/blog/2020/01/30/what-is-a-data-lakehouse.html) and [here](https://databricks.com/research/lakehouse-a-new-generation-of-open-platforms-that-unify-data-warehousing-and-advanced-analytics)).

# Features
* **Upsert Incremental data.** CueLake uses Iceberg’s `merge into` query to automatically merge incremental data.
* **Create Views in data lakehouse.** CueLake enables you to create views over Iceberg tables.
* **Create DAGs.** Group notebooks into workflows and create DAGs of these workflows.  
* **Elastically Scale Cloud Infrastructure.** CueLake uses Zeppelin to auto create and delete Kubernetes resources required to run data pipelines.
* **In-built Scheduler** to schedule your pipelines.
* **Automated maintenance of Iceberg tables.** CueLake does automated maintenance of Iceberg tables -  expires snapshots, removes old metadata and orphan files, compacts data files.
* **Monitoring.**  Get Slack alerts when a pipeline fails. CueLake maintains detailed logs.
* **Versioning in Github.** Commit and maintain versions of your Zeppelin notebooks in Github.
* **Data Security.** Your data always stays within your cloud account.

### Current Limitations
* Supports AWS S3 as a destination. Support for ADLS and GCS is in the roadmap.
* Uses Apache Iceberg as an open table format. Delta support is in the roadmap.
* Uses Celery for scheduling jobs. Support for Airflow is in the roadmap.


# Support
For general help using CueLake, read the documentation, or go to [Github Discussions](https://github.com/cuebook/cuelake/discussions).

To report a bug or request a feature, open an [issue](https://github.com/cuebook/cuelake/issues).

# Community
Join our [cuelake discord server](https://discord.gg/R7EABXwUnv) and ask your questions to the developers directly.

# Contributors!

<ul class="list-style-none">
{% for contributor in site.github.contributors %}
  <li class="d-inline-block mr-1">
     <a href="{{ contributor.html_url }}"><img src="{{ contributor.avatar_url }}" width="32" height="32" alt="{{ contributor.login }}"/></a>
  </li>
{% endfor %}
</ul>
