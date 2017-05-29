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


class SignupHandler(session_module.BaseSessionHandler):
	def write_form (self, username="", password="", verify="", email="", username_error="", password_error="", verify_error="", email_error=""):
		#self.response.out.write(login_form % {"username" : username,"password" : password, "verify" : verify,"email" : email,"username_error" : username_error,"password_error" : password_error,"verify_error" : verify_error,"email_error" : email_error})
		tem_values = {"username" : username,"password" : password, "verify" : verify,"email" : email,"username_error" : username_error,"password_error" : password_error,"verify_error" : verify_error,"email_error" : email_error}
		template = JINJA_ENVIRONMENT.get_template('signup.html')
		self.response.write(template.render(tem_values))
	def get(self):
		self.write_form()
	def post(self):
		def escape_html(s):
			return cgi.escape(s, quote=True)
		USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
		PASSWORD_RE = re.compile(r"^.{3,20}$")
		EMAIL_RE = re.compile(r"^[\S]+@[\S]+\.[\S]+$")
		def valid_username(username):
			return USER_RE.match(username)
		def valid_password(password):
			return PASSWORD_RE.match(password)
		def valid_email(email):
			return EMAIL_RE.match(email)
		user_username = self.request.get('username')
		user_password = self.request.get('password')
		user_verify = self.request.get('verify')
		user_email = self.request.get('email')
		sani_username = escape_html(user_username)
		sani_password = escape_html(user_password)
		sani_verify = escape_html(user_verify)
		sani_email = escape_html(user_email)
		username_error = ""
		password_error = ""
		verify_error = "" 
		email_error = ""
		user=""
		error = False
		if not valid_username(user_username):
			username_error = "Nombre incorrecto!"
			error = True
		if not valid_password(user_password):
			password_error = "Password incorrecto!"
			error = True
		if not user_verify or not user_password == user_verify:
			verify_error = "Password no coincide!"
			error = True
		if not valid_email(user_email):
			email_error = "Formato de Email incorrecto!"
			error = True
		if error:
			self.write_form(sani_username, sani_password, sani_verify, sani_email,username_error, password_error, verify_error, email_error)
		else:
			user= Visitante.query(Visitante.nombre==user_username, Visitante.email==user_email).count()
			if user==0:
				u=Visitante()
				u.nombre=user_username
				u.email=user_email
				u.password=user_password
				u.put()
				self.session['username']=user_username
				self.redirect("/manage?username=%s" % user_username)
			else:
				self.redirect("/manage")
				self.write_form(sani_username, sani_password, sani_verify, sani_email,username_error, password_error, verify_error, email_error)
				self.response.out.write ("Kaixo: %s <p> Ya estabas fichado" %user_username)