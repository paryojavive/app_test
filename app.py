from flask import Flask, jsonify, request
import os
from datetime import datetime

app = Flask(__name__)


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


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
