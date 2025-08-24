import logging
import os
from datetime import datetime

import psycopg2
from dotenv import load_dotenv
from flask import Flask, jsonify, request

# Load environment variables
load_dotenv()

# 로깅 설정
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Flask 로깅 설정
if not app.debug:
    import logging
    from logging.handlers import RotatingFileHandler

    if not os.path.exists("logs"):
        os.mkdir("logs")
    file_handler = RotatingFileHandler("logs/app.log", maxBytes=10240, backupCount=10)
    file_handler.setFormatter(
        logging.Formatter(
            "%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]"
        )
    )
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info("Application startup")


def get_db_connection():
    """데이터베이스 연결을 생성하고 반환합니다."""
    try:
        # Azure PostgreSQL 연결 문자열 사용
        connection_string = os.getenv("CUSTOMCONNSTR_AZURE_POSTGRESQL_CONNECTIONSTRING")

        if not connection_string:
            logger.error(
                "CUSTOMCONNSTR_AZURE_POSTGRESQL_CONNECTIONSTRING environment variable is not set"
            )
            return None

        logger.info(
            f"Attempting to connect with connection string: {connection_string[:50]}..."
        )
        connection = psycopg2.connect(connection_string)
        logger.info("Database connection successful")
        return connection
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        logger.error(f"Error type: {type(e).__name__}")
        return None


@app.route("/")
def home():
    return jsonify(
        {
            "message": "Hello from Azure App Service!",
            "timestamp": datetime.now().isoformat(),
            "environment": os.getenv("ENVIRONMENT", "development"),
        }
    )


@app.route("/health")
def health():
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})


@app.route("/api/echo", methods=["POST"])
def echo():
    data = request.get_json()
    return jsonify(
        {
            "message": "Echo response",
            "received_data": data,
            "timestamp": datetime.now().isoformat(),
        }
    )


@app.route("/api/info")
def info():
    return jsonify(
        {
            "app_name": "Simple Python Backend",
            "version": "1.0.0",
            "deployment_target": "Azure App Service",
            "timestamp": datetime.now().isoformat(),
        }
    )


@app.route("/api/db/test")
def test_db_connection():
    """데이터베이스 연결을 테스트합니다."""
    try:
        connection = get_db_connection()
        if connection is None:
            return jsonify(
                {
                    "status": "error",
                    "message": "Failed to connect to database",
                    "timestamp": datetime.now().isoformat(),
                }
            ), 500

        # 연결 테스트
        cursor = connection.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()

        cursor.close()
        connection.close()

        return jsonify(
            {
                "status": "success",
                "message": "Database connection successful",
                "database_version": version[0] if version else "Unknown",
                "timestamp": datetime.now().isoformat(),
            }
        )

    except Exception as e:
        return jsonify(
            {
                "status": "error",
                "message": f"Database test failed: {str(e)}",
                "timestamp": datetime.now().isoformat(),
            }
        ), 500


@app.route("/api/db/status")
def db_status():
    """데이터베이스 상태 정보를 반환합니다."""
    try:
        connection = get_db_connection()
        if connection is None:
            return jsonify(
                {
                    "database_connected": False,
                    "error": "Connection failed",
                    "timestamp": datetime.now().isoformat(),
                }
            )

        cursor = connection.cursor()

        # 데이터베이스 정보 수집
        cursor.execute("SELECT current_database(), current_user, version();")
        db_info = cursor.fetchone()

        cursor.close()
        connection.close()

        return jsonify(
            {
                "database_connected": True,
                "database_name": db_info[0],
                "current_user": db_info[1],
                "database_version": db_info[2],
                "timestamp": datetime.now().isoformat(),
            }
        )

    except Exception as e:
        return jsonify(
            {
                "database_connected": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }
        )


@app.route("/api/debug/env")
def debug_env():
    """환경변수 디버깅 정보를 반환합니다."""
    # 모든 환경변수 가져오기
    all_env_vars = dict(os.environ)

    # 민감한 정보 마스킹
    masked_env_vars = {}
    for key, value in all_env_vars.items():
        if any(
            sensitive in key.lower() or sensitive in value.lower()
            for sensitive in ["password", "secret", "key", "token"]
        ):
            masked_env_vars[key] = "*" * len(value) if value else ""
        else:
            masked_env_vars[key] = value

    connection_string = os.getenv("CUSTOMCONNSTR_AZURE_POSTGRESQL_CONNECTIONSTRING")
    return jsonify(
        {
            "has_connection_string": bool(connection_string),
            "connection_string_length": len(connection_string)
            if connection_string
            else 0,
            "connection_string_preview": connection_string[:50] + "..."
            if connection_string and len(connection_string) > 50
            else connection_string,
            "environment": os.getenv("ENVIRONMENT", "unknown"),
            "all_environment_variables": masked_env_vars,
            "timestamp": datetime.now().isoformat(),
        }
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
