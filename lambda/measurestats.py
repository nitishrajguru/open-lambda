import rethinkdb as r
import lambda_func
import psutil
import time

def measure_cpu(conn, event, ID):
    snet_sent = psutil.net_io_counters().bytes_sent
    snet_receive = psutil.net_io_counters().bytes_recv
    s_w = psutil.disk_io_counters().write_bytes
    s_r = psutil.disk_io_counters().read_bytes
    mem_start = psutil.virtual_memory()
    start = psutil.cpu_percent(interval=None)
    time_start = time.time()

    ret = lambda_func.handler(conn, event, ID)

    time_end = time.time()
    end = psutil.cpu_percent(interval=None)
    mem_end = psutil.virtual_memory()
    e_w = psutil.disk_io_counters().write_bytes
    e_r = psutil.disk_io_counters().read_bytes
    enet_sent = psutil.net_io_counters().bytes_sent
    enet_receive = psutil.net_io_counters().bytes_recv
    n_s = enet_sent - snet_sent
    n_r = enet_receive - snet_receive
    r_b = e_r - s_r
    w_b = e_w - s_w
    mem_diff = mem_end.active - mem_start.active
    time_diff = time_end - time_start
    parentID = 0
    if 'parentID' in event:
        parentID = event['parentID']

    cnt = r.db('stats').table('lambdaexec').filter(r.row['ID'] == ID).count().run(conn)
    if cnt == 0:
        r.db('stats').table('lambdaexec').insert({'time_taken': time_diff, 'cpu_util': end, 'mem_active': mem_diff, 'read_bytes': r_b, 'write_bytes': w_b, 'sent_bytes': n_s, 'receive_bytes': n_r, 'ID': ID, 'parentID': parentID, 'lambdaID': event['lambdaID']}).run(conn)
    else:
        rec_time = r.db('stats').table('lambdaexec').get(ID).run(conn)['time_taken']
        act_time = time_diff - rec_time
        r.db('stats').table('lambdaexec').get(ID).update({"time_taken": act_time, 'cpu_util': end, 'mem_active': mem_diff, 'read_bytes': r_b, 'write_bytes': w_b, 'sent_bytes': n_s, 'receive_bytes': n_r, 'ID': ID, 'parentID': parentID, 'lambdaID': event['lambdaID']}).run(conn)
    return ret

def call_db(conn, query, table, ID):
    stats_time = time.time()
    tid = table.config().run(conn)['id']
    sid = conn.server()['id']
    s_w = r.db("rethinkdb").table("stats").get(["table_server", tid, sid]).run(conn)['storage_engine']['disk']['written_bytes_total']
    s_r = r.db("rethinkdb").table("stats").get(["table_server", tid, sid]).run(conn)['storage_engine']['disk']['read_bytes_total']
    snet_sent = psutil.net_io_counters().bytes_sent
    snet_receive = psutil.net_io_counters().bytes_recv
    time_start = time.time()
    cnt = r.db('stats').table('lambdaIO').filter(r.row['ID'] == ID).count().run(conn)
    if cnt == 0:
        r.db('stats').table('lambdaIO').insert({'start_write_bytes': s_w, 'start_read_bytes': s_r, 'ID': ID}).run(conn)
    else:
        r.db('stats').table('lambdaIO').get(ID).update({'start_write_bytes': r.row['start_write_bytes']+s_w, 'start_read_bytes': r.row['start_read_bytes']+s_r}).run(conn)
    stats_time = time.time() - stats_time

    ret = query.run(conn)

    stats_time2 = time.time()
    time_end = time.time()
    enet_sent = psutil.net_io_counters().bytes_sent
    enet_receive = psutil.net_io_counters().bytes_recv
    n_s = enet_sent - snet_sent
    n_r = enet_receive - snet_receive
    e_w = r.db("rethinkdb").table("stats").get(["table_server", tid, sid]).run(conn)['storage_engine']['disk']['written_bytes_total']
    e_r = r.db("rethinkdb").table("stats").get(["table_server", tid, sid]).run(conn)['storage_engine']['disk']['read_bytes_total']
    # r_b = e_r - s_r
    # w_b = e_w - s_w
    time_diff = time_end - time_start

    r.db('stats').table('lambdaIO').get(ID).update({'time_taken': (r.row['time_taken']+time_diff).default(time_diff),'end_write_bytes': (r.row['end_write_bytes']+e_w).default(e_w),'end_read_bytes': (r.row['end_read_bytes']+e_r).default(e_r), 'sent_bytes': (r.row['sent_bytes']+n_s).default(n_s), 'receive_bytes': (r.row['receive_bytes']+n_r).default(n_r), 'ID': ID}).run(conn)
    
    # r.db('stats').table('lambdaIO').insert({'time_taken': time_diff,'read_bytes': r_b, 'write_bytes': w_bb, 'sent_bytes': n_s, 'receive_bytes': n_r, 'ID': ID}).run(conn)

    # rep = r.db('stats').table('lambdaIO').get(ID).run(conn)

    stats_time = time.time() - stats_time2 + stats_time
    r.db('stats').table('lambdaexec').insert({'time_taken': stats_time, 'ID': ID}).run(conn)    

    return ret
    
def call_lambda(curlrequest, ID):
    pass
