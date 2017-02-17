#!/usr/bin/env python
import os, sys, argparse
import rethinkdb as r
from lambda_func import *
from common import *

def main():
    print 'Initializing %s DB' % DB

    parser = argparse.ArgumentParser()
    parser.add_argument('--cluster', '-c', default='cluster')
    args = parser.parse_args()

    root_dir = os.path.join(SCRIPT_DIR, '..', '..')
    cluster_dir = os.path.join(root_dir, 'util', args.cluster)
    worker0 = rdjs(os.path.join(cluster_dir, 'worker-0.json'))
    conn = r.connect(worker0['ip'], 28015)

    # try to drop table (may or may not exist)
    rv = ''
    try:
        r.db_drop(DB).run(conn)
        print 'dropped old DB'
    except:
        print "couldn't drop old DB"
        pass
    print r.db_create(DB).run(conn);
    print r.db(DB).table_create(LAMBDA_TABLE).run(conn);
    print r.db(DB).table(LAMBDA_TABLE).index_create(ID).run(conn)
    r.db(DB).table(LAMBDA_TABLE).insert({ID:  "1", TIME : "1234"}).run(conn)
    r.db(DB).table(LAMBDA_TABLE).insert({ID:  "2", TIME : "2345"}).run(conn)
    r.db(DB).table(LAMBDA_TABLE).insert({ID:  "3", TIME : "3456"}).run(conn)

if __name__ == '__main__':
    main()
