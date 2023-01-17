import os.path
import psutil
from tools import *


def scrape_db_size(path_to_database, db_name) -> str:
    db_size_in_bytes = 0
    path_to_db = path_to_database.split(':')[1]
    if os.path.exists(path_to_db):
        db_size_in_bytes = os.path.getsize(path_to_db)
    return "db_size{database=\"%s\"} %i\n" % (db_name, db_size_in_bytes)


def scrape_mon_database(cursor, db_name) -> str:
    cursor.execute("SELECT MON$STAT_ID, MON$OLDEST_SNAPSHOT, MON$NEXT_TRANSACTION, MON$PAGE_BUFFERS, MON$SQL_DIALECT, MON$SHUTDOWN_MODE, MON$SWEEP_INTERVAL, MON$READ_ONLY, MON$FORCED_WRITES, MON$RESERVE_SPACE, MON$PAGES, MON$BACKUP_STATE, MON$CRYPT_PAGE, MON$OLDEST_TRANSACTION, MON$OLDEST_ACTIVE FROM MON$DATABASE;")
    response = ""
    databases = cursor.fetchall()
    for database in databases:
        response += "mon_database{database=\"%s\", stat_id=\"%i\", type=\"oldest_snapshot\"} %i\n" % (db_name, database[0], database[1])
        response += "mon_database{database=\"%s\", stat_id=\"%i\", type=\"next_transaction\"} %i\n" % (db_name, database[0], database[2])
        response += "mon_database{database=\"%s\", stat_id=\"%i\", type=\"page_buffers\"} %i\n" % (db_name, database[0], database[3])
        response += "mon_database{database=\"%s\", stat_id=\"%i\", type=\"SQL_dialect\"} %i\n" % (db_name, database[0], database[4])
        response += "mon_database{database=\"%s\", stat_id=\"%i\", type=\"shutdown_mode\"} %i\n" % (db_name, database[0], database[5])
        response += "mon_database{database=\"%s\", stat_id=\"%i\", type=\"sweep_interval\"} %i\n" % (db_name, database[0], database[6])
        response += "mon_database{database=\"%s\", stat_id=\"%i\", type=\"read_only\"} %i\n" % (db_name, database[0], database[7])
        response += "mon_database{database=\"%s\", stat_id=\"%i\", type=\"forced_writes\"} %i\n" % (db_name, database[0], database[8])
        response += "mon_database{database=\"%s\", stat_id=\"%i\", type=\"reserve_space\"} %i\n" % (db_name, database[0], database[9])
        response += "mon_database{database=\"%s\", stat_id=\"%i\", type=\"pages\"} %i\n" % (db_name, database[0], database[10])
        response += "mon_database{database=\"%s\", stat_id=\"%i\", type=\"crypt_page\"} %i\n" % (db_name, database[0], database[11])
        response += "mon_database{database=\"%s\", stat_id=\"%i\", type=\"oldest_transaction\"} %i\n" % (db_name, database[0], database[12])
        response += "mon_database{database=\"%s\", stat_id=\"%i\", type=\"oldest_active\"} %i\n" % (db_name, database[0], database[13])
    response += "diff_oldt_nt{database=\"%s\"} %i\n" % (db_name, databases[0][2] - databases[0][12])
    return response


def scrape_mon_attachments(cursor, db_name) -> str:
    cursor.execute("SELECT MON$STAT_ID, MON$ATTACHMENT_ID, MON$SERVER_PID, MON$STATE, MON$REMOTE_PID, MON$CHARACTER_SET_ID, MON$GARBAGE_COLLECTION, MON$SYSTEM_FLAG, MON$REPL_WAITFLUSH_COUNT, MON$REPL_WAITFLUSH_TIME FROM MON$ATTACHMENTS;")
    response = ""
    active_users = 0
    attachments = cursor.fetchall()
    for attachment in attachments:
        response += "mon_attachment{database=\"%s\", stat_id=\"%i\", attachment_id=\"%i\", type=\"server_pid\"} %i\n" % (db_name, attachment[0], attachment[1], attachment[2])
        response += "mon_attachment{database=\"%s\", stat_id=\"%i\", attachment_id=\"%i\", type=\"state\"} %i\n" % (db_name, attachment[0], attachment[1], attachment[3])
        response += "mon_attachment{database=\"%s\", stat_id=\"%i\", attachment_id=\"%i\", type=\"remote_pid\"} %i\n" % (db_name, attachment[0], attachment[1], 0 if attachment[4] is None else attachment[4])
        response += "mon_attachment{database=\"%s\", stat_id=\"%i\", attachment_id=\"%i\", type=\"character_set_id\"} %i\n" % (db_name, attachment[0], attachment[1], attachment[5])
        response += "mon_attachment{database=\"%s\", stat_id=\"%i\", attachment_id=\"%i\", type=\"garbage_collection\"} %i\n" % (db_name, attachment[0], attachment[1], attachment[6])
        response += "mon_attachment{database=\"%s\", stat_id=\"%i\", attachment_id=\"%i\", type=\"system_flag\"} %i\n" % (db_name, attachment[0], attachment[1], attachment[7])
        response += "mon_attachment{database=\"%s\", stat_id=\"%i\", attachment_id=\"%i\", type=\"repl_waitflush_count\"} %i\n" % (db_name, attachment[0], attachment[1], attachment[8])
        response += "mon_attachment{database=\"%s\", stat_id=\"%i\", attachment_id=\"%i\", type=\"repl_waitflush_time\"} %i\n" % (db_name, attachment[0], attachment[1], attachment[9])
        if attachment[3] == 1:
            active_users += 1
    response += "active_users{database=\"%s\"} %i\n" % (db_name, active_users)
    response += "amount_of_attachments{database=\"%s\"} %i\n" % (db_name, len(attachments))
    return response


def scrape_mon_transactions(cursor, db_name) -> str:
    cursor.execute("SELECT MON$STAT_ID, MON$TRANSACTION_ID, MON$ATTACHMENT_ID, MON$STATE, MON$TOP_TRANSACTION, MON$OLDEST_TRANSACTION, MON$OLDEST_ACTIVE, MON$ISOLATION_MODE, MON$LOCK_TIMEOUT, MON$READ_ONLY, MON$AUTO_COMMIT, MON$AUTO_UNDO FROM MON$TRANSACTIONS")
    response = ""
    transactions = cursor.fetchall()
    for transaction in transactions:
        response += "mon_transaction{database=\"%s\", stat_id=\"%i\", transaction_id=\"%i\", type=\"attachment_id\"} %i\n" % (db_name, transaction[0], transaction[1], transaction[2])
        response += "mon_transaction{database=\"%s\", stat_id=\"%i\", transaction_id=\"%i\", type=\"state\"} %i\n" % (db_name, transaction[0], transaction[1], transaction[3])
        response += "mon_transaction{database=\"%s\", stat_id=\"%i\", transaction_id=\"%i\", type=\"top_transaction\"} %i\n" % (db_name, transaction[0], transaction[1], transaction[4])
        response += "mon_transaction{database=\"%s\", stat_id=\"%i\", transaction_id=\"%i\", type=\"oldest_transaction\"} %i\n" % (db_name, transaction[0], transaction[1], transaction[5])
        response += "mon_transaction{database=\"%s\", stat_id=\"%i\", transaction_id=\"%i\", type=\"oldest_active\"} %i\n" % (db_name, transaction[0], transaction[1], transaction[6])
        response += "mon_transaction{database=\"%s\", stat_id=\"%i\", transaction_id=\"%i\", type=\"isolation_mode\"} %i\n" % (db_name, transaction[0], transaction[1], transaction[7])
        response += "mon_transaction{database=\"%s\", stat_id=\"%i\", transaction_id=\"%i\", type=\"lock_timeout\"} %i\n" % (db_name, transaction[0], transaction[1], transaction[8])
        response += "mon_transaction{database=\"%s\", stat_id=\"%i\", transaction_id=\"%i\", type=\"read_only\"} %i\n" % (db_name, transaction[0], transaction[1], transaction[9])
        response += "mon_transaction{database=\"%s\", stat_id=\"%i\", transaction_id=\"%i\", type=\"auto_commit\"} %i\n" % (db_name, transaction[0], transaction[1], transaction[10])
        response += "mon_transaction{database=\"%s\", stat_id=\"%i\", transaction_id=\"%i\", type=\"auto_undo\"} %i\n" % (db_name, transaction[0], transaction[1], transaction[11])
    return response


def scrape_mon_statements(cursor, db_name) -> str:
    cursor.execute("SELECT MON$STAT_ID, MON$STATEMENT_ID, MON$ATTACHMENT_ID, MON$TRANSACTION_ID, MON$STATE FROM MON$STATEMENTS")
    response = ""
    statements = cursor.fetchall()
    for statement in statements:
        response += "mon_statement{database=\"%s\", stat_id=\"%i\", statement_id=\"%i\", type=\"attachment_id\"} %i\n" % (db_name, statement[0], statement[1], statement[2])
        response += "mon_statement{database=\"%s\", stat_id=\"%i\", statement_id=\"%i\", type=\"transaction_id\"} %i\n" % (db_name, statement[0], statement[1], -1 if statement[3] is None else statement[3])
        response += "mon_statement{database=\"%s\", stat_id=\"%i\", statement_id=\"%i\", type=\"state\"} %i\n" % (db_name, statement[0], statement[1], statement[4])
    return response


def scrape_mon_io_stats(cursor, db_name) -> str:
    cursor.execute("SELECT MON$STAT_ID, MON$STAT_GROUP, MON$PAGE_READS, MON$PAGE_WRITES, MON$PAGE_FETCHES, MON$PAGE_MARKS FROM MON$IO_STATS")
    response = ""
    io = cursor.fetchall()
    for record in io:
        group = decode_group(record[1])
        response += "mon_io_stats{database=\"%s\", stat_id=\"%i\", stat_group=\"%s\", type=\"page_reads\"} %i\n" % (db_name, record[0], group, record[2])
        response += "mon_io_stats{database=\"%s\", stat_id=\"%i\", stat_group=\"%s\", type=\"page_writes\"} %i\n" % (db_name, record[0], group, record[3])
        response += "mon_io_stats{database=\"%s\", stat_id=\"%i\", stat_group=\"%s\", type=\"page_fetches\"} %i\n" % (db_name, record[0], group, record[4])
        response += "mon_io_stats{database=\"%s\", stat_id=\"%i\", stat_group=\"%s\", type=\"page_marks\"} %i\n" % (db_name, record[0], group, record[5])
    return response


def scrape_mon_memory_usage(cursor, db_name) -> str:
    cursor.execute("SELECT MON$STAT_ID, MON$STAT_GROUP, MON$MEMORY_USED, MON$MEMORY_ALLOCATED, MON$MAX_MEMORY_USED, MON$MAX_MEMORY_ALLOCATED FROM MON$MEMORY_USAGE")
    response = ""
    data = cursor.fetchall()
    for record in data:
        group = decode_group(record[1])
        response += "mon_memory_usage{database=\"%s\", stat_id=\"%i\", stat_group=\"%s\", type=\"memory_used\"} %i\n" % (db_name, record[0], group, record[2])
        response += "mon_memory_usage{database=\"%s\", stat_id=\"%i\", stat_group=\"%s\", type=\"memory_allocated\"} %i\n" % (db_name, record[0], group, record[3])
        response += "mon_memory_usage{database=\"%s\", stat_id=\"%i\", stat_group=\"%s\", type=\"max_memory_used\"} %i\n" % (db_name, record[0], group, record[4])
        response += "mon_memory_usage{database=\"%s\", stat_id=\"%i\", stat_group=\"%s\", type=\"max_memory_allocated\"} %i\n" % (db_name, record[0], group, record[5])
    return response


def scrape_mon_call_stack(cursor, db_name) -> str:
    cursor.execute("SELECT MON$STAT_ID, MON$CALL_ID, MON$OBJECT_TYPE, MON$STATEMENT_ID, MON$CALLER_ID, MON$SOURCE_LINE, MON$SOURCE_COLUMN FROM MON$CALL_STACK")
    response = ""
    data = cursor.fetchall()
    for record in data:
        object_type = decode_call_object_type(record[2])
        response += "mon_call_stack{database=\"%s\", stat_id=\"%i\", call_id=\"%i\", object_type=\"%s\", type=\"statement_id\"} %i\n" % (db_name, record[0], record[1], object_type, record[3])
        response += "mon_call_stack{database=\"%s\", stat_id=\"%i\", call_id=\"%i\", object_type=\"%s\", type=\"caller_id\"} %i\n" % (db_name, record[0], record[1], object_type, record[4])
        response += "mon_call_stack{database=\"%s\", stat_id=\"%i\", call_id=\"%i\", object_type=\"%s\", type=\"source_line\"} %i\n" % (db_name, record[0], record[1], object_type, record[5])
        response += "mon_call_stack{database=\"%s\", stat_id=\"%i\", call_id=\"%i\", object_type=\"%s\", type=\"source_column\"} %i\n" % (db_name, record[0], record[1], object_type, record[6])
    return response


def scrape_mon_record_stats(cursor, db_name) -> str:
    cursor.execute("SELECT MON$STAT_ID, MON$STAT_GROUP, MON$RECORD_SEQ_READS, MON$RECORD_IDX_READS, MON$RECORD_INSERTS, MON$RECORD_UPDATES, MON$RECORD_DELETES, MON$RECORD_BACKOUTS, MON$RECORD_PURGES, MON$RECORD_EXPUNGES, MON$RECORD_LOCKS, MON$RECORD_WAITS, MON$RECORD_CONFLICTS, MON$BACKVERSION_READS, MON$FRAGMENT_READS, MON$RECORD_RPT_READS FROM MON$RECORD_STATS")
    response = ""
    record_stats = cursor.fetchall()
    for stat in record_stats:
        group = decode_group(stat[1])
        response += "mon_record_stats{database=\"%s\", stat_id=\"%i\", stat_group=\"%s\", type=\"record_seq_reads\"} %i\n" % (db_name, stat[0], group, stat[2])
        response += "mon_record_stats{database=\"%s\", stat_id=\"%i\", stat_group=\"%s\", type=\"record_idx_reads\"} %i\n" % (db_name, stat[0], group, stat[3])
        response += "mon_record_stats{database=\"%s\", stat_id=\"%i\", stat_group=\"%s\", type=\"record_inserts\"} %i\n" % (db_name, stat[0], group, stat[4])
        response += "mon_record_stats{database=\"%s\", stat_id=\"%i\", stat_group=\"%s\", type=\"record_updates\"} %i\n" % (db_name, stat[0], group, stat[5])
        response += "mon_record_stats{database=\"%s\", stat_id=\"%i\", stat_group=\"%s\", type=\"record_deletes\"} %i\n" % (db_name, stat[0], group, stat[6])
        response += "mon_record_stats{database=\"%s\", stat_id=\"%i\", stat_group=\"%s\", type=\"record_backouts\"} %i\n" % (db_name, stat[0], group, stat[7])
        response += "mon_record_stats{database=\"%s\", stat_id=\"%i\", stat_group=\"%s\", type=\"record_purges\"} %i\n" % (db_name, stat[0], group, stat[8])
        response += "mon_record_stats{database=\"%s\", stat_id=\"%i\", stat_group=\"%s\", type=\"record_expunges\"} %i\n" % (db_name, stat[0], group, stat[9])
        response += "mon_record_stats{database=\"%s\", stat_id=\"%i\", stat_group=\"%s\", type=\"record_locks\"} %i\n" % (db_name, stat[0], group, stat[10])
        response += "mon_record_stats{database=\"%s\", stat_id=\"%i\", stat_group=\"%s\", type=\"record_waits\"} %i\n" % (db_name, stat[0], group, stat[11])
        response += "mon_record_stats{database=\"%s\", stat_id=\"%i\", stat_group=\"%s\", type=\"record_conflicts\"} %i\n" % (db_name, stat[0], group, stat[12])
        response += "mon_record_stats{database=\"%s\", stat_id=\"%i\", stat_group=\"%s\", type=\"backversion_reads\"} %i\n" % (db_name, stat[0], group, stat[13])
        response += "mon_record_stats{database=\"%s\", stat_id=\"%i\", stat_group=\"%s\", type=\"fragment_reads\"} %i\n" % (db_name, stat[0], group, stat[14])
        response += "mon_record_stats{database=\"%s\", stat_id=\"%i\", stat_group=\"%s\", type=\"record_rpt_reads\"} %i\n" % (db_name, stat[0], group, stat[15])
    return response


def scrape_mon_table_stats(cursor, db_name) -> str:
    cursor.execute("SELECT MON$STAT_ID, MON$STAT_GROUP, MON$TABLE_NAME, MON$RECORD_STAT_ID FROM MON$TABLE_STATS;")
    response = ""
    table_stats = cursor.fetchall()
    for stat in table_stats:
        response += "mon_table_stats{database=\"%s\", stat_id=\"%i\", stat_group=\"%s\", table=\"%s\"} %i\n" % (db_name, stat[0], decode_group(stat[1]), stat[2], stat[3])
    return response


def scrape_system_metrics() -> str:
    response = ""
    memory = psutil.virtual_memory()
    cpu_freq = psutil.cpu_freq()
    response += "system_memory{type=\"used\"} %i\n" % (memory.total - memory.available)
    response += "system_memory{type=\"available\"} %i\n" % memory.available
    response += "system_memory{type=\"total\"} %i\n" % memory.total
    response += "system_cpu{type=\"percent\"} %f\n" % psutil.cpu_percent()
    response += "system_cpu{type=\"frequency\"} %i\n" % cpu_freq.current

    return response

