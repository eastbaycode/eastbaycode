from app import app
from app import db
from app.models import Users, Problems, Examples, TestCases, Courses, Assignments, Task
from app import socketio

# create shell context that adds database instance and models to the shell
@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Users': Users, 'Problems': Problems,
            'Examples': Examples, 'Task': Task}


if __name__ == '__main__':
    socketio.run(app, debug=True, ssl_context=('./ssl.crt', './ssl.key'),
        host='0.0.0.0')
