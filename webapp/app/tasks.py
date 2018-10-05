import time
from rq import get_current_job
from app.models import Task
import requests

# from app import app
# app.app_context().push()



def example(sid):
    #job = get_current_job()
    print('Staring task: ', sid)
    for i in range(5):
        print(i)
        time.sleep(1)

    #job.meta['result'] = "finished"
    #job.save_meta()

    url = 'https://eastbaycode_webapp_1:5000/runner_done'
    data = {'sid': sid}
    r = requests.post(url = url, data = data, verify=False)
    print('Task completed: ', r)


def _set_task_progress(progress):
    job = get_current_job()
    if job:
        job.meta['progress'] = progress
        job.save_meta()
        task = Task.query.get(job.get_id())
        task.user.add_notification('task_progress', {'task_id': job.get_id(),
                                                     'progress': progress})
        if progress >= 100:
            task.complete = True
        db.session.commit()
