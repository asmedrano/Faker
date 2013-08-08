#!/usr/bin/python

import json
import urlparse
import cgi
import sys
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer


MIME_TYPES = {
    'html': 'text/html',
    'js' : 'application/javascript',
    'css' : 'text/css',
    'json' : 'application/json',
    'csv' : 'text/csv'
}

CONF = {}

class WebHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.do_request(self.path)

    def do_POST(self):
        self.do_request(self.path)

    def do_request(self, path):
        parsed_path = urlparse.urlparse(self.path)
        try:
            resp = CONF[parsed_path.path]
            self.respond(response=resp['response'],
                         mimetype=resp['mimetype'],
                         data=resp['data'])
        except KeyError:
            self.respond(404)

    def respond(self, response=200, mimetype='html', data=''):
        self.send_response(response)
        self.send_header('Content-type', MIME_TYPES[mimetype])
        self.end_headers()
        if 'file:' in data:
            print "Loading file %s" % data
            # check to see if the user wants us to load a file
            try:
                f_path = data.split(":")[1]
                f = open(f_path,"rb")
                data = f.read()
                f.close()
            except IOError:
                print "Error Reading file"
                self.respond(response=500)
        if mimetype == "json":
            self.wfile.write(json.dumps(data))
        else:
            self.wfile.write(data)

def run(conf_file, PORT_NUMBER):
    try:
        f = open(conf_file, 'rb')
        raw = f.read()
        f.close()
        try:
            global CONF
            CONF = json.loads(raw)
        except:
            exit('Cant Read JSON file, make sure you have valid json')
    except IOError:
        exit('Cant Open %s' % conf_file)

    try:
        server = HTTPServer(('', PORT_NUMBER), WebHandler)
        print 'Started httpserver on port ' , PORT_NUMBER
        server.serve_forever()

    except KeyboardInterrupt:
        print '^C received, shutting down the web server'
        server.socket.close()


HELP_TEXT = """
    faker.py -- A Protyping webserver
    Usage:
        Run Server:
        python faker.py path_to_conf_file.json PORT(optional)

        Kill it with ^C

        More:
        See sample_conf.json for example

"""


if __name__ == '__main__':

    if len(sys.argv) < 2:
        exit(HELP_TEXT)
    elif sys.argv[1] == "--help":
        exit(HELP_TEXT)
    else:
        CONF_FILE = sys.argv[1]
        try:
            PORT_NUMBER = sys.argv[2]
        except IndexError:
            PORT_NUMBER = 8888

        run(CONF_FILE, PORT_NUMBER)
