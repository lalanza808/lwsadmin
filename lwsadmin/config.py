from os import environ as env

from dotenv import load_dotenv

load_dotenv()

# Flask details
HOST = env.get("HOST", "127.0.0.1")
PORT = env.get("PORT", 5000)
SERVER_NAME = env.get("SERVER_NAME", f"127.0.0.1:{PORT}")
TEMPLATES_AUTO_RELOAD = True
FLASK_ENV = env.get("FLASK_ENV", "development")
SECRET_KEY = env.get("SECRET_KEY", "secretkey")
FLASK_AUTH_DURATION = int(env.get("FLASK_AUTH_DURATION", 60 * 60))    # 1 hour

# LWS API
LWS_URL = env.get("LWS_URL", "http://127.0.0.1:8080")
LWS_ADMIN_URL = env.get("LWS_ADMIN_URL", "http://127.0.0.1:8081")

# Monerod RPC
MONEROD_URL = env.get("MONEROD_URL", "http://127.0.0.1:18081")

# Database
DB_HOST = env.get("DB_HOST", "localhost")
DB_PORT = env.get("DB_PORT", 5432)
DB_NAME = env.get("DB_NAME", "lwsadmin")
DB_USER = env.get("DB_USER", "lwsadmin")
DB_PASS = env.get("DB_PASS", "lwsadmin")
DB_URI = "postgresql+psycopg2://{user}:{pw}@{host}:{port}/{db}".format(
    user=DB_USER,
    pw=DB_PASS,
    host=DB_HOST,
    port=DB_PORT,
    db=DB_NAME
)

# Cache
CACHE_HOST = env.get("CACHE_HOST", "localhost")
CACHE_PORT = env.get("CACHE_PORT", 6379)
