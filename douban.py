# from flask import Flask,jsonify,url_for,redirect,render_template
# import json
# import os
#
# app = Flask(__name__)
#
# PROJECT_DIR = os.path.dirname(__file__)
#
# # @app.route('/')
# # def index():
# #     print(url_for('my_list'))
# #     print(url_for('article',id='111'))
# #     return render_template('index.html')
#
# @app.route('/books')
# def books():
#     books = [
#         {
#             'name': u'西游记',
#             'author': u'吴承恩',
#             'price': 60
#         },
#         {
#             'name': u'红楼梦',
#             'author': u'曹雪芹',
#             'price': 70
#         },
#         {
#             'name': u'三国演义',
#             'author': u'罗贯中',
#             'price': 80
#         },
#         {
#             'name': u'水浒传',
#             'author': u'施耐庵',
#             'price': 90
#         }
#     ]
#     return render_template('index.html',books=books)
#
# @app.route('/list/')
# def my_list():
#     return 'list'
#
# @app.route('/article/<id>/')
# def article(id):
#     return u'请求的参数是：%s'% id
#
# @app.route('/login')
# def login():
#     return u'this is login web'
#
# @app.route('/question/<is_login>/')
# def question(is_login):
#     if is_login == '1':
#         return u'this is question web'
#     else:
#         return redirect(url_for('login'))
#
# if __name__ == '__main__':
#     app.run(debug=True)

from flask import Flask, render_template, request, redirect, url_for, session
import config
from models import User, Question,Answer
from exts import db
from decorators import login_required

app = Flask(__name__)
app.config.from_object(config)
db.init_app(app)


@app.route('/')
def index():
    context = {
        'questions':Question.query.order_by('-create_time').all()
    }
    return render_template('index.html',**context)


@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        telephone = request.form.get("telephone")
        password = request.form.get("password")

        user = User.query.filter(User.telephone == telephone).first()
        password = User.query.filter(User.password == password).first()
        if user:
            if password:
                session['user_id'] = user.id
                # 如果想在31天内都不需要重新登录
                session.permanent = True
                return redirect(url_for('index'))
            else:
                return u'密码错误，请重新输入！'
        else:
            return u'手机号码错误或未注册，请重新输入或注册！'


@app.route('/register/', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    else:
        telephone = request.form.get("telephone")
        username = request.form.get("username")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")

        # 手机号码验证，如果被注册了，就不能再注册了
        user = User.query.filter(User.telephone == telephone).first()
        if user:
            return u'该手机号码已经被注册，请更换手机号码！'
        else:
            # password1==password2
            if password1 != password2:
                return u'两次输入的密码不一致，请重新输入！'
            else:
                user = User(telephone=telephone, username=username, password=password2)
                db.session.add(user)
                db.session.commit()
                # 如果注册成功，则跳转到登录页面
                return redirect(url_for('login'))


@app.context_processor
def my_context_processor():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.filter(User.id == user_id).first()
        if user:
            return {'user': user}
    return {}


@app.route('/logout/')
def logout():
    # 因为判断是否登录的准则是session中是否存在user_id
    # 那么相应的，注销只要把session中的user_id删除即可
    session.pop('user_id')
    # del session['user_id']
    # session.clear()
    return redirect(url_for('login'))


@app.route('/question/', methods=['GET', 'POST'])
@login_required
def question():
    if request.method == 'GET':
        return render_template('question.html')
    else:
        title = request.form.get('title')
        content = request.form.get('content')
        question = Question(title=title, content=content)
        user_id = session.get('user_id')
        user = User.query.filter(User.id == user_id).first()
        question.author = user
        db.session.add(question)
        db.session.commit()
        return redirect(url_for('index'))

@app.route('/detail/<question_id>/')
def detail(question_id):
    question_model = Question.query.filter(Question.id == question_id).first()
    return render_template('detail.html',question_model=question_model)

@app.route('/add_answer',methods=['POST'])
@login_required
def add_answer():
    content = request.form.get('add_answer')
    question_id = request.form.get('question_id')
    answer = Answer(content=content)
    user_id = session['user_id']
    user = User.query.filter(User.id == user_id).first()
    answer.author = user
    question = Question.query.filter(Question.id == question_id).first()
    answer.question = question
    db.session.add(answer)
    db.session.commit()
    return redirect(url_for('detail',question_id = question_id))

if __name__ == '__main__':
    app.run()
