---
layout: default
title: Getting Started
nav_order: 3
permalink: /getting-started
---

# Getting started
## Install CueLake
CueLake uses Kubernetes kubectl to install CueLake. We first create a namespace and then install in the namespace via YAML. You can give any name to your namespace. In the commands below, we use `cuelake` as the namespace.

```
kubectl create namespace cuelake
kubectl apply -f https://raw.githubusercontent.com/cuebook/cuelake/main/cuelake.yaml -n cuelake
kubectl port-forward services/lakehouse 8080:80 -n cuelake
```

To test if the installation is successful, run the following command
```
kubectl get pods -n cuelake
```

You should see 3 pods in running status, something like below:
```
NAME                               READY   STATUS    RESTARTS   AGE
lakehouse-74cd5d759b-8pj5c         1/1     Running   0          23h
redis-69cc674bf8-rsd74             1/1     Running   0          23h
zeppelin-server-865974dc55-rt9vg   3/3     Running   0          23h
```

Now visit http://localhost:8080 in your browser.

If you don’t want to use Kubernetes and instead want to try it out on your local machine first, we’ll soon have a docker compose version. Let us know if you’d want that sooner.

## Add Connection to a Source database
Go to the Connections screen, click on New Connection, select a database, enter access credentials and Create.

## Configure AWS
?

## Add New Notebook
Go to the Notebooks screen, click on New Notebook.
Select Incremental Refresh template
Select the source connection
Enter the SQL Select statement
Enter the complete S3 path for the destination table. 
In the Timestamp column, enter the column name of the incremental column. This must of type timestamp. 
Enter the primary key of the source in the PK column.
Save the notebook.

Now RUN the notebook. This will create a new table in the specified S3 path.
Note that first run will load the historical data as defined in the SQL query. 

Once the run is complete, you can check the data in S3. To check, click on New notebook, select Blank as the template. Now try the following SQL query to query S3.

## Merge Incremental data
To upsert incremental data, run the above notebook again, after a few rows have been inserted or updated.
To confirm that merge is successful, query the S3 table.
