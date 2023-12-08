#!/bin/bash

NAME="kdoe_token_buy_bot"
pm2 delete ${NAME} ; pm2 start --name ${NAME} "pipenv run ${NAME}"
