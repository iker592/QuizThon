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


insertquestion_form='''
<html> 
<head> 
	<link type="text/css" rel="stylesheet" href="/stylesheets/main.css" /> 
	<title>Introduce una pregunta:</title> 
	<style type="text/css"> .label {text-align: right} .error {color: red} </style>
	<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.2.1/jquery.min.js"></script>
		<script>
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
</head> 
<body> 
	<h1>Adding a new Question</h1> 
	<h2>Fill and submit the form please:</h2> 
	<form method="post"> 
		<table> 
			<tr> <td class="label">Question</td> 
				<td> <input type="text" name="question" value="%(question)s" placeholder="Your question ..."> </td> 
				<td class="error"> %(question_error)s </td> 
			</tr> 
			<tr> <td class="label"> First Option </td> 
				<td> <input type="text" name="firstopt" value="%(firstopt)s"> </td> 
				<td class="error"> %(firstopt_error)s </td>
			</tr> 
			<tr> <td class="label"> Second Option </td>
				<td> <input type="text" name="secondopt" value="%(secondopt)s"> </td> 
				<td class="error"> %(secondopt_error)s </td> 
			</tr>
			<tr> <td class="label"> Third Option </td>
				<td> <input type="text" name="thirdopt" value="%(thirdopt)s"> </td> 
				<td class="error"> %(thirdopt_error)s </td> 
			</tr> 
		</table> 
		<input type="submit"> 
	</form> 
</body> 
</html>'''

answerquestion_form='''
<html> 
<head> 
	<link type="text/css" rel="stylesheet" href="/stylesheets/main.css" /> 
	<title>Answer the question:</title> 
	<style type="text/css"> .label {text-align: right} .error {color: red} </style>
	<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.2.1/jquery.min.js"></script>
		<script>
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
</head> 
<body> 
	<h1>Answering a Question</h1> 
	<h2>Answer the question please:</h2> 
	<form method="post"> 
		<table> 
			<tr> <td class="label">%(question)s</td> 
			</tr> 
			<tr> <td class="label"> 1) </td> 
				<td> <input type="radio" name="opt" value="%(firstopt)s" checked>%(firstopt)s <br> </td> 
				<td class="error"> %(firstopt_error)s </td>
			</tr> 
			<tr> <td class="label"> 2) </td>
				<td> <input type="radio" name="opt" value="%(secondopt)s"> %(secondopt)s<br></td> 
				<td class="error"> %(secondopt_error)s </td> 
			</tr>
			<tr> <td class="label"> 3) </td>
				<td> <input type="radio" name="opt" value="%(thirdopt)s"> %(thirdopt)s</td> 
				<td class="error"> %(thirdopt_error)s </td> 
			</tr> 
		</table> 
		<input type="submit"> 
	</form> 
</body> 
</html>'''


class AnswerHandler(session_module.BaseSessionHandler):

	def write_form (self, question="", firstopt="", secondopt="", thirdopt="", firstopt_error="", secondopt_error="", thirdopt_error=""):
		self.response.out.write(answerquestion_form % {"question" :
		question,"firstopt" : firstopt,
		"secondopt" : secondopt,"thirdopt" : thirdopt,
		"firstopt_error" : firstopt_error,
		"secondopt_error" : secondopt_error,
		"thirdopt_error" : thirdopt_error})

	def get(self):
		def escape_html(s):
			return cgi.escape(s, quote=True)
		question=""
		questionQuery= Question.query(Question.question=="Which is the first president of the USA?")
		if questionQuery.count()==1:
			question=questionQuery.get()
			firstopt_error = ""
			secondopt_error = "" 
			thirdopt_error = ""
			sani_question = escape_html(question.question)
			sani_firstopt = escape_html(question.first)
			sani_secondopt = escape_html(question.second)
			sani_thirdopt = escape_html(question.third)
			self.write_form(sani_question, sani_firstopt, sani_secondopt, sani_thirdopt, firstopt_error, secondopt_error, thirdopt_error)
		else:
			self.write_form()
			self.response.out.write ("No fak were given")

	def post(self):
		questionQuery= Question.query(Question.question=="Which is the first president of the USA?")
		if questionQuery.count()==1:
			question=questionQuery.get()
			if question.first==self.request.get('opt')	or question.second==self.request.get('opt') or question.third==self.request.get('opt'):
				self.write_form()
				self.response.out.write ("yay!")
			else:
				self.write_form()
				self.response.out.write ("duuude...")

class InsertHandler(session_module.BaseSessionHandler):

	def write_form (self, question="", firstopt="", secondopt="",
	thirdopt="", question_error="", firstopt_error="",
	secondopt_error="", thirdopt_error=""):
		self.response.out.write(insertquestion_form % {"question" :
		question,"firstopt" : firstopt,
		"secondopt" : secondopt,"thirdopt" : thirdopt,
		"question_error" : question_error,
		"firstopt_error" : firstopt_error,
		"secondopt_error" : secondopt_error,
		"thirdopt_error" : thirdopt_error})

	def get(self):
		self.write_form()

	def post(self):
		def escape_html(s):
			return cgi.escape(s, quote=True)
		QUESTION_RE = re.compile(r"^[a-zA-Z0-9_-]+( [a-zA-Z0-9_?]+)*$")
		def valid_question(question):
			return QUESTION_RE.match(question)
		u_question = self.request.get('question')
		u_firstopt = self.request.get('firstopt')
		u_secondopt = self.request.get('secondopt')
		u_thirdopt = self.request.get('thirdopt')
		sani_question = escape_html(u_question)
		sani_firstopt = escape_html(u_firstopt)
		sani_secondopt = escape_html(u_secondopt)
		sani_thirdopt = escape_html(u_thirdopt)
		question_error = ""
		firstopt_error = ""
		secondopt_error = "" 
		thirdopt_error = ""
		question=""
		error = False
		if not valid_question(u_question):
			question_error = "Wrong type question!"
			error = True
		if not valid_question(u_firstopt):
			firstopt_error = "Wrong type of answer in first option!"
			error = True
		if not valid_question(u_secondopt):
			secondopt_error = "Wrong type of answer in second option!"
			error = True
		if not valid_question(u_thirdopt):
			thirdopt_error = "Wrong type of answer in third option!"
			error = True
		if error:
			self.write_form(sani_question, sani_firstopt, sani_secondopt, thirdopt_error,question_error, firstopt_error, secondopt_error, thirdopt_error)
		else:
			question= Question.query(Question.question==u_question).count()
			if question==0:
				q=Question()
				q.question=u_question
				q.first=u_firstopt
				q.second=u_secondopt
				q.third=u_thirdopt
				q.put()
				self.redirect("/welcome?username=%s" "Poner username de la sesion")
			else:
				self.write_form(sani_question, sani_firstopt, sani_secondopt, thirdopt_error,question_error, firstopt_error, secondopt_error, thirdopt_error)
				self.response.out.write ("Question: %s <p> was already inserted" %u_question)

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

class Question(ndb.Model):
	question=ndb.StringProperty()
	first=ndb.StringProperty()
	second=ndb.StringProperty()
	third=ndb.StringProperty()
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
    ('/insert', InsertHandler),
    ('/answer', AnswerHandler),
    ('/comprobar',ComprobarEmail)
], config=session_module.myconfig_dict, debug=True)