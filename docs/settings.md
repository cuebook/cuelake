---
layout: default
title: Settings
nav_order: 7
permalink: /settings
---

# Settings

## Spark
You can edit your Spark cluster settings.

```
spark.driver.cores	        1	Number of cores to use for the driver process, only in cluster mode.
spark.driver.memory	        4g	Amount of memory to use for the driver process, i.e. where SparkContext is initialized, in the same format as JVM memory strings with a size unit suffix ("k", "m", "g" or "t") (e.g. 512m, 2g).
spark.executor.cores    	1	The number of cores to use on each executor
spark.executor.memory   	4g	Executor memory per worker instance. ex) 512m, 32g
spark.executor.instances	1	The number of executors for static allocation.
```


## Slack
To get Slack alerts on pipeline execution, enter your Slack Incoming Webhook here. To create an Incoming Webhook, follow the steps outlined at [https://api.slack.com/messaging/webhooks](https://api.slack.com/messaging/webhooks).
