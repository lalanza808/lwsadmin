from lws.factory import create_app
from lws import config

run = create_app().run(host=config.HOST, port=config.PORT)
