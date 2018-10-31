# Open Visualisation Environment

Open Visualisation Environment (OVE) is an open-source software stack, designed to be used in large high resolution display (LHRD) environments like the [Imperial College](http://www.imperial.ac.uk) [Data Science Institute's](http://www.imperial.ac.uk/data-science/) [Data Observatory](http://www.imperial.ac.uk/data-science/data-observatory/).

We welcome collaboration under our [Code of Conduct](https://github.com/ove/ove-apps/blob/master/CODE_OF_CONDUCT.md).

## Deployment guide

Docker images and docker compose configuration files are provided for easy setup. The docker-compose.ove.yml config spins up the OVE framework and docker-compose.asset.yml will create the asset manager service. These images can be configured by customizing the docker-compose files.

## Supported platforms

The system has been fully tested on Ubuntu 18.04 (desktop and server), both bare metal deployment and docker.

Docker version:

```sh
Client:
 Version:           18.06.1-ce
 API version:       1.38
 Go version:        go1.10.3
 Git commit:        e68fc7a
 Built:             Tue Aug 21 17:24:51 2018
 OS/Arch:           linux/amd64
 Experimental:      false

Server:
 Engine:
  Version:          18.06.1-ce
  API version:      1.38 (minimum version 1.12)
  Go version:       go1.10.3
  Git commit:       e68fc7a
  Built:            Tue Aug 21 17:23:15 2018
  OS/Arch:          linux/amd64
  Experimental:     false

```

Docker compose version:
```sh
docker-compose version 1.22.0, build f46880fe
docker-py version: 3.4.1
CPython version: 3.6.6
OpenSSL version: OpenSSL 1.1.0f  25 May 2017
```
