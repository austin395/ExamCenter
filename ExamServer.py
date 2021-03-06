import jinja2
import os
import random
import json
from zope.interface import Interface, Attribute, implements
from twisted.web.static import File
from twisted.python.components import registerAdapter
from twisted.web.util import redirectTo
from twisted.internet import reactor
from twisted.web import server
from twisted.web.resource import Resource


class IUser(Interface):
    value = Attribute("A user object which maintains user information.")


class User(object):
    implements(IUser)

    def __init__(self, session):
        self.id = session
        self.username = None
        self.givenname = None
        self.lastname = None
        self.currenttest = None


registerAdapter(User, server.Session, IUser)


class Hello(Resource):

    def __init__(self):
        Resource.__init__(self)
        self.templateLoader = jinja2.FileSystemLoader(searchpath='./templates')
        self.templateEnv = jinja2.Environment(loader=self.templateLoader)
        self.serverRoot = os.getcwd()
        self.Users = {'test.user': 'password',
                      'austin.daniels': 'password'}
        self.user = None

    def getChild(self, name, request):
        return self

    def render_GET(self, request):
        session = request.getSession()
        self.user = IUser(session)
        if request.uri == '/': return self.root_get(request)
        elif request.uri == '/login': return self.login_get(request)
        elif request.uri == '/images/cyber.jpg': return File.render_GET(File('templates/images/cyber.jpg'), request)
        elif request.uri == '/images/Smoky.jpg': return File.render_GET(File('templates/images/Smoky.jpg'), request)
        elif request.uri == '/logout': return self.logout_get(request)
        elif request.uri == '/{0}/home'.format(self.user.username): return self.home_get(request)
        elif request.uri == '/take_test': return self.take_test_get(request)
        elif request.uri == '/Subjects': return self.Subjects_get(request)
        elif request.uri == '/Previous_Scores': return self.Previous_Scores_get(request)
        else: return self.page_not_found(request)

    def render_POST(self, request):
        session = request.getSession()
        self.user = IUser(session)

        if request.uri == '/login': return self.login_post(request)

    # /
    def root_get(self, request):
        print(request)
        # if not logged in redirect to login page
        if self.user.username is None:
            return redirectTo('http://localhost:8000/login', request)
        # else redirect to home page
        else:
            print(self.user.username)
            return redirectTo("http://localhost:8000/{0}/home".format(self.user.username), request)

    # /login
    def login_get(self, request):
        if self.user.username is not None:
            return redirectTo("http://localhost:8000/{0}/home".format(self.user.username), request)
        return str(self.templateEnv.get_template('login.html').render())

    def login_post(self, request):
        print(request)
        if request.args["username"][0] in self.Users:
            if request.args["password"][0] == self.Users[request.args["username"][0]]:
                self.user.username = request.args["username"][0]
                return redirectTo("http://localhost:8000/{0}/home".format(self.user.username), request)
        return redirectTo("http://localhost:8000/login", request)

    # /logout
    def logout_get(self, request):
        request.getSession().expire()
        return redirectTo("http://localhost:8000/login", request)

    # /user/home
    def home_get(self, request):
        return str(self.templateEnv.get_template('home.html').render(user=self.user))

    def Previous_Scores_get(self, request):
        return str(self.templateEnv.get_template('Previous_scores.html').render(user=self.user))

    def Subjects_get(self, request):
        return str(self.templateEnv.get_template('Subjects.html').render(user=self.user))

    def take_test_get(self, request):
        json_data = open('tests/sample.json')
        questions = json.loads(json_data.read())
        json_data.close()
        random.shuffle(questions)
        self.user.currenttest = questions[:5]
        self.user.currentquestion = 0
        return self.render_question()


    def render_question(self):
        question = self.user.currenttest[self.user.currentquestion]['question']
        answers = [self.user.currenttest[self.user.currentquestion]['correct_ans']]
        for wans in self.user.currenttest[self.user.currentquestion]['wrong_ans']:
            answers.append(wans)
            random.shuffle(answers)
        return str(self.templateEnv.get_template('question.html').render(question=question, answers=answers))


    # 404 error
    def page_not_found(self, request):
        return str(self.templateEnv.get_template('404error.html').render())



site = server.Site(Hello())
reactor.listenTCP(8000, site)
reactor.run()
