import http.server
import socketserver
import json
import os
from urllib.parse import urlparse, parse_qs
from jinja2 import Environment, FileSystemLoader

PORT = 8000
DATA_FILE = os.path.join("data", "content.json")
TEMPLATE_DIR = "templates"
STATIC_DIR = "static"


def load_data():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

class MyHandler(http.server.SimpleHTTPRequestHandler):
    def render_template(self, template_name, **kwargs):
            env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
            template = env.get_template(template_name)
            content = template.render(**kwargs)
            return content.encode('utf-8')


    def do_GET(self):
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        query_params = parse_qs(parsed_url.query)
        data = load_data()

        if path == "/":
             content = self.render_template("index.html", **data)
             self.send_response(200)
             self.send_header("Content-type", "text/html")
             self.end_headers()
             self.wfile.write(content)

        elif path == "/products":
             content = self.render_template("products.html", **data)
             self.send_response(200)
             self.send_header("Content-type", "text/html")
             self.end_headers()
             self.wfile.write(content)

        elif path == "/about":
             content = self.render_template("about.html", **data)
             self.send_response(200)
             self.send_header("Content-type", "text/html")
             self.end_headers()
             self.wfile.write(content)


        elif path == "/contact":
              if 'search' in query_params:
                  search_term = query_params['search'][0]
              else:
                  search_term = ''

              content = self.render_template("contact.html", search_term=search_term, **data)
              self.send_response(200)
              self.send_header("Content-type", "text/html")
              self.end_headers()
              self.wfile.write(content)


        elif path.startswith("/static/"):
             file_path = os.path.join(STATIC_DIR, path[len("/static/"):])
             if os.path.exists(file_path) and os.path.isfile(file_path):
                 try:
                     with open(file_path, 'rb') as f:
                         content = f.read()
                     mime_type = self.guess_type(file_path)[0] or 'application/octet-stream'
                     self.send_response(200)
                     self.send_header("Content-type", mime_type)
                     self.end_headers()
                     self.wfile.write(content)
                 except Exception as e:
                    print(f"Error reading file: {e}")
                    self.send_error(404)

             else:
                self.send_error(404)

        else:
            self.send_error(404)


    def do_POST(self):
          content_length = int(self.headers['Content-Length'])
          post_data = self.rfile.read(content_length).decode('utf-8')
          query_params = parse_qs(post_data)
          data = load_data()
          if 'feedback' in query_params and 'page' in query_params:
               feedback = query_params['feedback'][0]
               page = query_params['page'][0]

               print(f"Feedback received from page '{page}': {feedback}")
               content = self.render_template("about.html", **data, feedback_message="Спасибо за ваш отзыв!")
               self.send_response(200)
               self.send_header("Content-type", "text/html")
               self.end_headers()
               self.wfile.write(content)
          else:
            self.send_error(400, "Invalid POST data")



 
if __name__ == "__main__":
    with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
        print(f"Serving on port {PORT}")
        httpd.serve_forever()