import re
import os.path
import psutil
import subprocess
import datetime
from tools import *


def scrape_db_size(path_to_database, cursor, db_name) -> str:
    db_size_in_bytes = 0
    path_to_db = path_to_database.split(':')[1]
    if os.path.exists(path_to_db):
        db_size_in_bytes = os.path.getsize(path_to_db)
    else:
        cursor.execute("SELECT MON$DATABASE_NAME FROM MON$DATABASE;")
        path_to_db = cursor.fetchone()[0]
        if os.path.exists(path_to_db):
            db_size_in_bytes = os.path.getsize(path_to_db)
    return make_prometheus_response("db_size", {"database": db_name}, db_size_in_bytes)


def scrape_mon_database(cursor, db_name) -> str:
    cursor.execute("SELECT MON$STAT_ID, MON$OLDEST_SNAPSHOT, MON$NEXT_TRANSACTION, MON$PAGE_BUFFERS, MON$SQL_DIALECT, MON$SHUTDOWN_MODE, MON$SWEEP_INTERVAL, MON$READ_ONLY, MON$FORCED_WRITES, MON$RESERVE_SPACE, MON$PAGES, MON$BACKUP_STATE, MON$CRYPT_PAGE, MON$OLDEST_TRANSACTION, MON$OLDEST_ACTIVE FROM MON$DATABASE;")
    response = ""
    metric_name = "mon_database"
    labels = {
        "database": db_name,
        "stat_id": None,
        "type": None
    }
    databases = cursor.fetchall()
    for database in databases:
        labels["stat_id"] = database[0]
        labels["type"] = "oldest_snapshot"
        response += make_prometheus_response(metric_name, labels, database[1])
        labels["type"] = "next_transaction"
        response += make_prometheus_response(metric_name, labels, database[2])
        labels["type"] = "page_buffers"
        response += make_prometheus_response(metric_name, labels, database[3])
        labels["type"] = "SQL_dialect"
        response += make_prometheus_response(metric_name, labels, database[4])
        labels["type"] = "shutdown_mode"
        response += make_prometheus_response(metric_name, labels, database[5])
        labels["type"] = "sweep_interval"
        response += make_prometheus_response(metric_name, labels, database[6])
        labels["type"] = "read_only"
        response += make_prometheus_response(metric_name, labels, database[7])
        labels["type"] = "forced_writes"
        response += make_prometheus_response(metric_name, labels, database[8])
        labels["type"] = "reserve_space"
        response += make_prometheus_response(metric_name, labels, database[9])
        labels["type"] = "pages"
        response += make_prometheus_response(metric_name, labels, database[10])
        labels["type"] = "crypt_page"
        response += make_prometheus_response(metric_name, labels, database[11])
        labels["type"] = "oldest_transaction"
        response += make_prometheus_response(metric_name, labels, database[12])
        labels["type"] = "oldest_active"
        response += make_prometheus_response(metric_name, labels, database[13])
    return response


def scrape_mon_attachments(cursor, db_name) -> str:
    cursor.execute("SELECT MON$STAT_ID, MON$ATTACHMENT_ID, MON$SERVER_PID, MON$STATE, MON$REMOTE_PID, MON$CHARACTER_SET_ID, MON$GARBAGE_COLLECTION, MON$SYSTEM_FLAG, MON$REPL_WAITFLUSH_COUNT, MON$REPL_WAITFLUSH_TIME, MON$TIMESTAMP, MON$REMOTE_ADDRESS, MON$REMOTE_PROCESS FROM MON$ATTACHMENTS;")
    response = ""
    active_users = 0
    metric_name = "mon_attachment"
    labels = {
        "database": db_name,
        "stat_id": None,
        "attachment_id": None,
        "remote_address": None,
        "remote_process": None,
        "type": None
    }
    attachments = cursor.fetchall()
    for attachment in attachments:
        seconds_gone = 0
        if not attachment[10] is None:
            time_zone = attachment[10].tzinfo
            current_time = datetime.datetime.now(time_zone)
            seconds_gone = (current_time - attachment[10]).total_seconds()
        labels["stat_id"] = attachment[0]
        labels["attachment_id"] = attachment[1]
        labels["remote_address"] = attachment[11]
        labels["remote_process"] = attachment[12]
        labels["type"] = "server_pid"
        response += make_prometheus_response(metric_name, labels, attachment[2])
        labels["type"] = "state"
        response += make_prometheus_response(metric_name, labels, attachment[3])
        labels["type"] = "remote_pid"
        response += make_prometheus_response(metric_name, labels, attachment[4])
        labels["type"] = "character_set_id"
        response += make_prometheus_response(metric_name, labels, attachment[5])
        labels["type"] = "garbage_collection"
        response += make_prometheus_response(metric_name, labels, attachment[6])
        labels["type"] = "system_flag"
        response += make_prometheus_response(metric_name, labels, attachment[7])
        labels["type"] = "repl_waitflush_count"
        response += make_prometheus_response(metric_name, labels, attachment[8])
        labels["type"] = "repl_waitflush_time"
        response += make_prometheus_response(metric_name, labels, attachment[9])
        labels["type"] = "deltatime"
        response += make_prometheus_response(metric_name, labels, seconds_gone)
        if attachment[3] == 1:
            active_users += 1
    response += "active_users{database=\"%s\"} %i\n" % (db_name, active_users)
    response += "amount_of_attachments{database=\"%s\"} %i\n" % (db_name, len(attachments))
    return response


def scrape_mon_transactions(cursor, db_name) -> str:
    cursor.execute("SELECT MON$STAT_ID, MON$TRANSACTION_ID, MON$ATTACHMENT_ID, MON$STATE, MON$TOP_TRANSACTION, MON$OLDEST_TRANSACTION, MON$OLDEST_ACTIVE, MON$ISOLATION_MODE, MON$LOCK_TIMEOUT, MON$READ_ONLY, MON$AUTO_COMMIT, MON$AUTO_UNDO, MON$TIMESTAMP FROM MON$TRANSACTIONS")
    response = ""
    metric_name = "mon_transaction"
    labels = {
        "database": db_name,
        "stat_id": None,
        "transaction_id": None,
        "attachment_id": None,
        "type": None
    }
    transactions = cursor.fetchall()
    for transaction in transactions:
        seconds_gone = 0
        if not transaction[12] is None:
            time_zone = transaction[12].tzinfo
            current_time = datetime.datetime.now(time_zone)
            seconds_gone = (current_time - transaction[12]).total_seconds()
        labels["stat_id"] = transaction[0]
        labels["transaction_id"] = transaction[1]
        labels["attachment_id"] = transaction[2]
        labels["type"] = "state"
        response += make_prometheus_response(metric_name, labels, transaction[3])
        labels["type"] = "top_transaction"
        response += make_prometheus_response(metric_name, labels, transaction[4])
        labels["type"] = "oldest_transaction"
        response += make_prometheus_response(metric_name, labels, transaction[5])
        labels["type"] = "oldest_active"
        response += make_prometheus_response(metric_name, labels, transaction[6])
        labels["type"] = "isolation_mode"
        response += make_prometheus_response(metric_name, labels, transaction[7])
        labels["type"] = "lock_timeout"
        response += make_prometheus_response(metric_name, labels, transaction[8])
        labels["type"] = "read_only"
        response += make_prometheus_response(metric_name, labels, transaction[9])
        labels["type"] = "auto_commit"
        response += make_prometheus_response(metric_name, labels, transaction[10])
        labels["type"] = "auto_undo"
        response += make_prometheus_response(metric_name, labels, transaction[11])
        labels["type"] = "deltatime"
        response += make_prometheus_response(metric_name, labels, seconds_gone)
    return response


def scrape_transactions_params(path_to_gstat, path_to_database, db_name) -> str:
    response = ""
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
    metric_name = "transactions_params"
    labels = {"database": db_name, "type": "NT"}
    response += make_prometheus_response(metric_name, labels, int(p["Next transaction"]))
    labels["type"] = "OIT"
    response += make_prometheus_response(metric_name, labels, int(p["Oldest transaction"]))
    labels["type"] = "OAT"
    response += make_prometheus_response(metric_name, labels, int(p["Oldest active"]))
    labels["type"] = "OST"
    response += make_prometheus_response(metric_name, labels, int(p["Oldest snapshot"]))
    return response


def scrape_mon_statements(cursor, db_name) -> str:
    cursor.execute("SELECT MON$STAT_ID, MON$STATEMENT_ID, MON$ATTACHMENT_ID, MON$TRANSACTION_ID, MON$STATE, MON$TIMESTAMP FROM MON$STATEMENTS")
    response = ""
    metric_name = "mon_statement"
    labels = {
        "database": db_name,
        "stat_id": None,
        "statement_id": None,
        "attachment_id": None,
        "transaction_id": None,
        "type": None
    }
    statements = cursor.fetchall()
    for statement in statements:
        seconds_gone = 0
        if not statement[5] is None:
            time_zone = statement[5].tzinfo
            current_time = datetime.datetime.now(time_zone)
            seconds_gone = (current_time - statement[5]).total_seconds()
        labels["stat_id"] = statement[0]
        labels["statement_id"] = statement[1]
        labels["attachment_id"] = statement[2]
        labels["transaction_id"] = statement[3]
        labels["type"] = "state"
        response += make_prometheus_response(metric_name, labels, statement[4])
        labels["type"] = "deltatime"
        response += make_prometheus_response(metric_name, labels, seconds_gone)
    return response


def scrape_mon_io_stats(cursor, db_name) -> str:
    cursor.execute("SELECT MON$STAT_ID, MON$STAT_GROUP, MON$PAGE_READS, MON$PAGE_WRITES, MON$PAGE_FETCHES, MON$PAGE_MARKS FROM MON$IO_STATS")
    response = ""
    metric_name = "mon_io_stats"
    labels = {
        "database": db_name,
        "stat_id": None,
        "stat_group": None,
        "type": None
    }
    io = cursor.fetchall()
    for record in io:
        labels["stat_id"] = record[0]
        labels["stat_group"] = decode_group(record[1])
        labels["type"] = "page_reads"
        response += make_prometheus_response(metric_name, labels, record[2])
        labels["type"] = "page_writes"
        response += make_prometheus_response(metric_name, labels, record[3])
        labels["type"] = "page_fetches"
        response += make_prometheus_response(metric_name, labels, record[4])
        labels["type"] = "page_marks"
        response += make_prometheus_response(metric_name, labels, record[5])
    return response


def scrape_mon_memory_usage(cursor, db_name) -> str:
    cursor.execute("SELECT MON$STAT_ID, MON$STAT_GROUP, MON$MEMORY_USED, MON$MEMORY_ALLOCATED, MON$MAX_MEMORY_USED, MON$MAX_MEMORY_ALLOCATED FROM MON$MEMORY_USAGE")
    response = ""
    metric_name = "mon_memory_usage"
    labels = {
        "database": db_name,
        "stat_id": None,
        "stat_group": None,
        "type": None
    }
    data = cursor.fetchall()
    for record in data:
        labels["stat_id"] = record[0]
        labels["stat_group"] = decode_group(record[1])
        labels["type"] = "memory_used"
        response += make_prometheus_response(metric_name, labels, record[2])
        labels["type"] = "memory_allocated"
        response += make_prometheus_response(metric_name, labels, record[3])
        labels["type"] = "max_memory_used"
        response += make_prometheus_response(metric_name, labels, record[4])
        labels["type"] = "max_memory_allocated"
        response += make_prometheus_response(metric_name, labels, record[5])
    return response


def scrape_mon_call_stack(cursor, db_name) -> str:
    cursor.execute("SELECT MON$STAT_ID, MON$CALL_ID, MON$OBJECT_TYPE, MON$STATEMENT_ID, MON$CALLER_ID, MON$SOURCE_LINE, MON$SOURCE_COLUMN, MON$TIMESTAMP FROM MON$CALL_STACK")
    response = ""
    metric_name = "mon_call_stack"
    labels = {
        "database": db_name,
        "stat_id": None,
        "call_id": None,
        "object_type": None,
        "statement_id": None,
        "type": None
    }
    data = cursor.fetchall()
    for record in data:
        seconds_gone = 0
        if not record[7] is None:
            time_zone = record[7].tzinfo
            current_time = datetime.datetime.now(time_zone)
            seconds_gone = (current_time - record[7]).total_seconds()
        labels["stat_id"] = record[0]
        labels["call_id"] = record[1]
        labels["object_type"] = decode_call_object_type(record[2])
        labels["statement_id"] = record[3]
        labels["type"] = "caller_id"
        response += make_prometheus_response(metric_name, labels, record[4])
        labels["type"] = "source_line"
        response += make_prometheus_response(metric_name, labels, record[5])
        labels["type"] = "source_column"
        response += make_prometheus_response(metric_name, labels, record[5])
        labels["type"] = "deltatime"
        response += make_prometheus_response(metric_name, labels, seconds_gone)
    return response


def scrape_mon_record_stats(cursor, db_name) -> str:
    cursor.execute("SELECT MON$STAT_ID, MON$STAT_GROUP, MON$RECORD_SEQ_READS, MON$RECORD_IDX_READS, MON$RECORD_INSERTS, MON$RECORD_UPDATES, MON$RECORD_DELETES, MON$RECORD_BACKOUTS, MON$RECORD_PURGES, MON$RECORD_EXPUNGES, MON$RECORD_LOCKS, MON$RECORD_WAITS, MON$RECORD_CONFLICTS, MON$BACKVERSION_READS, MON$FRAGMENT_READS, MON$RECORD_RPT_READS FROM MON$RECORD_STATS")
    response = ""
    metric_name = "mon_record_stats"
    labels = {
        "database": db_name,
        "stat_id": None,
        "stat_group": None,
        "type": None
    }
    record_stats = cursor.fetchall()
    for stat in record_stats:
        labels["stat_id"] = stat[0]
        labels["stat_group"] = decode_group(stat[1])
        labels["type"] = "record_seq_reads"
        response += make_prometheus_response(metric_name, labels, stat[2])
        labels["type"] = "record_idx_reads"
        response += make_prometheus_response(metric_name, labels, stat[3])
        labels["type"] = "record_inserts"
        response += make_prometheus_response(metric_name, labels, stat[4])
        labels["type"] = "record_updates"
        response += make_prometheus_response(metric_name, labels, stat[5])
        labels["type"] = "record_deletes"
        response += make_prometheus_response(metric_name, labels, stat[6])
        labels["type"] = "record_backouts"
        response += make_prometheus_response(metric_name, labels, stat[7])
        labels["type"] = "record_purges"
        response += make_prometheus_response(metric_name, labels, stat[8])
        labels["type"] = "record_expunges"
        response += make_prometheus_response(metric_name, labels, stat[9])
        labels["type"] = "record_locks"
        response += make_prometheus_response(metric_name, labels, stat[10])
        labels["type"] = "record_waits"
        response += make_prometheus_response(metric_name, labels, stat[11])
        labels["type"] = "record_conflicts"
        response += make_prometheus_response(metric_name, labels, stat[12])
        labels["type"] = "backversion_reads"
        response += make_prometheus_response(metric_name, labels, stat[13])
        labels["type"] = "fragment_reads"
        response += make_prometheus_response(metric_name, labels, stat[14])
        labels["type"] = "record_rpt_reads"
        response += make_prometheus_response(metric_name, labels, stat[15])
    return response


def scrape_mon_table_stats(cursor, db_name) -> str:
    cursor.execute("SELECT MON$STAT_ID, MON$STAT_GROUP, MON$TABLE_NAME, MON$RECORD_STAT_ID FROM MON$TABLE_STATS;")
    response = ""
    metric_name = "mon_table_stats"
    labels = {
        "database": db_name,
        "stat_id": None,
        "stat_group": None,
        "table": None
    }
    table_stats = cursor.fetchall()
    for stat in table_stats:
        labels["stat_id"] = stat[3]
        labels["stat_group"] = decode_group(stat[1])
        labels["table"] = stat[2]
        response += make_prometheus_response(metric_name, labels, 1)
    return response


def scrape_system_metrics(CONFIGURE) -> str:
    response = ""
    memory = psutil.virtual_memory()
    cpu_freq = psutil.cpu_freq()
    metric_name = "system_memory"
    labels = {"type": "used"}
    response += make_prometheus_response(metric_name, labels, memory.total - memory.available)
    labels["type"] = "available"
    response += make_prometheus_response(metric_name, labels, memory.available)
    labels["type"] = "total"
    response += make_prometheus_response(metric_name, labels, memory.total)
    metric_name = "system_cpu"
    labels["type"] = "percent"
    response += make_prometheus_response(metric_name, labels, psutil.cpu_percent())
    labels["type"] = "frequency"
    response += make_prometheus_response(metric_name, labels, cpu_freq.current)

    if 'mountpoints' in CONFIGURE:
        metric_name = "system_disk"
        for mp in CONFIGURE['mountpoints']:
            usage = psutil.disk_usage(mp)
            labels["disks"] = mp
            labels["type"] = "total"
            response += make_prometheus_response(metric_name, labels, usage.total)
            labels["type"] = "used"
            response += make_prometheus_response(metric_name, labels, usage.used)
            labels["type"] = "free"
            response += make_prometheus_response(metric_name, labels, usage.free)
    return response


def scrape_trace(path_to_trace, db_name) -> str:
    with open(path_to_trace, 'r') as file:
        data = file.read()
    metric_name = "trace_statements"
    labels = {
        "database": db_name,
        "type": None
    }
    fails = 0
    OK = 0
    times = 0
    statements = re.findall(r'(FAILED|UNAUTHORIZED)*\s?(EXECUTE_STATEMENT_FINISH|PREPARE_STATEMENT).*?\s+(\d+) ms', data, re.S)
    for statement in statements:
        failed = statement[0] == "FAILED" or statement[0] == "UNAUTHORIZED"
        if statement[2] != '':
            times += int(statement[2])
        if failed:
            fails += 1
        elif statement[1] == 'EXECUTE_STATEMENT_FINISH':
            OK += 1

    response = ""
    labels["type"] = "OK"
    response += make_prometheus_response(metric_name, labels, OK)
    labels["type"] = "FAIL"
    response += make_prometheus_response(metric_name, labels, fails)
    labels["type"] = "time"
    response += make_prometheus_response(metric_name, labels, times)
    return response
