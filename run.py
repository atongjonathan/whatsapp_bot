from . app import create_app
from threading import Thread

app = create_app()


def keep_alive():
    t = Thread(target=app.run(host="0.0.0.0", port=8000))
    t.start()

