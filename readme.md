A quick demo on setting up postgis and a flask api to query to bounds.

# Setup 
`docker-compose up`

### Todo
- create a read only user
- a better way to query for bounds? 
- I use geopandas for convince to query and upload data but that can largely be removed and replaced by ogr2ogr and psycopg2
- add a param for geojson returns using `st_asgeojson(geometry)`