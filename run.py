import logging

from .app import create_app


app = create_app()
logging.basicConfig(format="SGBot | %(asctime)s | %(levelname)s | %(module)s | %(lineno)s | %(message)s", level=logging.INFO, handlers=[
    logging.StreamHandler(),
    logging.FileHandler("logs.txt")
])
logger = logging.getLogger(__name__)
logging.info("Whatsapp bot started")
# if __name__ == "__main__":
#     logging.info("Flask app started")
#     app.run(host="0.0.0.0", port=8000)
