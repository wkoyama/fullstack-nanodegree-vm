# from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from http.server import BaseHTTPRequestHandler, HTTPServer
import cgi

# import CRUD Operations from Lesson 1
from database_setup import Base, Restaurant, MenuItem
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Create session and connect to DB
engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

class webServerHandler(BaseHTTPRequestHandler):

	def do_GET(self):
		try:
			if self.path.endswith("/restaurants"):
				restaurants = session.query(Restaurant).all()
				output = ""
				self.send_response(200)
				self.send_header('Content-type', 'text/html')
				self.end_headers()

				output += "<html><body>"
				for restaurant in restaurants:
					output += restaurant.name
					output += "</br></br></br>"

				output += "</body></html>"
				self.wfile.write(output)
				return

		except IOError:
			self.send_error(404, 'File Not Found: %s' % self.path)

def main():
	try:
		port = 80
		server = HTTPServer(('', port), webServerHandler)
		print('Web Server running on port %s' % port)
		server.serve_forever()
	except KeyboardInterrupt:
		print(" ^C entered, stopping web server....")
		server.socket.close()

if __name__ == '__main__':
    server_address = ('', 8000)
    httpd = http.server.HTTPServer(server_address, Shortener)
    httpd.serve_forever()