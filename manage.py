import pandas as pd
import geopandas as gpd
import urllib.request
from urllib.parse import urlparse
import os
import shutil
from dotenv import load_dotenv
from sqlalchemy import text
import sqlalchemy as sa

load_dotenv()  # for testing


def remove_files_in_folder(folder_path):
    for file_name in os.listdir(folder_path):
        os.remove(f"{folder_path}/{file_name}")


def read_dataset(dataset):
    # download
    file_name = "./tmp/" + dataset["file_name"]
    urllib.request.urlretrieve(dataset["source"], file_name)
    # todo deal with zips. geojson exported from arcgis/ bytes have a limit of 100 polygons
    df = gpd.read_file(file_name)
    # clean up
    return df

def create_read_user(engine, DBNAME):
    # Create a ready only user
    query = f"""
    DROP USER IF EXISTS read;

    CREATE USER read WITH PASSWORD 'read';
    GRANT USAGE ON SCHEMA public TO read;
    GRANT SELECT ON ALL TABLES IN SCHEMA public TO read;
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO read;

    """
    print('creating user "read"')
    with engine.connect() as con:
        con.execute(text(query))
    return sa.create_engine(f"postgresql://read:read@postgres:5432/{DBNAME}")

def setup(engine, datasets):
    if not os.path.exists('./tmp'):
        os.makedirs('./tmp')

    # setup database if items don't exist
    for dataset in datasets:
        query = f"""SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = '{dataset["name"]}')"""
        table_exists = pd.read_sql(query, engine)
        if table_exists.iloc[0, 0]:
            print(f"table {dataset['name']} already exists")
        else:
            print(f"creating {dataset['name']}")
            read_dataset(dataset).to_postgis(
                dataset["name"], engine, index=False, if_exists="replace"
            )
            # todo: create spatial index
    remove_files_in_folder("./tmp")


if __name__ == "__main__":
    df = read_dataset(
        {
            "name": "nycc_23b",
            "source": "https://services5.arcgis.com/GfwWNkhOj9bNBqoJ/arcgis/rest/services/NYC_City_Council_Districts_Water_Included/FeatureServer/0/query?where=1=1&outFields=*&outSR=4326&f=pgeojson",
            "file_name": "nycc_23b.geojson",
        }
    )
    print(df)
