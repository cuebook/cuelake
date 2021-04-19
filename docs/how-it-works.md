---
layout: default
title: How it works
nav_order: 3
permalink: /how-it-works
---

# How it works
CueLake is built upon three core open source products - [Zeppelin](https://zeppelin.apache.org/), [Spark SQL](https://spark.apache.org/), and [Iceberg](https://iceberg.apache.org/).

Every pipeline is a notebook in CueLake. When you add a new pipeline from a template in CueLake, it automatically creates a Zeppelin notebook. The notebook has one or more paragraphs that get executed in a sequence. CueLake monitors the execution of each notebook, and maintains detailed logs for each paragraph.

Here are examples of a few tasks that paragraphs execute:
* Execute Spark SQL query to fetch incremental data from the database.
* Sort the incremental data.
* Merge the incremental data into the Iceberg table.
* Run maintenance on Iceberg table

When assigned a schedule, a notebook gets executed as per the schedule.

On each trigger of a schedule, assigned notebooks are queued for execution. CueLake then starts the Spark cluster and queued notebooks are executed in parallel. Once all notebooks are executed, the Spark cluster is automatically shut down.
