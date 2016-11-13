import os
import yaml

from datetime import datetime

if os.environ.get("SECRET_KEY"):
    SECRET_KEY = os.environ.get("SECRET_KEY")
else:
    with open('main_app/app.yaml') as f:
        SECRET_KEY = yaml.load(f)["env_variables"]["SECRET_KEY"]


def get_secret_key():
    return SECRET_KEY


def valid_secret_key(request):
    return 'X-Secret-Key' in request.headers and request.headers["X-Secret-Key"] == get_secret_key()


def json_serial(obj):
    if isinstance(obj, datetime):
        serial = obj.isoformat()
        return serial
    raise TypeError("Type not serializable")


def json_deserial(pairs, format='%Y-%m-%dT%H:%M:%S'):
    d = {}
    for k, v in pairs:
        if isinstance(v, basestring):
            try:
                d[k] = datetime.strptime(v, format)
            except ValueError:
                d[k] = v
        else:
            d[k] = v
    return d