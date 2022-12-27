import os.path
import subprocess
import json
import psutil
from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer
from sys import platform

CONFIGURE = {}


def decode_group(code):
    if code == 0:
        return "database"
    elif code == 1:
        return "connection"
    elif code == 2:
        return "transaction"
    elif code == 3:
        return "statement"
    elif code == 4:
        return "call"
    elif code == 5:
        return "cached_query"
    else:
        return "Unknown"


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
        response += self.scrape_mon_memory_usage(CONFIGURE["utilities"]["isql"], CONFIGURE["databases"][db_name], CONFIGURE["login"], CONFIGURE["password"]).replace("db_name", db_name)
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
                f"CONNECT '{path_to_database}' USER '{login}' PASSWORD '{password}'; select * from MON$IO_STATS; QUIT;".encode())
        out = out[0].decode("UTF-8")  # get the string
        out = out.split('\n')
        for i in range(out.count('')):
            out.remove('')
        del out[0]
        del out[0]
        IO_STATS = []
        for line in out:
            line = line.split()
            IO_STATS.append({"stat_id": line[0], "stat_group": decode_group(int(line[1])), "page_reads": line[2], "page_writes": line[3], "page_fetches": line[4], "page_marks": line[5]})

        response = ""

        for stat in IO_STATS:
            response += "db_name_io_stats{stat_id=\"" + stat["stat_id"] + "\",stat_group=\"" + stat["stat_group"] + "\",type=\"page_reads\"} " + stat["page_reads"] + "\n"
            response += "db_name_io_stats{stat_id=\"" + stat["stat_id"] + "\",stat_group=\"" + stat["stat_group"] + "\",type=\"page_writes\"} " + stat["page_writes"] + "\n"
            response += "db_name_io_stats{stat_id=\"" + stat["stat_id"] + "\",stat_group=\"" + stat["stat_group"] + "\",type=\"page_fetches\"} " + stat["page_fetches"] + "\n"
            response += "db_name_io_stats{stat_id=\"" + stat["stat_id"] + "\",stat_group=\"" + stat["stat_group"] + "\",type=\"page_marks\"} " + stat["page_marks"] + "\n"

        return response

    def scrape_memory(self) -> str:
        memory = psutil.virtual_memory()
        return "db_name_used_memory{} " + str(memory.total - memory.available) + "\n"

    def scrape_mon_memory_usage(self, path_to_isql, path_to_database, login, password) -> str:
        query = f"CONNECT '{path_to_database}' USER '{login}' PASSWORD '{password}'; select * from MON$MEMORY_USAGE; QUIT;"
        with subprocess.Popen(path_to_isql, stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True) as isql:
            out = isql.communicate(query.encode())
        out = out[0].decode("utf-8")
        out = out[0].decode("utf-8")
        out = out.split('\n')
        for i in range(out.count('')):
            out.remove('')
        del out[0]
        del out[0]
        MEMORY_USAGE = []
        for line in out:
            line = line.split()
            MEMORY_USAGE.append({"stat_id": line[0],
                                 "stat_group": decode_group(int(line[1])),
                                 "memory_used": line[2],
                                 "memory_allocated": line[3],
                                 "max_memory_used": line[4],
                                 "max_memory_allocated": line[5]})
        response = ""
        for stat in MEMORY_USAGE:
            response += "db_name_memory_usage{stat_id=\"%s\",stat_group=\"%s\",type=\"memory_used\"} %s\n" % (stat["stat_id"], stat["stat_group"], stat["memory_used"])
            response += "db_name_memory_usage{stat_id=\"%s\",stat_group=\"%s\",type=\"memory_allocated\"} %s\n" % (stat["stat_id"], stat["stat_group"], stat["memory_allocated"])
            response += "db_name_memory_usage{stat_id=\"%s\",stat_group=\"%s\",type=\"max_memory_used\"} %s\n" % (stat["stat_id"], stat["stat_group"], stat["max_memory_used"])
            response += "db_name_memory_usage{stat_id=\"%s\",stat_group=\"%s\",type=\"max_memory_allocated\"} %s\n" % (stat["stat_id"], stat["stat_group"], stat["max_memory_allocated"])
        return response


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
