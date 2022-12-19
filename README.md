# rdb_exporter
This is a prometheus exporter for DBMS "Red Database".
# Exported metrics
<table>
  <tr>
    <th>Name</th>
    <th>Description</th>
    <th>Labels</th>
  </tr>
  <tr><td>[db_nickname]_db_size</td><td>The amount of database bytes which are taken to store data.</td><td>This metric does not have any label</td></tr>
  <tr><td>[db_nickname]_diff_oldt_nt</td><td>The difference between Oldest transaction number and Next transaction number.</td><td>This metric does not have any label</td></tr>
  <tr><td>[db_nickname]_active_users</td><td>The amount of active users in a database.</td><td>This metric does not have any label</td></tr>
  <tr><td>[db_nickname]_io_stats</td><td>The amount of read, written, fetched, marked pages of a database.</td><td><strong>stat_id, stat_group, type</strong></td></tr>
  <tr><td>[db_nickname]_used_memory</td><td>The amount of used memory bytes.</td><td>This metric does not have any label</td></tr>
</table>

# Exporter configuration file
You need to add a configuration json file beside "main.py" file and name it <strong>"exporter_conf"</strong> and fill it with a content.
<br>
The example of required content is:
```
{
  "port": 8000, 
  "login":  "SYSDBA", 
  "password":  "masterkey", 
  "databases": {
    "[db_nickname]": "localhost:[insert_path_to_database]",
    "[another_db_nickname]": "localhost:[insert_path_to_another_database]"
  }
  "utilities": "[insert_path_to_folder_with_utilities]"
}
```
<p><strong>Path to utilities folder must contain next following binary files:</strong></p>
<ul>
  <li>gstat</li>
  <li>isql</li>
</ul>

# Libraries
You need to install next following libraries to make the exporter work:
<ul>
  <li><strong>psutil</strong> (pip install psutil)</li>
</ul>
