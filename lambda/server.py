#!/usr/bin/python
import traceback, json, socket, struct, os, sys, socket, threading
import rethinkdb
import flask
import tornado.ioloop
import tornado.web
import tornado.httpserver
import tornado.netutil
import measurestats

sys.path.append('/handler')
import lambda_func # assume submitted .py file is /handler/lambda_func

flask_app = flask.Flask(__name__)

PROCESSES_DEFAULT = 10
PORT = 8080
initialized = False
config = None
db_conn = None

# run once per process
def init():
    global initialized, config, db_conn
    if initialized:
        return
    sys.stdout = sys.stderr # flask supresses stdout :(
    config = json.loads(os.environ['ol.config'])
    if config.get('db', None) == 'rethinkdb':
        host = config.get('rethinkdb.host', 'localhost')
        port = config.get('rethinkdb.port', 28015)
        print 'Connect to %s:%d' % (host, port)
        db_conn = rethinkdb.connect(host, port)
	try:
		rethink.db_create('stats').run(db_conn)
	except:
		pass
	try: 
		rethink.db('stats').table_create('lambdaexec',primary_key='ID').run(db_conn)
	except:
		pass
	try:
		rethink.db('stats').table_create('lambdaIO',primary_key='ID').run(db_conn)
	except:
		pass
    initialized = True

# catch everything
@flask_app.route('/', defaults={'path': ''}, methods=['POST'])
@flask_app.route('/<path:path>', methods=['POST'])
def flask_post(path):
    try:
        init()
        flask.request.get_data()
        data = flask.request.data
        try :
            event = json.loads(data)
        except:
            return ('bad POST data: "%s"'%str(data), 400)
        ID = int(1000*time.time())
		return json.dumps(measurestats.measure_cpu(db_conn, event, ID))
    except Exception:
        return (traceback.format_exc(), 500) # internal error

class SockFileHandler(tornado.web.RequestHandler):
    def post(self):
        try:
            init()
            data = self.request.body
            try :
                event = json.loads(data)
            except:
                self.set_status(400)
                self.write('bad POST data: "%s"'%str(data))
                return
            self.write(json.dumps(lambda_func.handler(db_conn, event)))
        except Exception:
            self.set_status(500) # internal error
            self.write(traceback.format_exc())

tornado_app = tornado.web.Application([
    (r".*", SockFileHandler),
])

def main():
    config = json.loads(os.environ['ol.config'])

    if 'sock_file' in config:
        # listen on sock file with Tornado
        server = tornado.httpserver.HTTPServer(tornado_app)
        socket = tornado.netutil.bind_unix_socket('/host/' + config['sock_file'])
        server.add_socket(socket)
        tornado.ioloop.IOLoop.instance().start()
    else:
        # listen on port with Flask
        procs = config.get('processes', PROCESSES_DEFAULT)
        flask_app.run(processes=procs, host='0.0.0.0', port=PORT)

if __name__ == '__main__':
    main()
