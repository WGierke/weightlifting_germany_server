import os
import yaml

if os.environ.get("SECRET_KEY"):
    SECRET_KEY = os.environ.get("SECRET_KEY")
else:
    with open('germany_app_engine/app.yaml') as f:
        SECRET_KEY = yaml.load(f)["env_variables"]["SECRET_KEY"]


def valid_secret_key(request):
    return 'X-Secret-Key' in request.headers and request.headers["X-Secret-Key"] == SECRET_KEY
