import os, time
import psycopg2
from flask import Flask, jsonify

app = Flask(__name__)

DB_HOST = os.getenv("DB_HOST", "postgres")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_NAME = os.getenv("POSTGRES_DB", "appdb")
DB_USER = os.getenv("POSTGRES_USER", "appuser")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "")

def db_conn():
    return psycopg2.connect(
        host=DB_HOST, port=DB_PORT,
        dbname=DB_NAME, user=DB_USER, password=DB_PASS,
        connect_timeout=2
    )

@app.get("/healthz")
def healthz():
    return "ok", 200

@app.get("/readyz")
def readyz():
    try:
        with db_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1;")
                cur.fetchone()
        return "ready", 200
    except Exception as e:
        return f"not ready: {e}", 503

@app.get("/api/info")
def info():
    data = {"time": time.time(), "db_host": DB_HOST, "db_name": DB_NAME}
    try:
        with db_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT version();")
                data["db_version"] = cur.fetchone()[0]
    except Exception as e:
        data["db_error"] = str(e)
    return jsonify(data), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)

