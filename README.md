# Web3 Python Framework

## Installation
```bash
# clone
git clone [url]
cd [proj-name]

# Install pipenv Windows
pip install --user pipenv

# Install pipenv Linux
sudo apt install pipenv

# Install dependencies
pipenv sync

# Run Scripts
pipenv run doe_nft_os_buy_bot
pipenv run kdoe_token_buy_bot
```

## Bot usage
Change the "Details required from the user" to your own tokens

## Bot PM2
```bash
pm2 install pm2-logrotate
pm2 start --name doe_nft_os_buy_bot "pipenv run doe_nft_os_buy_bot"
pm2 delete doe_nft_os_buy_bot
```

## Bot daemon
```bash
cat <<EOF > /lib/systemd/system/doe_buy_bot.service
 [Unit]
 Description=DOE Buy Bot
 After=multi-user.target

 [Service]
 Type=idle
 ExecStart=[path-to-repo]/start_and_log.sh

 [Install]
 WantedBy=multi-user.target
EOF

sudo chmod 644 /lib/systemd/system/doe_buy_bot.service
sudo systemctl daemon-reload
sudo systemctl enable doe_buy_bot.service

sudo service start doe_buy_bot
```

pipenv run pytest tests
pipenv run pip install .
