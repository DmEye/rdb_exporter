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
</table>

# Exporter configuration file
You need to add a configuration json file beside "main.py" file and name it "exporter_conf" and fill it with an content.
<br>
The example of required content is:
```
{
  "port": 8000, 
  "login":  "SYSDBA", 
  "password":  "masterkey", 
  "databases": {
    "test_db": "localhost:[insert_path_to_database]"
  },
  "utilities": {
    "gstat":  "[insert_path_to_gstat]",
    "isql": "[insert_path_to_isql]"
  }
}
```
