#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import re
import cgi

from google.appengine.api import users

import session_module
from webapp2_extras import sessions 


from google.appengine.ext import ndb

signup_form='''<html> <head> <link type="text/css" rel="stylesheet"
href="/stylesheets/main.css" /> <title>Introduzca sus datos:</title> <style
type="text/css"> .label {text-align: right} .error {color: red} </style>
<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.2.1/jquery.min.js"></script>

<script>
$(document).ready(function(){
    $("button").click(function(){
        $("p").hide();
    });
});

function validarEmail(email)
{$("#erroremail").html('Procesando...');
$.ajax("/comprobar",
	{"type": "post",
	"data":{"email":email},
	"success": function(result) {
	$("#erroremail").html(result);},
	"error": function(result)
			{ console.error("Se ha producido un error:", result);}, "async": true })}
</script>

</head> <body> 

<p>This is a paragraph.</p>
<p>This is another paragraph.</p>
<button>Click me</button>

<h1>DSSW-Tarea 2</h1> <h2>Rellene los campos por
favor:</h2> <form method="post"> <table> <tr> <td
class="label"> Nombre de usuario </td> <td> <input
type="text" name="username" value="%(username)s" placeholder="Tu nombre
..."> </td> <td class="error"> %(username_error)s
</td> </tr> <tr> <td class="label"> Password
</td> <td> <input type="password" name="password"
value="%(password)s" autocomplete="off"> </td> <td
class="error"> %(password_error)s </td> </td>
</tr> <tr> <td class="label"> Repetir Password </td>
<td> <input type="password" name="verify" value="%(verify)s"
placeholder="El mismo de antes"> </td> <td class="error">
%(verify_error)s </td> </tr> 
<tr> <td class="label">Email </td> <td> <input type="text" name="email" id="email" onBlur="validarEmail(this.value)" value="%(email)s"><div id="erroremail"></div> 
</td> <td class="error">
%(email_error)s </td> </tr> </table> <input
type="submit"> </form> </body> </html>'''

class ComprobarEmail(webapp2.RequestHandler):
	def post(self):
		user = Visitante.query(Visitante.email==self.request.get('email')).count()
		if user==0 and self.request.get('email')!="":
			self.response.out.write("<span style='color:green'>Email -> " +self.request.get('email')+ " <- Correcto</span>")
		else:
			self.response.out.write("<span style='color:red'>Este email ya esta registrado o no es valido</span>")


class Visitante(ndb.Model):
	nombre=ndb.StringProperty()
	email=ndb.StringProperty()
	password=ndb.StringProperty(indexed=True)
	creado=ndb.DateTimeProperty(auto_now_add=True)

class SignupHandler(session_module.BaseSessionHandler):

	def write_form (self, username="", password="", verify="",
	email="", username_error="", password_error="",
	verify_error="", email_error=""):
		self.response.out.write(signup_form % {"username" :
		username,"password" : password,
		"verify" : verify,"email" : email,
		"username_error" : username_error,
		"password_error" : password_error,
		"verify_error" : verify_error,
		"email_error" : email_error})

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
				self.redirect("/welcome?username=%s" % user_username)
			else:
				self.write_form(sani_username, sani_password, sani_verify, sani_email,username_error, password_error, verify_error, email_error)
				self.response.out.write ("Kaixo: %s <p> Ya estabas fichado" %user_username)


class WelcomeHandler(session_module.BaseSessionHandler):
	def get(self):
		greeting = ('Saludos, %s <p><a href="%s">Sign out </a><br>' %(self.request.get('username'), users.create_logout_url('/')))
		self.response.out.write('<html><body><h1>%s</h1></body></html>' %greeting) 

class MainHandler(session_module.BaseSessionHandler):
	def get(self):
		user = users.get_current_user()
		if user:
			greeting = ('Saludos, %s <p><a href="%s">Sign out </a><br>' %(user.nickname(), users.create_logout_url('/')))
			self.response.out.write('<html><body><h1>%s</h1></body></html>' %greeting)  
		else:
			self.redirect(users.create_login_url(self.request.uri))
class PruebaHandler(session_module.BaseSessionHandler):
	def get(self):
		if self.session.get('counter'):
			self.response.out.write('<b>La sesion existe</b><p>')
			counter = self.session.get('counter')
			self.session['counter'] = counter + 1
			self.response.out.write('<h2>Numero de accesos = ' +
			 str(self.session.get('counter'))+'</h2>')
		else:
			self.response.out.write('<b>No habia sesion Sesion Creada</b><p>')
			self.session['counter'] = 1
			self.response.out.write('<h2>Numero de accesos = ' +
			str(self.session.get('counter'))+'</h2>')
class CerrarSesionHandler(session_module.BaseSessionHandler):
	def get(self):
		for k in self.session.keys():
			del self.session[k]
			self.response.out.write ("Borrada la sesion ...")
		self.response.out.write("<p><h2><a href='/prueba'> Ir a inicio ...</a></h2>")
app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/prueba', PruebaHandler),
    ('/signup', SignupHandler),
    ('/cerrarsesion', CerrarSesionHandler),
    ('/welcome',WelcomeHandler),
    ('/comprobar',ComprobarEmail)
], config=session_module.myconfig_dict, debug=True)