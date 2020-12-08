# Notes for GKE Migration

* Source code copied under /src directory from root.  This allows us to only copy code and not all github repo.  Ansible deploys to rackspace where copying entire repo including readmes
* .gitignore file updated to allow /src to be added.  Was specifically blocked before.

## Unused Files

Following files can probably be deleted

* .travis.yaml
* .env.dev.tempate
* gunicorn.conf

## New Directories
* src - copied Stars source code under this subdirectory
* docker-base - Directory for docker base files
* kubernetes-manifests - Kubernetes Manifests
* utils - located for gcp utilities

## New Files
* cloubuild-cert-mgr.yaml
* cloudbuild-ingress.yaml
* cloudbuild-kustomize-dev.yaml
* cloudbuild-rmq.yaml


## Modified Files
* src/stars/config/settings.py - added in MEDIA_LOCAL setting for having static be set to local
* src/stars/urls.py - changed IF statement for DEBUG to MEDIA_LOCAL so that static can be set for local

## GCS Static

Added in IS_GCS env var to trigger Django loading files into GCS. Django storage and Django libraries need to be upgraded first.  Link [here]( https://django-storages.readthedocs.io/en/latest/backends/gcloud.html#authentication)

[These instructions are for setting up static in GCS.](https://cloud.google.com/python/django/kubernetes-engine#deploying_the_app_to_)

