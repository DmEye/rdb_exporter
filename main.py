
import json
from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer
from sys import platform
from scrapers import *
import firebirdsql

CONFIGURE = {}


def close_connections():
    for connection in CONFIGURE["connections"]:
        CONFIGURE["connections"][connection].close()


def scrape(db_name) -> str:
    response = ""
    cursor = CONFIGURE["connections"][db_name].cursor()
    response += scrape_mon_database(cursor, db_name)
    response += scrape_mon_attachments(cursor, db_name)
    response += scrape_mon_transactions(cursor, db_name)
    response += scrape_mon_statements(cursor, db_name)
    response += scrape_mon_io_stats(cursor, db_name)
    response += scrape_mon_memory_usage(cursor, db_name)
    response += scrape_mon_call_stack(cursor, db_name)
    response += scrape_mon_record_stats(cursor, db_name)
    response += scrape_mon_table_stats(cursor, db_name)
    response += scrape_transactions_params(CONFIGURE["RedDatabase"]["gstat"], CONFIGURE["databases"][db_name], db_name)
    response += scrape_db_size(CONFIGURE["databases"][db_name], cursor, db_name)
    response += scrape_trace(db_name)

    cursor.close()
    return response


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/metrics":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            response = ""
            response += scrape_system_metrics(CONFIGURE)
            for database in CONFIGURE["databases"]:
                response += scrape(database)
                CONFIGURE["connections"][database].commit()
            self.wfile.write(response.encode())
        else:
            self.send_response(404)


def run(server_class=HTTPServer, handler_class=Handler):
    server_address = ('', CONFIGURE["port"])
    httpd = server_class(server_address, handler_class)
    try:
        CONFIGURE["trace_thread"].start()
        httpd.serve_forever()
    except KeyboardInterrupt:
        close_connections()
        httpd.server_close()
        print("Exporter has been closed")


if __name__ == "__main__":
    # Parsing
    with open("./exporter_conf.json", "r") as file:
        CONFIGURE = json.loads("".join(list(map(lambda line: line.replace("\n", ""), file.readlines()))))

    # Editing
    rdb_path = CONFIGURE["RedDatabase"]
    if platform == "linux" or platform == "linux2":
        if rdb_path[-1] != "/":
            rdb_path += "/"
        CONFIGURE["RedDatabase"] = {
            "gstat": rdb_path + "bin/gstat",
            "isql": rdb_path + "bin/isql",
            "rdbtracemgr": rdb_path + "bin/rdbtracemgr",
            "trace_conf": rdb_path + "fbtrace.conf"
        }
        CONFIGURE["mountpoints"] = [disk.mountpoint for disk in psutil.disk_partitions()]
    elif platform == "win32":
        if rdb_path[-1] != "\\":
            rdb_path += "\\"
        CONFIGURE["RedDatabase"] = {
            "gstat": rdb_path + "gstat.exe",
            "isql": rdb_path + "isql.exe",
            "rdbtracemgr": rdb_path + "rdbtracemgr.exe",
            "trace_conf": rdb_path + "fbtrace.conf"
        }
    else:
        print("This OS is not supported")
        exit(1)

    # Creating thread of extracting trace procedure
    CONFIGURE["trace_thread"] = threading.Thread(target=extract_trace, kwargs={
        "rdbtracemgr": CONFIGURE["RedDatabase"]["rdbtracemgr"],
        "trace_config": CONFIGURE["RedDatabase"]["trace_conf"],
        "login": CONFIGURE["login"],
        "password": CONFIGURE["password"]
    }, daemon=True)

    # Opening connections
    try:
        CONFIGURE["connections"] = {}
        for database in CONFIGURE["databases"]:
            conf = CONFIGURE["databases"][database]
            CONFIGURE["connections"][database] = firebirdsql.connect(
                host=conf.split(':')[0],
                database=conf.split(':')[1],
                port=CONFIGURE["RDB_port"],
                user=CONFIGURE["login"],
                password=CONFIGURE["password"]
            )
    except:
        close_connections()
        exit(1)
    run()
