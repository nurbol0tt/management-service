import os
import sys
from twisted.python import log
from app.api.api import app

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    log.startLogging(sys.stdout)
    port = int(os.getenv("PORT", 8080))

    app.run("0.0.0.0", port)


if __name__ == "__main__":
    main()
