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
from __future__ import division

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
import logging
class FillThemeHandler(session_module.BaseSessionHandler):
	def write_form (self, question="", firstopt="", secondopt="", thirdopt="", firstopt_error="", secondopt_error="", thirdopt_error=""):
			tem_values = {"question" : question,"firstopt" : firstopt, "secondopt" : secondopt,"thirdopt" : thirdopt,"firstopt_error" : firstopt_error,	"secondopt_error" : secondopt_error,"thirdopt_error" : thirdopt_error}
			template = JINJA_ENVIRONMENT.get_template('fillanswer.html')
			self.response.write(template.render(tem_values))
	def post(self):
		def escape_html(s):
			return cgi.escape(s, quote=True)
		#self.response.out.write("<span style='color:red'>Este es valido</span>")
		#questionQueryThemes = ndb.gql("SELECT question FROM Question WHERE theme = :1", self.request.get('theme'))
		logging.info("hello")
		questionQuery= Question.query(Question.theme==self.request.get('theme')) 
		lastQuestion=self.session.get('currentQuestion')
		firstTime=False
		if not lastQuestion:
			lastQuestion=""
		if not lastQuestion or lastQuestion=="":
			firstTime=True
		logging.info("lastQuestion: %s"  %lastQuestion)
		#question=""
		question_s=""
		foundLast=False
		end=False
		themeFinished=False
		clock=0
		n = questionQuery.count()

		if n==1 and  lastQuestion!="":
			end =True
		if n>0:
			count=0
			for  q in questionQuery:
				logging.info("count: %s" %count)
				count=count+1

				if firstTime:
					question_s=q.question
					break

				if foundLast:															
					logging.info("415")
					logging.info("dentro del if foundLast TRUE %s" %question_s)
					question_s=q.question
					#last=False
					break
				if(q.question==lastQuestion):										
					logging.info("421")
					foundLast=True
					logging.info("q.question==lastQuestion %s" %q.question)
					question_s=q.question
					if count==n and n!=1:
						end=True
			if not foundLast:
				aux=questionQuery.get()
				question_s=aux.question
			if end:
				self.session['currentQuestion']=""

			questionQuery2= Question.query(Question.question==question_s) 
			if questionQuery2.count()==1 and not end :								
				logging.info("432")
				question=questionQuery2.get()
				firstopt_error = ""
				secondopt_error = "" 
				thirdopt_error = ""
				sani_question = escape_html(question.question)
				sani_firstopt = escape_html(question.first)
				sani_secondopt = escape_html(question.second)
				sani_thirdopt = escape_html(question.third)
				self.write_form(sani_question, sani_firstopt, sani_secondopt, sani_thirdopt, firstopt_error, secondopt_error, thirdopt_error)
			else:
				logging.info("End, question_s: %s"  %question_s)
				if self.session.get('username'):
					email=self.session.get('username')
					#url="<a href='/manage'>Go to Main Page</a>"
					url="<a href='/manage'><button>Go to Main Page</button></a>"
				else:
					email=self.session.get('nickname')
					#url="<a href='/logout'>End Session</a>"
					url="<a href='/logout'><button>End Session</button></a>"
			#	fList=FinishedThemes.query(FinishedThemes.theme==self.request.get('theme'), FinishedThemes.email==email)
			#	if fList.count()>0:
			#		f=fList.get()
			#	else: 
				f=FinishedThemes()
				f.theme=self.request.get('theme')
				f.email=email
				f.corrects=self.session.get('correctAnswer')
				f.incorrects=self.session.get('incorrectAnswer')
				f.put()


				listaPreguntasTheme= Question.query(Question.theme==self.request.get('theme'))
				finQlist= FinishedThemes.query(FinishedThemes.email==email,FinishedThemes.theme==self.request.get('theme'))
				count=0
				for finQ in finQlist:
					count=count+finQ.corrects
				count=count+self.session.get('correctAnswer')
				totalAnswered=(finQlist.count() * listaPreguntasTheme.count()) +listaPreguntasTheme.count()
				if totalAnswered>0:
					percentage=count/totalAnswered
#				else:
#					percentage=count/(self.session.get('correctAnswer')+self.session.get('incorrectAnswer'))
#					logging.info("porcentaje 0")
					percentTwoDecimals = float("{0:.2f}".format(percentage))
				else:
					percentTwoDecimals=0

				percentTwoDecimals=percentTwoDecimals*100

				finQGlobalList= FinishedThemes.query(FinishedThemes.email==email)
				PreguntasRespondidasList= VisiQuest.query(VisiQuest.email==email)
				countGlobal=0
				countIncorGlobal=0
				for ft in finQGlobalList:
					countGlobal=countGlobal+ft.corrects
					countIncorGlobal=countIncorGlobal+ft.incorrects
				countGlobal=countGlobal+self.session.get('correctAnswer')
				countIncorGlobal=countIncorGlobal+self.session.get('incorrectAnswer')
				logging.info("countGlobal %s" %countGlobal)
				totalAnsweredGlobal=countGlobal+countIncorGlobal
				if totalAnsweredGlobal>0:
					percentageGlobal=countGlobal/totalAnsweredGlobal 
				else:
					percentageGlobal=self.session.get('correctAnswer')/(self.session.get('correctAnswer')+self.session.get('incorrectAnswer'))
					logging.info("porcentaje global 0")
				logging.info("totalAnsweredGlobal %s" %totalAnsweredGlobal)
				percentTwoDecimalsGlobal = float("{0:.2f}".format(percentageGlobal))
				percentTwoDecimalsGlobal=percentTwoDecimalsGlobal*100

				self.response.out.write("<h3>You answered all the questions of this theme!</h3><h2>Quiz Score: "+ str(self.session.get('correctAnswer'))+"/"+str(listaPreguntasTheme.count()) +"</h2> <h2>"+self.request.get('theme')+" Right Guess Percentage: "+str(percentTwoDecimals)+"%</h2><h2>Global Right Guess Percentage: "+str(percentTwoDecimalsGlobal)+"%</h2><h3>"+url+" or Select another theme!!</h3>" )
				self.session['correctAnswer']=0
				self.session['incorrectAnswer']=0
		else:
			self.response.out.write ("damn no questions bruh")

class PlayHandler(session_module.BaseSessionHandler):
	def write_form (self, mylist,mylistThemes,result,nick,logoutlink,guest):
		tem_values = {"mylist" : mylist,"mylistThemes" : mylistThemes, "result":result,"nick":nick,"logoutlink":logoutlink,"guest":guest}
		template = JINJA_ENVIRONMENT.get_template('listanswer.html')
		self.response.write(template.render(tem_values))
	def get(self):
			logged_username=self.session.get('username')
			logging.info("%s" %logged_username)
#		if user:
#			greeting = ('Logged as: %s <a href="%s">Finish session </a><br>' %(user.nickname(), users.create_logout_url('/')))
			result=self.request.get('result')
			nick=self.request.get('nick')
			if (self.request.get('nick')):
			#	user = users.User(nick)
				user_name=nick
				guest="Nickname:"
				self.session['nickname'] = user_name
			#	logoutlink=users.create_logout_url('/bootstrap')
			elif (self.session.get('username')): #and self.session.get('username')
				user_name=logged_username
				logging.info("en el elif !!!%s" %user_name)
				guest="Username:"
			#	logoutlink="/logout"
			else:
				self.redirect('/')
				return
			questionQuery= Question.query()
			questionQueryThemes = ndb.gql("SELECT DISTINCT theme FROM Question ") #+ "WHERE theme = :1", self.request.get('theme'))
			self.write_form(questionQuery,questionQueryThemes,result,user_name,"/logout",guest)

class ShowQuestionsHandler(session_module.BaseSessionHandler):
	def write_form (self, mylist,username):
		tem_values = {"mylist" : mylist,"username":username}
		template = JINJA_ENVIRONMENT.get_template('showQuestions.html')
		self.response.write(template.render(tem_values))
	def get(self):
			if (self.session.get('username')): 
				logged_username=self.session.get('username')
				questionQuery= Question.query()
				self.write_form(questionQuery,logged_username)
			else:
				self.redirect('/')
				return

class ComprobarEmail(webapp2.RequestHandler):
	def post(self):
		EMAIL_RE = re.compile(r"^[\S]+@[\S]+\.[\S]+$")
		emailOK=EMAIL_RE.match(self.request.get('email'))
		user = Visitante.query(Visitante.email==self.request.get('email')).count()
		if user==0 and self.request.get('email')!="" and emailOK:
			self.response.out.write("<span style='color:green'>Email -> " +self.request.get('email')+ " <- Correcto</span>")
		else:
			self.response.out.write("<span style='color:red'>Este email ya esta registrado o no es valido</span>")

class AddedThemeHandler(session_module.BaseSessionHandler):
	def post(self):
		if self.session.get('added')==True:
			self.response.out.write("<h2>Question Added</h2>")
			self.session['added']=False
		else:
			self.response.out.write("<h2>Try again</h2>")

class LogoutSesionHandler(session_module.BaseSessionHandler):
	def get(self):
		for k in self.session.keys():
			del self.session[k]
			self.response.out.write ("Session ended ...")
		self.redirect('/')
		self.response.out.write ("<h2>Goodbye!</h2>")
		self.response.out.write("<p><h2><a href='/'> Go back Home ...</a></h2>")

class CheckAnswerHandler(session_module.BaseSessionHandler):
	def post(self):
		givenAnswer=self.request.get('ans')
		question=self.request.get('question')
		questionQuery= Question.query(Question.question==question)
		visiqList= VisiQuest.query(VisiQuest.question==question)
		if questionQuery.count()==1:
			question=questionQuery.get()
			#user=users.get_current_user()
			if self.session.get('correctAnswer'):
				aux=self.session['correctAnswer']
			else:
				self.session['correctAnswer']=0
				aux=self.session.get('correctAnswer')

			if self.session.get('incorrectAnswer'):
				incor=self.session['incorrectAnswer']
			else:
				self.session['incorrectAnswer']=0
				incor=self.session.get('incorrectAnswer')

			if self.session.get('username'):
				if visiqList.count()>0:
					vq=visiqList.get()
				else: 
					vq=VisiQuest()
				vq.question=question.question
				vq.email=self.session.get('username')
				if question.correct==givenAnswer:
					vq.correct=True
					self.session['correctAnswer']=aux+1
					self.response.out.write ("<h2>Correct!!!</h2>  <h3>Correct Answers:"+str(self.session.get('correctAnswer'))+"</h3> <button onClick='fillThemes()''>Next Question</button> <div id='theQ'  style='display: none;'>"+self.request.get('question')+"</div>" )
				else:
					vq.correct=False
					self.session['incorrectAnswer']=incor+1
					self.response.out.write ("<h2>Incorrect...</h2> <h3>Correct Answers: %s</h3><button onClick='fillThemes()''>Next Question</button>" %self.session.get('correctAnswer'))
				vq.put()
			elif self.session.get('nickname'):
				if question.correct==givenAnswer:
					self.session['correctAnswer']=aux+1
					self.response.out.write ("<h2>Correct!!!</h2> <h3>Correct Answers: %s</h3><button onClick='fillThemes()''>Next Question</button>" %self.session.get('correctAnswer'))
				else: 
					self.session['incorrectAnswer']=incor+1
					self.response.out.write ("<h2>Incorrect...</h2> <h3>Correct Answers: %s</h3><button onClick='fillThemes()''>Next Question</button>" %self.session.get('correctAnswer'))
			else:
				self.response.out.write ("no username nor nickname")
			self.session['currentQuestion']=question.question
		else:
			self.response.out.write ("no such question")

from manage import *
from login import *
from signup import *
from insert import *

class VisiQuest(ndb.Model):
	email=ndb.StringProperty()
	question=ndb.StringProperty()
	correct=ndb.BooleanProperty()
	creado=ndb.DateTimeProperty(auto_now_add=True)

class FinishedThemes(ndb.Model):
	email=ndb.StringProperty()
	theme=ndb.StringProperty()
	corrects=ndb.IntegerProperty()
	incorrects=ndb.IntegerProperty()
	creado=ndb.DateTimeProperty(auto_now_add=True)

class RootHandler(session_module.BaseSessionHandler):
	def write_form (self, question="", firstopt="", secondopt="", thirdopt="", firstopt_error="", secondopt_error="", thirdopt_error=""):
			tem_values = {"question" : question,"firstopt" : firstopt, "secondopt" : secondopt,"thirdopt" : thirdopt,"firstopt_error" : firstopt_error,	"secondopt_error" : secondopt_error,"thirdopt_error" : thirdopt_error}
			template = JINJA_ENVIRONMENT.get_template('index.html')
			self.response.write(template.render(tem_values))
	def get(self):
		self.write_form()

app = webapp2.WSGIApplication([
    ('/', RootHandler),
    ('/signup', SignupHandler),
    ('/login', LoginHandler),
    ('/play', PlayHandler),
    ('/logout', LogoutSesionHandler),

    ('/insert', InsertHandler),
    ('/manage', ManageHandler),
    ('/checkanswer', CheckAnswerHandler),
    ('/fillanswer', FillAnswerHandler),
    ('/filltheme', FillThemeHandler),
    ('/showQuestions', ShowQuestionsHandler),

    ('/checkAdd', AddedThemeHandler),
    ('/comprobar',ComprobarEmail)
], config=session_module.myconfig_dict, debug=True)