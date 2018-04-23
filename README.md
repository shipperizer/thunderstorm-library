# Thunderstorm Library

[![Build Status](https://ts-jenkins.aamts.io/buildStatus/icon?job=AAM/thunderstorm-library/master)](https://ts-jenkins.aamts.io/job/AAM/thunderstorm-library/master)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/437721a3b0f64ec2b648fd34af053b53)](https://www.codacy.com?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=artsalliancemedia/thunderstorm-library&amp;utm_campaign=Badge_Grade)
[![Codacy Badge](https://api.codacy.com/project/badge/Coverage/437721a3b0f64ec2b648fd34af053b53)](https://www.codacy.com?utm_source=github.com&utm_medium=referral&utm_content=artsalliancemedia/thunderstorm-library&utm_campaign=Badge_Coverage)

**Note: This is a public repo**

Thunderstorm library is a package for keeping functionality which is useful across multiple Thunderstorm Services in one convenient location.
If you have some functionality that you feel would be useful to other users of the library or wish to submit suggestions for improvement please
feel free to submit a pull request.

This document provides instructions for installation and basic usage.


## Contents

- [Installation](#installation)
  - [Basic usage](#basic-usage)
- [Development](#development)
- [Testing](#testing)
- [Releasing](#releasing)


## Installation

Install this library from a tarball on Github.

```shell
> pip install https://github.com/artsalliancemedia/thunderstorm-library/releases/download/vX.Y.Z/thunderstorm-library-X.Y.Z.tar.gz
> pip install thunderstorm-library
```

### Basic usage

At present the library provides some basic functions although the library will expand to cover areas such as messaging in future releases.

## Development

First you will need to pick a service to develop against.

If, for example, you are working on the `complex-service`, first clone this
repo as a subdirectory of that project.

Next, modify the installation of the thunderstorm library. The [complex-service](https://github.com/artsalliancemedia/complex-service/blob/master/env_conf/Dockerfile#L27)
has a line in its `Dockerfile` installing the auth library from a tarball. Change
this line to the following two lines:

```dockerfile
COPY thunderstorm-library /var/app/thunderstorm-library
RUN pip install -e file:/var/app/thunderstorm-library
```

## Testing

At present the library needs to support python versions 3.4, 3.5 and 3.6. The docker-compose file in this repo has individual services for each python version.
e.g. to run unit tests for python 3.4:

```bash
> docker-compose run --rm python34 make test
```

## Releasing

New releases can be easily created using [github-release](https://github.com/aktau/github-release).
Increment the version number in [`thunderstorm/__init__.py`](./thunderstorm/__init__.py),
and ensure you have a valid github token and run the following command (replacing
your github token with `{github token}`).

```shell
> GITHUB_TOKEN={github token} release
```
