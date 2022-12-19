import os.path
import subprocess
import json
import psutil
from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer
from sys import platform

CONFIGURE = {}


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/metrics":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            response = ""
            for database in CONFIGURE["databases"]:
                response += self.scrape(database)
            self.wfile.write(response.encode())
        else:
            self.send_response(404)

    def scrape(self, db_name) -> str:
        response = ""
        response += self.scrape_db_size(CONFIGURE["databases"][db_name]).replace("db_name", db_name)
        response += self.scrape_transactions(CONFIGURE["utilities"]["gstat"], CONFIGURE["databases"][db_name]).replace("db_name", db_name)
        response += self.scrape_active_users(CONFIGURE["utilities"]["isql"], CONFIGURE["databases"][db_name], CONFIGURE["login"],CONFIGURE["password"]).replace("db_name", db_name)
        response += self.scrape_mon_io_stats(CONFIGURE["utilities"]["isql"], CONFIGURE["databases"][db_name], CONFIGURE["login"], CONFIGURE["password"]).replace("db_name", db_name)
        response += self.scrape_memory().replace("db_name", db_name)
        return response

    def scrape_db_size(self, path_to_database) -> str:
        db_size_in_bytes = 0
        path_to_db = path_to_database.split(':')[1]
        if os.path.exists(path_to_db):
            db_size_in_bytes = os.path.getsize(path_to_db)
        return "db_name_db_size{} " + str(db_size_in_bytes) + "\n"

    def scrape_transactions(self, path_to_gstat, path_to_database) -> str:
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
        return "db_name_diff_oldt_nt{} " + str(difference_OLDT_NT) + "\n"

    def scrape_active_users(self, path_to_isql, path_to_database, login, password) -> str:
        with subprocess.Popen(path_to_isql, stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True) as isql:
            out = isql.communicate(
                f"CONNECT '{path_to_database}' USER '{login}' PASSWORD '{password}'; SHOW USERS; QUIT;".encode())
        out = out[0].decode("UTF-8")  # get the string
        # extracting data
        out = out.split('\n')
        del out[0]  # remove header
        del out[-1]  # remove empty string

        amount_of_active_users = 0
        for record in out:
            active = int(record.split()[0])
            amount_of_active_users += active

        return "db_name_active_users{} " + str(amount_of_active_users) + "\n"

    def scrape_mon_io_stats(self, path_to_isql, path_to_database, login, password) -> str:
        with subprocess.Popen(path_to_isql, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                              shell=True) as isql:
            out = isql.communicate(
                f"CONNECT '{path_to_database}' USER '{login}' PASSWORD '{password}'; select * from MON$IO_STATS WHERE MON$STAT_GROUP = 0; QUIT;".encode())
        out = out[0].decode("UTF-8")  # get the string
        out = out.split('\n')
        for i in range(out.count('')):
            out.remove('')
        del out[0]
        del out[0]
        out = out[0].split()
        READS = out[2]
        WRITES = out[3]
        FETCHES = out[4]
        MARKS = out[5]

        response = "db_name_mon_reads{} " + READS + "\ndb_name_mon_writes{} " + WRITES + "\ndb_name_mon_fetches{} " + FETCHES + "\ndb_name_mon_marks{} " + MARKS + "\n"
        return response

    def scrape_memory(self) -> str:
        memory = psutil.virtual_memory()
        return "db_name_used_memory{} " + str(memory.total - memory.available) + "\n"


def run(server_class=HTTPServer, handler_class=Handler):
    server_address = ('', CONFIGURE["port"])
    httpd = server_class(server_address, handler_class)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.server_close()


if __name__ == "__main__":
    # Parsing
    with open("./exporter_conf.json", "r") as file:
        CONFIGURE = json.loads("".join(list(map(lambda line: line.replace("\n", ""), file.readlines()))))

    # Editing
    utilities_path = CONFIGURE["utilities"]
    if platform == "linux" or platform == "linux2":
        if utilities_path[-1] != "/":
            utilities_path += "/"
        CONFIGURE["utilities"] = {
            "gstat": utilities_path + "gstat",
            "isql": utilities_path + "isql"
        }
    elif platform == "win32":
        if utilities_path[-1] != "\\":
            utilities_path += "\\"
        CONFIGURE["utilities"] = {
            "gstat": utilities_path + "gstat.exe",
            "isql": utilities_path + "isql.exe"
        }

    run()