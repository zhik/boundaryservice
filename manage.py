import pandas as pd
import geopandas as gpd
import urllib.request
from urllib.parse import urlparse
import os
import shutil


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


def setup(engine, datasets):
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
