from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
import psycopg2
import sqlalchemy as sa
from manage import setup
import json
import os

load_dotenv()  # for testing
with open("datasets.json", "r") as f:
    datasets = json.load(f)

DBNAME = os.environ["POSTGRES_DBNAME"]
USER = os.environ["POSTGRES_USER"]
PASS = os.environ["POSTGRES_PASS"]

engine = sa.create_engine(f"postgresql://{USER}:{PASS}@postgres:5432/{DBNAME}")
app = Flask(__name__, template_folder="templates")
CORS(app)


@app.route("/")
def home():
    return render_template(
        "index.html", table_names=[dataset["name"] for dataset in datasets]
    )


if __name__ == "__main__":
    setup(engine, datasets)
    app.run(debug=True, host="0.0.0.0", port=5000)
