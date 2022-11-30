# rdb_exporter
This is an prometheus exporter for DBMS "Red Database".
# Exported metrics
<table>
  <tr>
    <th>Name</th>
    <th>Description</th>
  </tr>
  <tr><td>reddatabase_db_size</td><td>The amount of database bytes which are taken to store data.</td></tr>
  <tr><td>RedDatabase_diff_oldt_nt</td><td>The difference between Oldest transaction number and Next transaction number.</td></tr>
  <tr><td>RedDatabase_active_users</td><td>The amount of active users in a database. (Note: you need to have an administrator rights to extract this metric)</td></tr>
  <tr><td>RedDatabase_mon_reads</td><td>Quantity read (read) pages bases data.</td></tr>
  <tr><td>RedDatabase_mon_writes</td><td>Quantity recorded (write) pages bases data.</td></tr>
  <tr><td>RedDatabase_mon_fetches</td><td>Quantity loaded in memory (fetch) pages bases data.</td></tr>
</table>

# Exporter configuration file
You need to add a configuration json file beside "main.py" file and name it "exporter_conf" and fill it with a content.
<br>
The example of required content is:
```
{
  "port": 8000, 
  "login":  "SYSDBA", 
  "password":  "masterkey", 
  "databases": "localhost:[insert_path_to_database]",
  "utilities": "insert_path_to_folder_with_utilities"
}
```
Path to utilities is that path wich has binaries files of next following utilities:
1. gstat
2. isql
