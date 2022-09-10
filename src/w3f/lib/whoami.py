import w3f.lib.logger as log

NAME = "w3f"

def get_whoami():
    return f"{NAME}-{log.git_describe()}"

def log_whoami():
    log.log(get_whoami())