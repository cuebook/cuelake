---
layout: default
title: How it works
nav_order: 3
permalink: /how-it-works
---

# How it works
CueLake is built upon three core open source products - [Zeppelin](https://zeppelin.apache.org/), [Spark SQL](https://spark.apache.org/), and [Iceberg](https://iceberg.apache.org/).

You write SQL statements or code as **paragraphs** in a Zeppelin **notebook**. When you run a notebook, it's paragraphs run in a sequence. CueLake provides prebuilt notebook templates for common use cases like incremental refresh.

You add one or more notebooks to a **Workflow**. When you run a workflow, it's notebooks run in parallel.

To create a DAG of workflows, you trigger a workflow after another workflow.

To run a workflow or a notebook as per schedule, you assign it a schedule.

CueLake monitors the execution of workflows and notebooks, and maintains logs for each notebook paragraph.

On each trigger of a schedule, assigned notebooks are queued for execution. CueLake then starts the Spark cluster and runs the queued notebooks. Once notebooks are executed, the Spark cluster is automatically shut down.
