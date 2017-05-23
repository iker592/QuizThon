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

from models import *

class LoginHandler(session_module.BaseSessionHandler):
	def write_form (self, username="", password="", verify="", email="", username_error="", password_error="", verify_error="", email_error=""):
		#self.response.out.write(login_form % {"username" : username,"password" : password, "verify" : verify,"email" : email,"username_error" : username_error,"password_error" : password_error,"verify_error" : verify_error,"email_error" : email_error})
		tem_values = {"username" : username,"password" : password, "verify" : verify,"email" : email,"username_error" : username_error,"password_error" : password_error,"verify_error" : verify_error,"email_error" : email_error}
		template = JINJA_ENVIRONMENT.get_template('login.html')
		self.response.write(template.render(tem_values))
	def get(self):
		self.write_form()
	def post(self):
		user_username = self.request.get('username')
		user_password = self.request.get('password')
		user= Visitante.query(Visitante.nombre==user_username, Visitante.password==user_password).count()
		if user==1:
			self.redirect("/manage?username=%s" % user_username)
		else:
			self.redirect('/login')
