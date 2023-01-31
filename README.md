# rdb_exporter
This is a prometheus exporter for DBMS "Red Database".
# Exported metrics
<table>
  <tr>
    <th>Name</th>
    <th>Description</th>
  </tr>
  <tr><td>db_size</td><td>The amount of database bytes which are taken to store data.</td></tr>
  <tr><td>diff_oldt_nt</td><td>The difference between Oldest transaction number and Next transaction number.</td></tr>
  <tr><td>active_users</td><td>The amount of active users in a database.</td></tr>
  <tr><td>mon_io_stats</td><td>The amount of read, written, fetched, marked pages of a database/connections/transactions/statements/calls.</td></tr>
  <tr><td>mon_memory_usage</td><td>Information about memory usage by database/connections/transactions/statements/calls/cached_queries</td></tr>
  <tr>
    <td>mon_database</td><td>Information about a database:
      <ul>
        <li><b>oldest_snapshot</b>: The number of the transaction that was active at the moment when the OAT was started — oldest snapshot transaction (OST)</li>
        <li><b>next_transaction</b>: The number of the next transaction, as it stood when the monitoring snapshot was taken</li>
        <li><b>oldest_transaction</b>: The number of the oldest [interesting] transaction (OIT)</li>
        <li><b>oldest_active</b>: The number of the oldest active transaction (OAT)</li>
        <li><b>page_buffers</b>: The number of pages allocated in RAM for the database page cache</li>
        <li><b>SQL_dialect</b>: Database SQL Dialect: 1 or 3</li>
        <li><b>shutdown_mode</b>: The current shutdown state of the database: <br>0 - the database is online <br>1 - multi-user shutdown <br>2 - single-user shutdown <br>3 - full shutdown</li>
        <li><b>sweep_interval</b>: sweep interval</li>
        <li><b>read_only</b>: Flag indicating whether the database is read-only (value 1) or read-write (value 0)</li>
        <li><b>forced_writes</b>: Indicates whether the write mode of the database is set for synchronous write (forced writes ON, value is 1) or asynchronous write (forced writes OFF, value is 0)</li>
        <li><b>reserve_space</b>: The flag indicating reserve_space (value 1) or use_all_space (value 0) for filling database pages</li>
        <li><b>pages</b>: The number of pages allocated for the database on an external device</li>
        <li><b>crypt_page</b>: Number of encrypted pages</li>
      </ul>
    </td>
  </tr>
  <tr>
    <td>mon_attachment</td><td>Displays information about active attachments to the database:
      <ul>
        <li><b>server_pid</b>: Server process identifier</li>
        <li><b>state</b>: Connection state: <br>0 - idle <br>1 - active</li>
        <li><b>remote_pid</b>: Remote client process identifier</li>
        <li><b>character_set_id</b>: Connection character set identifier (see RDB$CHARACTER_SET in system table RDB$TYPES)</li>
        <li><b>garbage_collection</b>: Garbage collection flag (as specified in the attachment’s DPB): <br>1=allowed, <br>0=not allowed</li>
        <li><b>system_flag</b>: Flag that indicates the type of connection: <br>0 - normal connection <br>1 - system connection</li>
        <li><b>repl_waitflush_count</b>: Number of packets sent to reserve databases.</li>
        <li><b>repl_waitflush_time</b>: Time (in ms) that the main server waits for a response from backup servers.</li>
      </ul>
    </td>
  </tr>
  <tr>
    <td>mon_transaction</td><td>Reports started transactions:
    <ul>
      <li><b>attachment_id</b>: Connection identifier</li>
      <li><b>state</b>: Transaction state: <br>0 - idle <br>1 - active</li>
      <li><b>top_transaction</b>: Top-level transaction identifier (number)</li>
      <li><b>oldest_transaction</b>: Transaction ID of the oldest [interesting] transaction (OIT)</li>
      <li><b>oldest_active</b>: Transaction ID of the oldest active transaction (OAT)</li>
      <li><b>isolation_mode</b>: Isolation mode (level): <br>0 - consistency (snapshot table stability) <br>1 - concurrency (snapshot) <br>2 - read committed record version <br>3 - read committed no record version</li>
      <li><b>lock_timeout</b>: Lock timeout: <br>-1 - wait forever <br>0 - no waiting <br>1 or greater - lock timeout in seconds</li>
      <li><b>read_only</b>: Flag indicating whether the transaction is read-only (value 1) or read-write (value 0)</li>
      <li><b>auto_commit</b>: Flag indicating whether automatic commit is used for the transaction (value 1) or not (value 0)</li>
      <li><b>auto_undo</b>: Flag indicating whether the logging mechanism automatic undo is used for the transaction (value 1) or not (value 0)</li>
    </ul>
    </td>
  </tr>
  <tr>
    <td>mon_statement</td><td>Displays statements prepared for execution:
      <ul>
        <li><b>attachment_id</b>: Connection identifier</li>
        <li><b>transaction_id</b>: Transaction identifier</li>
        <li><b>state</b>: Statement state: <br>0 - idle <br>1 - active <br>2 - stalled</li>
      </ul>
    </td>
  </tr>
  <tr>
    <td>mon_call_stack</td><td>Displays calls to the stack from queries executing in stored procedures and triggers:
      <ul>
        <li><b>statement_id</b>: The identifier of the top-level SQL statement, the one that initiated the chain of calls. Use this identifier to find the records about the active statement in the MON$STATEMENTS table</li>
        <li><b>caller_id</b>: The identifier of the calling trigger or stored procedure</li>
        <li><b>source_line</b>: The number of the source line in the SQL statement being executed at the moment of the snapshot</li>
        <li><b>source_column</b>: The number of the source column in the SQL statement being executed at the moment of the snapshot</li>
      </ul>
    </td>
  </tr>
  <tr>
    <td>system_memory</td>
    <td>
      Information about device RAM:
      <ul>
        <li><b>used</b>: The amount of used memory by OS and other applications</li>
        <li><b>available</b>: The amount of available memory</li>
        <li><b>total</b>: The amount of memory which is had by device</li>
      </ul>
    </td>
  </tr>
  <tr>
    <td>system_cpu</td>
    <td>
      Information about cpu usage:
      <ul>
        <li><b>percent</b>: CPU load</li>
        <li><b>frequency</b>: CPU frequency</li>
      </ul>
    </td>
  </tr>
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
  "RDB_port": 3050,
  "utilities": "/opt/RedDatabase/bin"
  "databases": {
    "[db_nickname]": "localhost:[insert_path_to_database]",
    "[another_db_nickname]": "localhost:[insert_path_to_another_database]"
  }
}
```

# Prometheus configuration file
Prometheus can be configured from either a terminal and a configuration file. The most important settings are from which node prometheus scrapes metrics and time between two scrape queries.
The example content of prometheus configuration file:
```
global:
  scrape_interval: 10s # Time between two scrape queries

scrape_configs:
  - job_name: "RedDatabases"
    static_configs:
      - targets: ["localhost:8000"] # A node where exporter is located
```

# Libraries
You need to install next following libraries to make the exporter work:
<ul>
  <li><strong>psutil</strong> version 5.9.4 (pip install psutil==5.9.4)</li>
  <li><strong>firebirdsql</strong> version 1.2.2 (pip install firebirdsql==1.2.2)</li>
</ul>

# How to use
<ol>
  <li>Install python, <a href="#libraries">libraries</a>, Prometheus, Grafana, Exporter;</li>
  <li>Launch RedDatabase server;</li>
  <li>Edit <a href="#exporter-configuration-file">exporter configuration file</a>;</li>
  <li>Launch this exporter (python main.py);</li>
  <li>Edit <a href="#prometheus-configuration-file">Prometheus configuration file</a>;</li>
  <li>Launch prometheus;</li>
  <li>Launch Grafana (on linux: <i>sudo systemctl start grafana-server</i>). It might be on 3000 port now;</li>
  <li>Open browser and insert into address section the next following string "http://localhost:3000/";</li>
  <li>Enter login and password to sign in. The string "admin" is default login and password. Grafana make you change default password when you have signed in for the first time;</li>
  <li>Make a data source. To do it you must go to left side of screen and find a gear picture (configure section) then click on the "Data sources" subsection. Now click the button "add data source, select Prometheus, insert url path to prometheus (default is "<b>http://localhost:9090/</b>")", click the button "Save & test";</li>
  <li>Import dashboards or build your own. To import dashboards you must find the "Dashboards" section at the left side of the screen and click the "+ Import" button. Click the button "Upload JSON file" and select json file of a dashboard, click "Import". To build your own dashboard follow instructions at <a href="https://grafana.com/docs/grafana/latest/getting-started/build-first-dashboard/">Grafana official site</a>.</li>
</ol>
Congratulations! Use dashboards to watch your RedDatabase.
