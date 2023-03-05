import w3f.lib.logger as log

NAME = "w3f"

def get_whoami(name = None):
    if name is None:
        name = NAME
    return f"{name}-{log.git_describe()}"

def log_whoami(name = None):
    log.log(get_whoami(name))