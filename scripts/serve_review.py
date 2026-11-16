"""Local review server mirroring the proposed query rules; not a staging deployment."""
import argparse,functools,re
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from urllib.parse import urlsplit
class ReviewHandler(SimpleHTTPRequestHandler):
    def send_head(self):
        self.original=self.path
        url=urlsplit(self.path)
        if url.path.rstrip('/')=='/categories/nurses' or (url.path=='/' and url.query=='category=nurses'):
            self.send_response(301);self.send_header('Location','/');self.send_header('Content-Length','0');self.end_headers();return None
        if url.path=='/' and url.query:
            m=re.fullmatch(r'category=(hospitals|pharmacies)',url.query)
            if m or url.query=='category=care':
                self.send_response(301);self.send_header('Location','/categories/'+m[1]+'/' if m else '/');self.send_header('Content-Length','0');self.end_headers();return None
            self.path='/seo/noindex.html'
        return super().send_head()
    def send_error(self,code,message=None,explain=None):
        if code==404:
            from pathlib import Path
            data=(Path(self.directory)/'404.html').read_bytes()
            self.send_response(404);self.send_header('Content-Type','text/html; charset=utf-8');self.send_header('X-Robots-Tag','noindex, follow');self.send_header('Content-Length',str(len(data)));self.end_headers()
            if self.command!='HEAD':self.wfile.write(data)
        else:super().send_error(code,message,explain)
    def log_message(self,*args):pass
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--directory',required=True);p.add_argument('--port',type=int,default=8768);a=p.parse_args()
    server=ThreadingHTTPServer(('127.0.0.1',a.port),functools.partial(ReviewHandler,directory=a.directory))
    print('Local review only: http://127.0.0.1:'+str(a.port),flush=True);server.serve_forever()
