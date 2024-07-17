from flask import Flask, request, jsonify
import os
import datetime

# from utils import get_scanned_barcodes
import sys

app = Flask(__name__)


try:
    wd = sys._MEIPASS
except AttributeError:
    wd = os.getcwd()


# Function to create directory for today's date if it doesn't exist
def create_directory_if_not_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


@app.route("/scans", methods=["POST"])
def process_scans():
    try:
        data = request.get_data().decode("utf-8")
        # data = request.get_json()

        # Assuming the body contains a list of scan data
        scans = data

        # Create a directory with today's date
        today_date = datetime.date.today().strftime("%Y-%m-%d")
        directory = os.path.join(wd, today_date)
        print("directory", directory)
        create_directory_if_not_exists(directory)

        # Write the scans to a file within today's directory
        filename = os.path.join(directory, "scans.txt")
        print("filename", filename)
        with open(filename, "a") as file:
            file.write(f"{scans}\n")

        return jsonify({"message": "Scans received and saved successfully"}), 200

    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 400


@app.route("/getall", methods=["GET"])
def get_all():
    try:
        data = get_scanned_barcodes()

        return (
            jsonify({"message": "Scans received and saved successfully", "data": data}),
            200,
        )

    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 400


def run_flask(port=5001, host="0.0.0.0"):
    app.run(port=port, debug=False, host=host)
