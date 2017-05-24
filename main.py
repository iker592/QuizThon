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
main_form=''' 
<!DOCTYPE html>
<html>
<head> 
	<link type="text/css" rel="stylesheet" href="/stylesheets/main.css" />
</head> 
<body>
	<button type="button" onclick="window.location.href='/login'">Login</button></br> 
	<button type="button" onclick="window.location.href='/signup'">Sign Up</button> </br> 
	<button type="button" onclick="window.location.href='/prueba'">Take a Quiz!</button> </br> 
</body>
</html>
'''

manage_form=''' 
<!DOCTYPE html>
<html>
<head> 
	<link type="text/css" rel="stylesheet" href="/stylesheets/main.css" />
</head> 

<body>
	<button type="button" onclick="window.location.href='/cerrarsesion'">Logout</button> </br> 
	<button type="button" onclick="window.location.href='/insert'">Add a question</button> </br> 
	<button type="button" onclick="window.location.href='/prueba'">Take a Quiz!</button> </br> 
</body>
</html>
'''

signup_form='''<html> <head> <link type="text/css" rel="stylesheet"
href="/stylesheets/main.css" /> <title>Introduzca sus datos:</title> <style
type="text/css"> .label {text-align: right} .error {color: red} </style>
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
<h1>Sign up</h1> <h2>Please fill up the blanks:</h2> <form method="post"> <table> <tr> <td
class="label"> Username </td> <td> <input
type="text" name="username" value="%(username)s" placeholder="Tu nombre
..."> </td> <td class="error"> %(username_error)s
</td> </tr> <tr> <td class="label"> Password
</td> <td> <input type="password" name="password"
value="%(password)s" autocomplete="off"> </td> <td
class="error"> %(password_error)s </td> </td>
</tr> <tr> <td class="label"> Repeat Password </td>
<td> <input type="password" name="verify" value="%(verify)s"
placeholder="El mismo de antes"> </td> <td class="error">
%(verify_error)s </td> </tr> 
<tr> <td class="label">Email </td> <td> <input type="text" name="email" id="email" onBlur="validarEmail(this.value)" value="%(email)s"><div id="erroremail"></div> 
</td> <td class="error">
%(email_error)s </td> </tr> 
</table> 
<input type="submit"> 
</form> 
</body> 
</html>'''

login_form='''
<html> 
	<head> 
	<link type="text/css" rel="stylesheet" href="/stylesheets/main.css" /> 
	<title>Introduzca sus datos:</title> 
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
	<h1>Login</h1>
	<h2>Please fill up the blanks:</h2> 
		<form method="post"> 
			<table> 
				<tr> 
					<td class="label"> Username </td> 
					<td> <input type="text" name="username" value="%(username)s" placeholder="Tu nombre..."> </td> 
					<td class="error"> %(username_error)s </td> 
				</tr> 
				<tr> <td class="label"> Password </td> 
					<td> <input type="password" name="password" value="%(password)s" autocomplete="off"> </td> 
					<td class="error"> %(password_error)s </td> </td>
				</tr>  

			</table> 
			<input type="submit"> 
		</form>
	</body> 
</html>'''

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
			<tr> <td class="label"> Theme </td>
				<td> <input type="text" name="theme" value="%(theme)s"> </td> 
				<td class="error"> %(theme_error)s </td> 
			</tr> 
			<tr> <td class="label"> Correct Option </td>
				<td> <input type="text" name="correct" value="%(correct)s"> </td> 
				<td class="error"> %(correct_error)s </td> 
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


listquestion_form='''
<html> 
<head> 
	<link type="text/css" rel="stylesheet" href="/stylesheets/main.css" /> 
	<title>Answer the question:</title> 
	<style type="text/css"> .label {text-align: right} .error {color: red} </style>
</head> 
<body> 
	<h1>Answering a Question</h1> 
	<h2>Answer the question please:</h2> 
	<form method="post"> 
		{% for greeting in greetings %}

		<input type="submit"> 
	</form> 
</body> 
</html>'''


class ResultHandler(session_module.BaseSessionHandler):
	def get(self):
		questionQuery= Question.query(Question.question==self.request.get('questions'))
		if questionQuery.count()==1:
			question=questionQuery.get()
			if question.first==self.request.get('opt')	or question.second==self.request.get('opt') or question.third==self.request.get('opt'):
				#self.write_form()
				self.response.out.write ("yay!")
				self.redirect("/prueba?result=Correct answer!!! Select another one or leave whenever you want.")
			else:
				#self.write_form()
				self.response.out.write ("duuude...")
				self.redirect("/prueba?result=Wrong answer :( Try again or leave whenever you want!")

class FillAnswerHandler(webapp2.RequestHandler):
	def write_form (self, question="", firstopt="", secondopt="", thirdopt="", firstopt_error="", secondopt_error="", thirdopt_error=""):
			tem_values = {"question" : question,"firstopt" : firstopt, "secondopt" : secondopt,"thirdopt" : thirdopt,"firstopt_error" : firstopt_error,	"secondopt_error" : secondopt_error,"thirdopt_error" : thirdopt_error}
			template = JINJA_ENVIRONMENT.get_template('fillanswer.html')
			self.response.write(template.render(tem_values))
	def post(self):
		def escape_html(s):
			return cgi.escape(s, quote=True)
		#self.response.out.write("<span style='color:red'>Este es valido</span>")
	#	questionQuery=Question.query(Question.question=="Which is the first president of the USA?")#self.request.get('question')
		question=""
		questionQuery= Question.query(Question.question==self.request.get('question'))
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
			self.response.out.write ("damn no questions bruh")

class FillThemeHandler(webapp2.RequestHandler):
	def write_form (self, question="", firstopt="", secondopt="", thirdopt="", firstopt_error="", secondopt_error="", thirdopt_error=""):
			tem_values = {"question" : question,"firstopt" : firstopt, "secondopt" : secondopt,"thirdopt" : thirdopt,"firstopt_error" : firstopt_error,	"secondopt_error" : secondopt_error,"thirdopt_error" : thirdopt_error}
			template = JINJA_ENVIRONMENT.get_template('fillanswer.html')
			self.response.write(template.render(tem_values))
	def post(self):
		def escape_html(s):
			return cgi.escape(s, quote=True)
		#self.response.out.write("<span style='color:red'>Este es valido</span>")
	#	questionQuery=Question.query(Question.question=="Which is the first president of the USA?")#self.request.get('question')
		question=""
		questionQueryThemes = ndb.gql("SELECT DISTINCT question FROM Question WHERE theme = :1", self.request.get('theme'))

		questionQuery= Question.query(Question.theme==self.request.get('theme')) 
		#TODO: extraer exactamente la pregunta numero X que queremos, HAY Q LLEVAR LA CUENTA DE DONDE ESTAMOS DE ALGUNA FORMA
		if questionQuery.count()>0:
			tope =questionQuery.count()
			count=0
			while (count < tope ):#or question != self.request.get('question')):
				question=questionQuery.get()
				count = count + 1
#			if(question == self.request.get('question') or (self.request.get('question')=="" and questionQueryThemes.count>0))
#				question=questionQueryThemes.get()
			firstopt_error = ""
			secondopt_error = "" 
			thirdopt_error = ""
			sani_question = escape_html(question.question)
			sani_firstopt = escape_html(question.first)
			sani_secondopt = escape_html(question.second)
			sani_thirdopt = escape_html(question.third)
			self.write_form(sani_question, sani_firstopt, sani_secondopt, sani_thirdopt, firstopt_error, secondopt_error, thirdopt_error)
		else:
			self.response.out.write ("damn no questions bruh")

class PlayHandler(session_module.BaseSessionHandler):
	def write_form (self, mylist,mylistThemes,result):
		tem_values = {"mylist" : mylist,"mylistThemes" : mylistThemes, "result":result}
		template = JINJA_ENVIRONMENT.get_template('listanswer.html')
		self.response.write(template.render(tem_values))
	def get(self):
#		user = users.get_current_user()
#		if user:
#			greeting = ('Logged as: %s <a href="%s">Finish session </a><br>' %(user.nickname(), users.create_logout_url('/')))
			result=self.request.get('result')

			questionQuery= Question.query()
			questionQueryThemes = ndb.gql("SELECT DISTINCT theme FROM Question ") #+ "WHERE theme = :1", self.request.get('theme'))
#			self.response.out.write('<h2>%s</h2>' %greeting)  	
			self.write_form(questionQuery,questionQueryThemes,result)

#		else:
#			self.redirect(users.create_login_url(self.request.uri))
#	def post(self):
		#question=self.request.get('questions')

		#self.redirect("/answer?question=%s" %question)



class AnswerHandler(session_module.BaseSessionHandler):

	def write_form (self, question="", firstopt="", secondopt="", thirdopt="", firstopt_error="", secondopt_error="", thirdopt_error=""):
		
		tem_values = {"question" : question,"firstopt" : firstopt, "secondopt" : secondopt,"thirdopt" : thirdopt,"firstopt_error" : firstopt_error,	"secondopt_error" : secondopt_error,"thirdopt_error" : thirdopt_error}

		template = JINJA_ENVIRONMENT.get_template('answer.html')
		self.response.write(template.render(tem_values))

	def get(self):
		def escape_html(s):
			return cgi.escape(s, quote=True)
		question=""
		questionQuery= Question.query(Question.question=="Which is the first president of the USA?")#self.request.get('question'))
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
				self.response.out.write (self.request.get('opt'))



class ComprobarEmail(webapp2.RequestHandler):
	def post(self):
		user = Visitante.query(Visitante.email==self.request.get('email')).count()
		if user==0 and self.request.get('email')!="":
			self.response.out.write("<span style='color:green'>Email -> " +self.request.get('email')+ " <- Correcto</span>")
		else:
			self.response.out.write("<span style='color:red'>Este email ya esta registrado o no es valido</span>")


class WelcomeHandler(session_module.BaseSessionHandler):
	def get(self):
		greeting = ('Saludos, %s <p><a href="%s">Sign out </a><br>' %(self.request.get('username'), users.create_logout_url('/')))
		self.response.out.write('<html><body><h1>%s</h1></body></html>' %greeting) 

class PrincipalHandler(session_module.BaseSessionHandler):
	def get(self):
		user = users.get_current_user()
		if user:
			greeting = ('Hi, %s <p><a href="%s">Finish session </a><br>' %(user.nickname(), users.create_logout_url('/')))
			self.response.out.write(answerquestion_form)
			self.response.out.write('<h1>%s</h1>' %greeting) 
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
		self.response.out.write ("<h2>Goodbye!</h2>")
		self.response.out.write("<p><h2><a href='/'> Go back Home ...</a></h2>")

class MainHandler(session_module.BaseSessionHandler):
	def write_form (self):
		self.response.out.write(main_form)
	def get(self):
		self.write_form()

class CheckAnswerHandler(session_module.BaseSessionHandler):
	def post(self):
		givenAnswer=self.request.get('ans')
		question=self.request.get('question')
		questionQuery= Question.query(Question.question==question)
		if questionQuery.count()==1:
			question=questionQuery.get()
			if question.correct==givenAnswer:
				self.response.out.write ("<h2>Correct!!!</h2>   <button onClick='fillThemes()''>Next Question</button>" )
			else: 
				self.response.out.write ("Sorry, try again...")
		else:
			self.response.out.write ("no question")

from manage import *
from login import *
from signup import *
from insert import *

class BootHandler(session_module.BaseSessionHandler):
	def write_form (self, question="", firstopt="", secondopt="", thirdopt="", firstopt_error="", secondopt_error="", thirdopt_error=""):
			tem_values = {"question" : question,"firstopt" : firstopt, "secondopt" : secondopt,"thirdopt" : thirdopt,"firstopt_error" : firstopt_error,	"secondopt_error" : secondopt_error,"thirdopt_error" : thirdopt_error}
			template = JINJA_ENVIRONMENT.get_template('index.html')
			self.response.write(template.render(tem_values))
	def get(self):
		self.write_form()

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/bootstrap', BootHandler),
    ('/manage', ManageHandler),
    ('/main', PrincipalHandler),
    ('/prueba', PlayHandler),
    ('/signup', SignupHandler),
    ('/login', LoginHandler),
    ('/cerrarsesion', CerrarSesionHandler),
    ('/welcome',WelcomeHandler),
    ('/insert', InsertHandler),
    ('/answer', AnswerHandler),
    ('/checkanswer', CheckAnswerHandler),
    ('/result',ResultHandler),
    ('/fillanswer', FillAnswerHandler),
    ('/filltheme', FillThemeHandler),
    ('/comprobar',ComprobarEmail)
], config=session_module.myconfig_dict, debug=True)