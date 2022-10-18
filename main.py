import prometheus_client as pr
import os.path

EXPORTER_PORT = 10101
PATHS_TO_DATABASES = {"First db" : "C:\\REDSOFT\\TestDB.fdb"}

gauge_database_size = pr.Gauge("RedDatabase_db_size", "The amount of database bytes which are taken to store data.")

def scrape_db_size(path_to_database):
    if os.path.exists(path_to_database):
        db_size_in_bytes = os.path.getsize(path_to_database)
        gauge_database_size.set(db_size_in_bytes)

if __name__ == "__main__":
    pr.start_http_server(EXPORTER_PORT)
    while True:
        scrape_db_size(PATHS_TO_DATABASES["First db"])
