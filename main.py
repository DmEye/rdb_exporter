import os.path
import subprocess
from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer
import json

CONFIGURE = {}

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/metrics":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(self.scrape_db_size(CONFIGURE["databases"]["test_db"]).encode())
            self.wfile.write(self.scrape_transactions(CONFIGURE["utilities"]["gstat"], CONFIGURE["databases"]["test_db"]).encode())
            self.wfile.write(self.scrape_active_users(CONFIGURE["utilities"]["isql"], CONFIGURE["databases"]["test_db"], CONFIGURE["login"], CONFIGURE["password"]).encode())
        else:
            self.send_response(404)

    def scrape_db_size(self, path_to_database) -> str:
        db_size_in_bytes = 0
        if os.path.exists(path_to_database):
            db_size_in_bytes = os.path.getsize(path_to_database)
        return "reddatabase_db_size{} " + str(db_size_in_bytes) + "\n"

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
        return "RedDatabase_diff_oldt_nt{} " + str(difference_OLDT_NT) + "\n"

    def scrape_active_users(self, path_to_isql, path_to_database, login, password):
        with subprocess.Popen(path_to_isql, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                              shell=True) as isql:
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

        return "RedDatabase_active_users{} " + str(amount_of_active_users) + "\n"


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
        CONFIGURE = json.loads(file.readline().encode())
    run()

