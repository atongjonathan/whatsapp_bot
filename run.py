from logging import basicConfig, INFO, StreamHandler, FileHandler

from . app import create_app
from threading import Thread

app = create_app()
basicConfig(format="SGWABot | %(asctime)s | %(levelname)s | %(module)s | %(lineno)s | %(message)s", level=INFO, handlers=[
    StreamHandler(),
    FileHandler("logs.txt")
])


def keep_alive():
    t = Thread(target=app.run(host="0.0.0.0", port=8000))
    t.start()

