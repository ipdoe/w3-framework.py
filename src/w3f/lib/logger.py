import datetime, json, git, sys, os

def func_name(n=0):
    return sys._getframe(n + 1).f_code.co_name

def _internal_slog(msg, n=1):
    return f'[{datetime.datetime.now()}] [{func_name(n + 1)}] {msg}'

def _internal_log(msg, n=1):
    print(_internal_slog(msg, n + 1))

def slog(msg):
    return _internal_slog(msg)

def log(msg):
    _internal_log(msg)

def log_json(msg):
    try:
        _internal_log(json.dumps(msg, indent=2))
    except:
        _internal_log(msg)

def to_json_str(msg):
    try:
        return json.dumps(msg, indent=2)
    except:
        return ""

def log_version():
    _internal_log(f'{os.path.basename(sys.argv[0])}-{git_describe()}')

def git_describe():
    return git.cmd.Git().describe(tags=True, dirty=True)

class LogLatch:
    def __init__(self, limit=3) -> None:
        self.limit = limit
        self.consecutive = 0

    def log(self, msg):
        if (not self.reached_limit()):
            _internal_log(msg)

        self.consecutive = self.consecutive + 1

    def reset(self):
        self.consecutive = 0

    def reached_limit(self):
        return self.consecutive > self.limit