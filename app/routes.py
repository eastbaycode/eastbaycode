import json
import time
from flask import render_template, flash, request, redirect, url_for, session
from flask_login import login_required, login_user, current_user
from flask_debugtoolbar import DebugToolbarExtension
from app import app
from app import db
from app.models import Problems, Users
from app.forms import QuestionForm
from app.login_google import get_google_auth
from config import Config
from requests.exceptions import HTTPError
from app.msgqueue import push_msg, get_result

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/create', methods=['GET', 'POST'])
def create_question():
    form = QuestionForm()
#   if current_user.can(Permission.WRITE_ARTICLES) and \
    if form.validate_on_submit():
        problem = Problems(title=form.title.data, question=form.question.data,
                            version=form.version.data, solution=form.solution.data,
                            creator=current_user._get_current_object())
        db.session.add(problem)
        db.session.commit()
        flash('Your question is created!')
        return redirect(url_for('create_question'))
    return render_template('create_prob.html', form=form)

@app.route('/login')
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    google = get_google_auth()
    auth_url, state = google.authorization_url(Config.AUTH_URI, access_type='offline')
    session['oauth_state'] = state
    return render_template('login.html', auth_url=auth_url)

@app.route('/gCallback')
def callback():
    # Redirect user to home page if already logged in.
    if current_user is not None and current_user.is_authenticated:
        return redirect(url_for('index'))
    if 'error' in request.args:
        if request.args.get('error') == 'access_denied':
            return 'You denied access.'
        return 'Error encountered.'
    if 'code' not in request.args and 'state' not in request.args:
        return redirect(url_for('login'))
    else:
        # Execution reaches here when user has successfully authenticated our app.
        google = get_google_auth(state=session['oauth_state'])
        try:
            token = google.fetch_token(Config.TOKEN_URI, client_secret=Config.CLIENT_SECRET,
                                        authorization_response=request.url)
        except HTTPError:
            return 'HTTPError occurred.'
        google = get_google_auth(token=token)
        resp = google.get(Config.USER_INFO)
        if resp.status_code == 200:
            user_data = resp.json()
            email = user_data['email']
            user = Users.query.filter_by(email=email).first()
            if user is None:
                user = Users()
                user.email = email
            user.name = user_data['name']
            user.tokens = json.dumps(token)
            user.avatar = user_data['picture']
            db.session.add(user)
            db.session.commit()
            login_user(user)
            return redirect(url_for('index'))
        return 'Could not fetch your information.'

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route("/problem/<int:id>", methods= ['GET', 'POST'])
def displayTextEditor(id):
    code = ''
    result = ''
    problem = Problems.query.filter_by(id=id).first()

    if request.method == 'POST':
        inputs = TestCases.query(TestCases.input).filter_by(problem=id).all()
        code = request.form['code']
        # result = runcode(code, inputs) - just for subprocess.run
        # push msg to redis queue
        msg = json.dumps({"code": code, "inputs": inputs,
                          "prototype": "def sayHello(s)","handle": 38})
        push_msg(qname="msgQueue", msg=msg)
        time.sleep(10)
        result = get_result(qname="result")

    return render_template("text_editor.html", code=code, result=result,
                            problem=problem)
