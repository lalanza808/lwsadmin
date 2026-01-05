from os import environ as env
from secrets import token_urlsafe
from dotenv import load_dotenv

DEBUG = 1 == env.get("DEBUG", 1)
if DEBUG:
    load_dotenv()

HOST = env.get("HOST", "127.0.0.1")
PORT = env.get("PORT", 5000)
TEMPLATES_AUTO_RELOAD = True
QUART_ENV = env.get("QUART_ENV", "development")
SECRET_KEY = env.get("SECRET_KEY", token_urlsafe(12))
SERVER_NAME = env.get("SERVER_NAME", f"127.0.0.1:{PORT}")
QUART_AUTH_DURATION = int(env.get('QUART_AUTH_DURATION', 60 * 60))    # 1 hour

# LWS
LWS_URL = env.get("LWS_URL", "http://127.0.0.1:8080")
LWS_ADMIN_URL = env.get("LWS_ADMIN_URL", "http://127.0.0.1:8081")

# Monerod
MONEROD_URL = env.get("MONEROD_URL", "http://singapore.node.xmr.pm:18089")

# MyMonero
MYMONERO_URL = env.get("MYMONERO_URL", "http://localhost:9110")