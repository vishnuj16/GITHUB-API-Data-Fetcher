from app.main import app
import webbrowser
from threading import Timer

def open_browser():
    url = "http://localhost:8000"
    webbrowser.open_new(url)


if __name__ == "__main__":
    Timer(1, open_browser).start()
    app.run(port=8000)