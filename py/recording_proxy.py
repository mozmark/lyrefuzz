import config
import sys
import BaseHTTPServer
import json
import logging
import os
import platform
import re
import time
import traceback
import threading
import urllib

import httplib2

logger = logging.getLogger('Recorder-Proxy')
ch = logging.FileHandler('recorder-proxy.log')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


lyre_recorder = None

class RecorderRequestServer(BaseHTTPServer.HTTPServer):
    def __init__(self, *args, **kwargs):
        self.runner = None
        BaseHTTPServer.HTTPServer.__init__(self, *args, **kwargs)

    def __del__(self):
        pass

LYRE_RECORD = 1
LYRE_REPLAY = 2

pathRe = re.compile(r'/session/(.*?)($|/((\w+/(.*?)/)?(.*)))')

def extract_session_and_element(path):
    session = element = None
    m = pathRe.search(path)
    if m:
        session = m.group(1)
        element = m.group(5)
        if element is not None:
            element = urllib.unquote(element)
    return session, element

class LyreRecorder:
    running = True

    # we need to map session IDs two ways; from recorded to actual and vice
    # versa
    recorded_to_actual = {}
    actual_to_recorded = {}

    def __init__(self, filename, mode):
        self.mode = mode
        file_mode = 'r'
        if self.is_recording():
            file_mode = 'w'
        self.recording = open(filename,file_mode)

    def replace_session_in_path(self, path):
        recorded, element = extract_session_and_element(path)
        if recorded:
            actual = recorded
            try:
                actual = self.recorded_to_actual[recorded]
            except:
                pass
            return path.replace(recorded, actual)
        return path


    def is_recording(self):
        return self.mode == LYRE_RECORD

    def make_request(self, path, method, body, headers):
        http = httplib2.Http()
        response, content = http.request(config.base+path, method=method, body=body, headers=headers)
        recdata = {'path':path,
                'method':method,
                'body':body,
                'headers':headers,
                'response':response,
                'content':content}
        if self.is_recording():
            self.recording.write(json.dumps(recdata)+'\n')
            self.recording.flush()
        else:
            # Maybe throw - this makes no sense
            pass
        return response, content

    def play(self):
        for line in self.recording.readlines():
            self.currentLine = line
            recorded = json.loads(line)
            recorded_content = None
            try:
                recorded_content = json.loads(recorded['content'])
            except:
                pass

            # take the element and session from the original conversation
            recorded_path_session, recorded_path_element = extract_session_and_element(recorded['path'])
            parsed_response = None

            # try to substitute the path
            path = self.replace_session_in_path(recorded['path'])

            http = httplib2.Http()
            response, content = http.request(config.base+path,
                    method = recorded['method'],
                    body = recorded['body'],
                    headers = recorded['headers'])
            try:
                parsed_response = json.loads(content)
                # TODO: doing this here is fugly; we should be more state aware
                if None == recorded_path_session:
                    if True and None != recorded_content:
                        recorded_session = recorded_content['sessionId']
                        actual_session = parsed_response['sessionId']
                        self.recorded_to_actual[recorded_session] = actual_session
                        self.actual_to_recorded[actual_session] = recorded_session
            except:
                pass
            if recorded['path'].endswith('session'):
                time.sleep(0.05)
        self.running = False

    def getCurrentLine(self):
        return self.currentLine

class RecorderRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def headers_as_dict(self):
        headers = self.headers
        keys = headers.keys()
        headers_dict = {}
        for (key, value) in [(key, headers.getheader(key)) for key in keys]:
            headers_dict[key] = value
        return headers_dict

    def do_request(self, method):
        path = self.path

        session, element = extract_session_and_element(self.path)
        headers = self.headers_as_dict()
        body = None
        try:
            content_len = headers['content-length']
            body = self.rfile.read(int(content_len))
        except:
            pass

        http = httplib2.Http()
        response, content = lyre_recorder.make_request(path, method=method, body=body, headers=headers)

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

        try:
            parsed_data = json.loads(content)
        except:
            pass
        self.wfile.write(content)

    def do_REQ(self, method):
        self.do_request(method)

    def do_GET(self):
        return self.do_REQ('GET')

    def do_DELETE(self):
        return self.do_REQ('DELETE')

    def do_POST(self):
        return self.do_REQ('POST')

class RecorderProxy(object):
    def __init__(self, remote_host='localhost', proxy_port=5555):
        self.remote_host = remote_host
        self.proxy_port = proxy_port

    def start(self):
        logger.info("Starting the Recorder Proxy. Server is running is running on %s:%s" \
                     % ("localhost", self.proxy_port) )
        httpd = RecorderRequestServer(('0.0.0.0', self.proxy_port), RecorderRequestHandler)
        httpd.serve_forever()

class OracleRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    recorder = None

    def do_GET(self):
        print 'Got one!', self.path
        if self.recorder:
            print "line is ", self.recorder.getCurrentLine()
        self.wfile.write("Whoa!")

class OracleServer(threading.Thread):
    def __init__(self, recorder, host="localhost", port=8081):
        threading.Thread.__init__(self)
        self.recorder = recorder
        self.host = host
        self.port = port

    def run(self):
        print 'RUNNNN!!!!!'
        OracleRequestHandler.recorder = self.recorder
        logger.info("Starting the Oracle Server. Server is running on %s:%s" % ("localhost", self.port))
        httpd = BaseHTTPServer.HTTPServer(('0.0.0.0', self.port), OracleRequestHandler)
        while self.recorder.running:
            httpd.handle_request()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == 'play':
        lyre_recorder = LyreRecorder('recording.json', LYRE_REPLAY)
        oracle = OracleServer(lyre_recorder)
        oracle.start()
        print 'in replay mode'
        lyre_recorder.play()
    else:
        lyre_recorder = LyreRecorder('recording.json', LYRE_RECORD)
        print 'in record mode'
        proxy = RecorderProxy()
        proxy.start()
