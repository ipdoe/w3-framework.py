#!/bin/bash

pm2 delete ${1} ; pm2 start --name ${1} "pipenv run ${1}"
