#!/bin/bash

pm2 delete new_doe_nft_os_buy_bot ; pm2 start --name new_doe_nft_os_buy_bot "pipenv run new_doe_nft_os_buy_bot"
pm2 delete mongs_nft_os_buy_bot ; pm2 start --name mongs_nft_os_buy_bot "pipenv run mongs_nft_os_buy_bot"
