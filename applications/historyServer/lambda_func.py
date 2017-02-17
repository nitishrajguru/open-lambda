import traceback
import rethinkdb as r

DB = 'stats'                  # DB
LAMBDA_TABLE = 'lambdaexec'   # LAMBDA EXEC TABLE
LAMBDA_IO_TABLE = 'lambdaIO'
ID   = 'ID'                   # COLUMN
TIME = 'time_taken'           # Completion Time
PID  = 'parentID'
LAMBDAID = 'lambdaID'

def updates(conn, event, jobId):
    recv_id = int(event.get('id', 0))
    rows = list(r.db(DB).table(LAMBDA_TABLE).filter(r.row[ID] > recv_id).run(conn))
    #rows = list(r.db(DB).table(LAMBDA_TABLE).run(conn))
    rows.sort(key=lambda row: row[ID])
    return rows

def getLambdaInternals(conn, event, jobId, recv_id):
    rows = list(r.db(DB).table(LAMBDA_TABLE).filter(r.row[PID] == recv_id).run(conn))
    return rows

def getDBInternals(conn, event, jobId, recv_id):
    rows = list(r.db(DB).table(LAMBDA_IO_TABLE).filter(r.row[ID] == recv_id).run(conn))
    rows.sort(key=lambda row: row[ID])
    return rows

def details(conn, event, jobId):
    recv_id = int(event.get('id', 0))
    rows = list(r.db(DB).table(LAMBDA_TABLE).filter(r.row[ID] == recv_id).run(conn))
    results = {'details' : rows};
    results['lambda'] = getLambdaInternals(conn, event, jobId, recv_id)
    results['DB'] = getDBInternals(conn, event, jobId, recv_id)
    return results

def history(conn, event, jobId):
    lambdaId = event.get('selLambda')
    rows = list(r.db(DB).table(LAMBDA_TABLE).filter(lambda row: row[LAMBDAID].match(lambdaId)).run(conn))
    rows.sort(key=lambda row: row[ID])
    results = {'details' : rows};
    results['DB'] = list(r.db(DB).table(LAMBDA_IO_TABLE).filter(lambda row: row[LAMBDAID].match(lambdaId)).run(conn))
    return results

def handler(conn, event, jobId):
    fn = {'updates': updates, 'details' : details, 'history': history}.get(event['op'], None)
    if fn != None:
        try:
            result = fn(conn, event, jobId)
            return {'result': result}
        except Exception:
            return {'error': traceback.format_exc()}
    else:
        return {'error': 'bad op'}
