import os
import sys
from twisted.python import log
from app.api.api import app

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    log.startLogging(sys.stdout)
    port = int(os.getenv("PORT", 8080))

    print(f"Starting Configuration Management Service on port {port}")
    print("Available endpoints:")
    print("  GET  /                          - API info")
    print("  POST /config/{service}          - Upload configuration")
    print("  GET  /config/{service}          - Get configuration")
    print("  GET  /config/{service}/history  - Get configuration history")

    app.run("0.0.0.0", port)


if __name__ == "__main__":
    main()
