import os
from datetime import datetime

import psycopg2
from dotenv import load_dotenv
from flask import Flask, jsonify, request

# Load environment variables
load_dotenv()

app = Flask(__name__)


def get_db_connection():
    """데이터베이스 연결을 생성하고 반환합니다."""
    try:
        # Azure PostgreSQL 연결 문자열 사용
        connection_string = os.getenv("CUSTOMCONNSTR_AZURE_POSTGRESQL_CONNECTIONSTRING")

        if not connection_string:
            print(
                "CUSTOMCONNSTR_AZURE_POSTGRESQL_CONNECTIONSTRING environment variable is not set"
            )
            return None

        print(
            f"Attempting to connect with connection string: {connection_string[:50]}..."
        )
        connection = psycopg2.connect(connection_string)
        print("Database connection successful")
        return connection
    except Exception as e:
        print(f"Database connection error: {e}")
        print(f"Error type: {type(e).__name__}")
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


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
