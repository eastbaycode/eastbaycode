import json
import time
from flask import render_template, flash, request, redirect, url_for, session, jsonify
from flask_login import login_required, login_user, current_user, logout_user
from flask_debugtoolbar import DebugToolbarExtension
from app import app
from app import db
from app.models import Problems, Users, TestCases, Examples, Courses, Assignments
from app.models import Submissions
from app.forms import QuestionForm, TestCaseForm, ExamplesForm, CourseForm, AssignmentForm
from app.login_google import get_google_auth
from config import Config
from requests.exceptions import HTTPError
from app.msgqueue import push_msg, get_result
from flask_socketio import send, emit
from app import socketio

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/courses')
@login_required
def show_courses():
    # show the courses that User takes
    # get the course list from database based on user id
    user = Users.query.filter_by(id=current_user._get_current_object().id).first()
    course = user.courses.all()
    created_courses = user.professor.all()

    return  render_template("course_view.html", course=course,
                            created_courses=created_courses)

@app.route("/course/<int:course_id>")
@login_required
def show_assignments(course_id):
    course = Courses.query.filter_by(id=course_id).first()
    assignments = course.assignments.all()

    return render_template("assignments.html", course=course, assignments=assignments)

@app.route('/problems')
@login_required
def show_problems():
    user = Users.query.filter_by(id=current_user._get_current_object().id).first()
    problems = user.problems.all()
    return render_template('show_problems.html', problems=problems)

@app.route('/create/course', methods=['GET', 'POST'])
@login_required
def create_course():
    form = CourseForm()
    if form.validate_on_submit():
        course = Courses(title=form.title.data,
                         startdate=form.startdate.data,
                         enddate = form.enddate.data,
                         semester=form.semester.data,
                         professor_id=current_user._get_current_object().id)
        db.session.add(course)
        db.session.commit()
        flash("Your course is created!")
        return redirect(url_for('show_courses'))
    return render_template('create_course.html', form=form)

@app.route('/create', methods=['GET', 'POST'])
@login_required
# create question and testcases for this problem
def create_question():
    form = QuestionForm()
    tc_form = TestCaseForm()
    ex_form = ExamplesForm()
#   if current_user.can(Permission.WRITE_ARTICLES) and \
    if form.validate_on_submit():
        problem = Problems(title=form.title.data, question=form.question.data,
                            version=form.version.data, solution=form.solution.data,
                            creator=current_user._get_current_object())
        for t in form.testcases.data:
            testcase = TestCases(input=t['input'])
            problem.testcases.append(testcase)
        for e in form.examples.data:
            example = Examples(input=e['input'], output=e['output'])
            problem.examples.append(example)
        db.session.add(problem)
        db.session.commit()
        flash('Your question is created!')
        return 'Your question is created!'
    return render_template('create_prob.html', form=form)

@app.route('/create_assignment/<int:course_id>', methods=['GET', 'POST'])
@login_required
def create_assignment(course_id):
    # choose course from drop down list
    # choose problems from drop downlist
    problems = Problems.query.filter_by(creator_id=current_user._get_current_object().id).all(  )
    form = AssignmentForm()
    form.problem.choices = problems
    if form.validate_on_submit():
        # write the select problem into Assignments
        assignment = Assignments(course_id=course_id,
                                problems=form.problem.data,
                                startdate=form.startdate.data,
                                enddate=form.enddate.data)
        db.session.add(assignment)
        db.session.commit()
        flash('Your assignment is created!')
        return redirect(url_for('index'))
    return render_template('create_assignment.html', form=form)

@app.route('/profile')
@login_required
def profile():
    # show avatar, name, email address
    user = Users.query.filter_by(id=current_user._get_current_object().id).first()
    return render_template('profile.html', user=user)

@app.route('/login')
def login():
    # if current_user.is_authenticated:
    #     return redirect(url_for('index'))
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

@app.route("/problem/<int:id>", methods= ['GET', 'POST'])
def displayTextEditor(id):
    code = ''
    result = ''
    problem = Problems.query.filter_by(id=id).first()
    testcase = problem.testcases.all()

    # convert the elements in input into input_list
    input_list = []
    for t in testcase:
        input_list.append(t.input)
    print(input_list)

    if request.method == 'POST':
        code = request.form['code']
        if code:
            submission = Submissions(student_id=current_user._get_current_object().id,
                                    problem_id=id, submission=code)
            db.session.add(submission)
            db.session.commit()


        # input_list=["bhavik"]
        #
        # # result = runcode(code, inputs) - just for subprocess.run
        # # push msg to redis queue
        # msg = json.dumps({"code": code, "inputs": input_list,
        #                   "prototype": "def sayHello(s)","handle": 38})
        # push_msg(qname="work", msg=msg)
        # time.sleep(10)
        # result = get_result(qname="result")
        # # inputs = problem.testcases.all()
        # # return redirect(url_for(displayTextEditor))
    return render_template("text_editor.html", code=code, inputs=testcase,
                            problem=problem, result = result)

@app.route("/test/<int:id>")
def testAjax(id):
    code = ''
    result = ''
    problem = Problems.query.filter_by(id=id).first()
    testcase = problem.testcases.all()
    input_list = []
    for t in testcase:
        input_list.append(t.input)
    print(input_list)
    return render_template("submission.html", code=code, inputs=testcase,
                            problem=problem, result = result)

@app.route("/runner_done", methods=['POST'])
def runner_done():
    data = request.form
    sid = data['sid']
    json = {}
    socketio.emit('answer', json, room=sid)
    print("The runner is done.")
    return "thanks"


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@socketio.on('connect')
def socket_connect():
    print("connection ", request.sid)
    session['websocket'] = request.sid

@socketio.on('disconnect')
def socket_disconnect():
    pass


@socketio.on('aaa')
def handle_aaa(json):
    print("received aaaa: ", str(json))
    emit('aaa_response', {'data': 'Server'})

@socketio.on('message')
def handle_message(message):
    print('received message: ' + message)

@socketio.on('my event')
def handle_my_custom_event(json):
    emit('answer', json)

@socketio.on('submit_code')
def handle_my_custom_event(json):
    rq_job = app.task_queue.enqueue('app.tasks.example', request.sid)
