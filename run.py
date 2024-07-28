import logging

from . app import create_app
from threading import Thread

app = create_app()
logging.basicConfig(format="SGBot | %(asctime)s | %(levelname)s | %(module)s | %(lineno)s | %(message)s", level=logging.INFO, handlers=[
    logging.StreamHandler(),
    logging.FileHandler("logs.txt")
])
logger = logging.getLogger(__name__)
logging.info("Whatsapp bot started")


def keep_alive():
    t = Thread(target=app.run(host="0.0.0.0", port=8000))
    t.start()


if __name__ == "__main__":
    logging.info("Flask app started")
    keep_alive()
