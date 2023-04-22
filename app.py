from flask import Flask, render_template, Response
import os
import io
import csv

def web(deduplicated_data):
    app = Flask(__name__)

    @app.route("/")
    def home():
        return render_template("home.html")

    @app.route("/download")
    def download():
        
        csv_buffer = io.StringIO()
        writer = csv.writer(csv_buffer)
        writer.writerow(['owner_id', 'owner_name', 'owner_email', 'repo_id', 'repo_name', 'repo_status', 'stars_count'])
        for row in deduplicated_data:
            writer.writerow([row['owner_id'], row['owner_name'], row['owner_email'], row['repo_id'], row['repo_name'], row['repo_status'], row['stars_count']])
        
        # Set the filename and headers for the response
        filename = 'output.csv'
        headers = {
            'Content-Disposition': f'attachment; filename="{filename}"',
            'Content-Type': 'text/csv'
        }

        # Return the CSV file as a response with the appropriate headers
        return Response(
            csv_buffer.getvalue(),
            headers=headers,
            mimetype='text/csv'
        )

    app.run(port=8000)
