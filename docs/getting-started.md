---
layout: default
title: Getting Started
nav_order: 3
permalink: /getting-started
---

# Getting started
```
kubectl create namespace cuelake
kubectl apply -f https://raw.githubusercontent.com/cuebook/cuelake/main/cuelake.yaml -n cuelake
kubectl port-forward services/lakehouse 8080:80 -n cuelake
```
Now open http://localhost:8080




