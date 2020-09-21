# Sialab project INERIS

This is the Gitlab project of the Sialab platform for INERIS which is available at the following URL:
* [https://heka-dev.sia-partners.ai/ineris/](https://heka-dev.sia-partners.ai/ineris/)

## Description

In this repo you will find all code that was developed for the INERIS project.
So far, you can find all code for a python dash app developed for the first need in the folder heka/frontend/src/ , and several 
codes and notebooks for the 3 needs in heka/divers .

# Running the Sialab

## **Setting up**

### 1 - Authenticate against the docker registry

In order to authenticate against the docker registry, you must run the following command:

```
docker login git.sia-partners.com:5656
```

### 2 - Set-up the project configuration

Local code tries to fetch the project's configuration under the path `conf/project_config.yml`. In order to set this up you need to:
* naviagate to the URI https://git.sia-partners.com/k8s/asterix/heka/{PROJECT_NAME}/-/settings/ci_cd#js-cicd-variables-settings
* copy the content of the `PROJECT_CONFIG` or `PROJECT_CONFIG_DEV` files
* Save this content into a new file in `conf/project_config.yml`
* **replace**, inside the file, the key `project.hostname` content with `lab.localhost` and `project.protocol` with `http`. This means that the contents of the file should look something like this:

```
[...]
project:
  hostname: lab.localhost
  log-level: INFO
  name: {PROJECT_NAME}
  protocol: http
[...]
```


## Running locally

The application can be run by using the `docker-compose` command.
Docker compose works by reading the `docker-compose.yml` file and running Docker containers according to the contents of the file.

Here are the basic commands:

* `docker-compose up (--force-recreate)` - Launch the Docker containers of the application (and force them to be re-created and not only re-started if possible)
* `docker-compose pull` - Pulls all the Docker images contained in the docker-compose.yml file
* `docker-compose build` - Builds locally all of the images within the docker-compose.yml file

## Running in the cluster

By default, all commits are deployed to the Sia Partners Kubernetes cluster:
- Commits on the *master* branch are then available at [https://heka.sia-partners.ai/ineris/](https://heka.sia-partners.ai/ineris/)
- Commits on the *dev* branch are then available at [https://heka-dev.sia-partners.ai/ineris/](https://heka-dev.sia-partners.ai/ineris/)

## Modifying the pipeline
