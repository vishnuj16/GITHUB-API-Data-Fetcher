from flask import Flask, render_template, send_file
import os

def web():
    app = Flask(__name__)

    @app.route("/")
    def home():
        return render_template("home.html")

    @app.route("/download")
    def download():
        file_path = "data.csv"
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            return "Error: File not found."

    app.run(debug=True, port=8000)
