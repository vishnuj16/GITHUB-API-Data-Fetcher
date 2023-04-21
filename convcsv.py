import csv
import json

def writecsv(json_list):
    csv_file = "data.csv"
    csv_headers = ["Owner ID", "Owner Name", "Owner Email", "Repo ID", "Repo Name", "Status", "Stars Count"]

    # open the CSV file for writing
    with open(csv_file, mode="w", newline="") as file:
        # create a CSV writer object
        writer = csv.DictWriter(file, fieldnames=csv_headers)

        # write the CSV headers
        writer.writeheader()

        # write the data from the JSON strings to the CSV file
        for json_string in json_list:
            # parse the JSON string
            data = json.loads(json_string)

            # write the data to the CSV file
            writer.writerow(data)