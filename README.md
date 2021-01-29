# edgex-docker-hub-documentation

## Summary

EdgeX Foundry Docker Hub descriptions and overviews.

Also includes Python3 scripts to:
* generate the overviews from markdown files
* update the description of the associated Docker images in DockerHub

## Jenkins Triggers

Refers to the `deploy-overviews` script only.

* Manual (User initiated)

## Script Usage

### `deploy-overviews`
```bash
usage: deploy-overviews.py [-h] [--overviews OVERVIEWS_PATH]
                           [--descriptions DESCRIPTIONS_PATH] [--user USER]
                           [--name NAME] [--execute]

A Python script that updates descriptions of DockerHub images using a folder
containing associated markdown files

optional arguments:
  -h, --help            show this help message and exit
  --overviews OVERVIEWS_PATH
                        folder path containing Docker image overviews in md
                        format
  --descriptions DESCRIPTIONS_PATH
                        path to file containing Docker image descriptions
  --user USER           DockerHub user containing the Docker images to update
  --name NAME           a regex to match name of images to include in
                        processing
  --execute             execute processing - not setting is same as running in
                        NOOP mode
```