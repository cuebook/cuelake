---
layout: default
title: Settings
nav_order: 10
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

1. Create a slack app.
2. Once you create the app, you will be redirected to your app's `Basic Information` screen. In `Add features and functionality`, click on `Incoming Webhooks`.
3. In the next screen, use the slider button to Activate incoming webooks.
4. Click on `Add New Webhook to Workspace`.
5. In the next screen, choose a channel from your Slack workspace and click `Allow`.
6. You will now be redirected to your app's incoming webhooks screen. Copy the `Webhook URL` and paste it in Cuelake’s Settings screen.
