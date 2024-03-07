from functools import cached_property
import re 
import redis
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qsl, urlparse

# Código basado en:
# https://realpython.com/python-http-server/
# https://docs.python.org/3/library/http.server.html
# https://docs.python.org/3/library/http.cookies.html

mappings = [(r"^/books/(?P<book_id>\d+)$", "get_book"),
            (r"^/book/(?P<book_id>\d+)$", "get_book"), 
            (r"^/$", "index"),]
            
r = redis.StrictRedis(host="localhost", port = 6379, db = 0)

class WebRequestHandler(BaseHTTPRequestHandler):
    @cached_property
    def url(self):
        return urlparse(self.path)

    @cached_property
    def query_data(self):
        return dict(parse_qsl(self.url.query))

    @cached_property
    def cookies(self):
        return SimpleCookie(self.headers.get("Cookie"))

    def do_GET(self):
        #match = self.get_params(r"^/books/(?P<book_id>\d+)$", self.path)
        #if match:
            # self.get_book(match["book_id"])
             #self.wfile.write(f"<h1> El path {self.path} es correcto </h1>".encode("utf-8"))
        #else:
             #self.wfile.write(f"<h1> El path {self.path} es incorrecto </h1>".encode("utf-8"))
             # self.index()
        self.url_mapping_response()

    def get_params(self, pattern, path):
        match = re.match(pattern,path)
        if match:
            return match.groupdict()
      
    def url_mapping_response(self):
        for (parrent, method) in mappings:
            match = self.get_params(parrent, self.path)
            print(match)
            if match is not None:
                md = getattr(self, method)
                md(**match)
                return
            
        self.send_response(404)
        self.end_headers()
        self.wfile.write("Not Found".encode("utf-8"))
 
    def index(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        index_page = f"<h1> Bienvenidos a los libros </h1>".encode("utf-8")
        self.wfile.write(index_page)
        
    def get_book(self,book_id):
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        #book_info = f"<h1> Info del libro {book_id} es correcto </h1>".encode("utf-8")
        book_info = r.get(f"book:{book_id}") or "No existe libro".encode("utf-8")
        self.wfile.write(book_info)
    
    def get_response(self):
        pattern = r'/books/(?P<id>\d+)'
        return f"""
    <h1> Hola Web </h1>
    <p>  {self.path}         </p>
    <p>  {self.get_params(self.path, pattern)}  </p>
    <p>  {self.headers}      </p>
    <p>  {self.cookies}      </p>
    <p>  {self.query_data}   </p>
"""


if __name__ == "__main__":
    print("Server starting...")
    server = HTTPServer(("0.0.0.0", 8000), WebRequestHandler)
    server.serve_forever()