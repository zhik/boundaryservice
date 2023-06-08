from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
import psycopg2
import sqlalchemy as sa
from manage import setup, create_read_user
import json
import os
import pandas as pd

load_dotenv()  # for testing
with open("datasets.json", "r") as f:
    datasets = json.load(f)

DBNAME = os.environ["POSTGRES_DBNAME"]
USER = os.environ["POSTGRES_USER"]
PASS = os.environ["POSTGRES_PASS"]

admin_engine = sa.create_engine(f"postgresql://{USER}:{PASS}@postgres:5432/{DBNAME}")
read_only_engine = create_read_user(admin_engine, DBNAME)

app = Flask(__name__, template_folder="templates")
CORS(app)


@app.route("/")
def home():
    return render_template(
        "index.html", table_names=[dataset["name"] for dataset in datasets]
    )

@app.route("/query")
def query():
    lat = request.args.get('lat')
    lng = request.args.get('lng')
    bound = request.args.get('bound')
    dataset = next(dataset for dataset in datasets if dataset["name"] == bound)
    if dataset:
        # warp column in quotes
        intersects = pd.read_sql(f"""
            select {','.join([f'"{i}"' for i in dataset['columns']])} from {dataset['name']} 
            where ST_Intersects(ST_SetSRID(ST_MakePoint({lng}, {lat}), 4326), geometry)
        """, read_only_engine)
       

        return jsonify(intersects.to_dict(orient = 'records'))
    else:
        return jsonify({"success": False, "error": "dataset does not exist in the dataset"})


if __name__ == "__main__":
    setup(admin_engine, datasets)
    app.run(debug=True, host="0.0.0.0", port=5000)
