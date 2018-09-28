import time
from rq import get_current_job


def example(seconds):
    job = get_current_job()
    print('Staring task')
    for i in range(seconds):
        print(i)
        time.sleep(1)
    job.meta['result'] = "finished"
    job.save_meta()
    print('Task completed')

