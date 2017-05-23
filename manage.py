import webapp2
import re
import cgi
import jinja2
import os
from google.appengine.api import users

import session_module
from webapp2_extras import sessions 


from google.appengine.ext import ndb

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class ManageHandler(session_module.BaseSessionHandler):
	def write_form (self):
		template = JINJA_ENVIRONMENT.get_template('manage.html')
		self.response.write(template.render())
	def get(self):
		greeting = ('Hi, %s! <p>' %(self.request.get('username')))
		self.write_form()
		self.response.out.write('<h3>%s</h3>' %greeting)