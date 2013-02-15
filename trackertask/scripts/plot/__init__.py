import time
from celery import Task
from celery import current_task
from trackertask.scripts import add_script
from trackertask.scripts import Script

class Plot(Task):
    """Perform a simple python task"""
    def run(self, start, end, id, username, password):
        for i in xrange(int(end)):
            current_task.update_state(state='PROGRESS',
                meta={'current': i, 'total': end})
            time.sleep(float(start))
        return 'fancy plot of {} from {} to {}'.format(id, start, end)

add_script(Script(id='plot',
                  name='Plot overview',
                  description='Plots tracker measurements over time',
                  authors='Willem Bouten',
                  task=Plot,
                  ))
