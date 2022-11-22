# rdb_exporter
This is an prometheus exporter for DBMS "Red Database".
# exported metrics
<table>
  <tr>
    <th>Name</th>
    <th>Description</th>
  </tr>
  <tr><td>reddatabase_db_size</td><td>The amount of database bytes which are taken to store data.</td></tr>
  <tr><td>RedDatabase_diff_oldt_nt</td><td>The difference between Oldest transaction number and Next transaction number.</td></tr>
  <tr><td>RedDatabase_active_users</td><td>The amount of active users in a database. (Note: you need to have an administrator rights to extract this metric)</td></tr>
</table>
