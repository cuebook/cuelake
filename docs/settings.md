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
3. In the next screen, use the slider button to Activate incoming webhooks.
4. Click on `Add New Webhook to Workspace`.
5. In the next screen, choose a channel from your Slack workspace and click `Allow`.
6. You will now be redirected to your app's incoming webhooks screen. Copy the `Webhook URL` and paste it in Cuelake’s Settings screen.


## Add Github as version control for notebooks

### Create a Github repo
Signup on github.com and create a new repository.

### Exec inside the zeppelin server pod
Get the pod id by running the following command:

```
kubectl get pods -n cuelake | grep zeppelin-server
```

Once you have the pod id then you can exec inside the pod:

```
kubectl exec -it <POD_ID> -n namespace bash
```


### Clone the github repository in your Zeppelin notebook directory
Since /zeppelin/notebook is mounted via PV, we cannot delete it and also we cannot directly clone the github repository there. So first we will clone the github repository in some other folder and then just copy the conetent of the folder to our /zeppelin/notebook directory.

Go to `/zeppelin/` and place you git repo:

```bash
git clone <remote repo> 
```

Copy all contents from the cloned directory to /zeppelin/notebook

```
cp -R <remote-repo>/* /zeppelin/notebook/
```

### Configure zeppelin-site.xml
Go to file `/zeppelin/conf/zeppelin-site.xml` and add:

```xml
<property>
  <name>zeppelin.notebook.git.remote.access-token</name>
  <value>GITHUB_PERSONAL_ACCESS_TOKEN</value>
  <description>from https://github.com/settings/tokens</description>
</property>

<property>
  <name>zeppelin.notebook.git.remote.origin</name>
  <value>org.apache.zeppelin.notebook.repo.GitHubNotebookRepo</value>
  <description>notebook persistence layer implementation</description>
</property>

<property>
  <name>zeppelin.notebook.dir</name>
  <value>YOUR_GIT_CLONED_DIRECTORY</value>
  <description>notebook persistence layer implementation</description>
</property>

<property>
  <name>zeppelin.notebook.git.remote.username</name>
  <value>GITHUB_USERNAME</value>
  <description>remote Git repository username</description>
</property>
```

You can get GITHUB_PERSONAL_ACCESS_TOKEN from [https://github.com/settings/tokens](https://github.com/settings/tokens)


### Configure add all and auto push
This step is required to automatically push all your changes to github when you commit it while you are working on a zeppelin notebook.

Exec inside the pod and go to /zeppelin/notebook, in the `.git/hooks` folder, and create a `post-commit` file, make it executable `chmod +x filename`, and add:

```bash
#!/bin/sh
git push origin master
```

For adding all changed files when you commit:

Create a `pre-commit` file, make it executable `chmod +x filename`, and add:

```bash
#!/bin/sh
git add -A
```
