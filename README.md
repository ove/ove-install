# Open Visualisation Environment - Install

This repository contains a collection of installers for [Open Visualisation Environment (OVE)](https://github.com/ove/ove).

OVE is an open-source software stack, designed to be used in large high resolution display (LHRD) environments like the [Imperial College](http://www.imperial.ac.uk) [Data Science Institute's](http://www.imperial.ac.uk/data-science/) [Data Observatory](http://www.imperial.ac.uk/data-science/data-observatory/).

We welcome collaboration under our [Code of Conduct](https://github.com/ove/ove-apps/blob/master/CODE_OF_CONDUCT.md).

## Running the script

The compiled **setup** can be downloaded from the repository releases for each platform. The file will guide you thorough all the parameters of the setup process.

Alternatively the Python script can be executed as well. After cloning or downloading this repository, the **setup.py** script can be executed locally using a valid Python 2 or 3 install.

## Developing/Building a single setup file

- Create a virtual environment with virtualenv
- Install the dependencies (requirements.txt) by running: 

```bash
pip install -r requirements.txt
```

- Build the compiled setup/executable by running:

**UNIX:**

```bash
pyinstaller setup.py --add-data templates/docker-compose.*.yml:templates --add-data versions.yml:. --onefile
```

**Windows:**

```bash
pyinstaller setup.py --add-data templates/docker-compose.*.yml;templates --add-data versions.yml;. --onefile
```

- At the end of the build, the compiled **setup** file can be found at `dist/setup`.

## Supported platforms

The system has been fully tested on macOS 10.13.4 (High Sierra), Ubuntu 18.04 (desktop and server), both bare metal deployment and docker.

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
