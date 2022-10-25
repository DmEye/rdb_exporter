import prometheus_client as pr
import os.path

EXPORTER_PORT = 10101
PATHS_TO_DATABASES = {"First db" : "C:\\REDSOFT\\TestDB.fdb"}
PATHS_TO_UTILITIES = {"gstat" : "C:\\REDSOFT\\gstat.exe"}

gauge_database_size = pr.Gauge("RedDatabase_db_size", "The amount of database bytes which are taken to store data.")
gauge_diff_oldt_nt_size = pr.Gauge("RedDatabase_diff_oldt_nt", "The difference between Oldest transaction number and Next transaction numbers.")

def scrape_db_size(path_to_database):
    if os.path.exists(path_to_database):
        db_size_in_bytes = os.path.getsize(path_to_database)
        gauge_database_size.set(db_size_in_bytes)

def scrape_transactions(path_to_gstat, path_to_database):
    out = subprocess.run([path_to_gstat, '-h', path_to_database], capture_output=True).stdout
    out = [row.replace('\r', '') for row in str(out, encoding="UTF-8").split('\n')]
    for i in range(out.count('')):
        out.remove('')
    out = [row[1:] for row in out]
    p = {}
    for row in out:
        buffer = row.split('\t')
        p[buffer[0]] = buffer[-1]
    del out
    difference_OLDT_NT = int(p["Next transaction"]) - int(p["Oldest transaction"])
    gauge_diff_oldt_nt_size.set(difference_OLDT_NT)
    


if __name__ == "__main__":
    pr.start_http_server(EXPORTER_PORT)
    while True:
        scrape_db_size(PATHS_TO_DATABASES["First db"])
        scrape_transactions(PATHS_TO_UTILITIES["gstat"], PATHS_TO_DATABASES["First db"])
