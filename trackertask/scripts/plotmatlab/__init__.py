import subprocess
from celery import Task
from celery import current_task
from trackertask.scripts import add_script
from trackertask.scripts import Script

class PlotMatLab(Task):
    """Perform something in a Matlab executable"""

    def run(self, start, end, id, username, password):
        current_task.update_state(state='PROGRESS')
        args = ['/bin/sh',
                # TODO make configurable
                '/tmp/sw/run_stefan.sh',
                # TODO make configurable
                '/home/stefanv/MATLAB/MATLAB_Compiler_Runtime/v717',
                username,
                password,
                ]
        popen = subprocess.Popen(args,
                                      stderr=subprocess.PIPE,
                                      stdout=subprocess.PIPE)
        (stdout, stderr) = popen.communicate()
        return {'returncode': popen.returncode,
                'stderr': stderr,
                'stdout': stdout,
                }

add_script(Script(id='plotMatlab',
                  name='Plot overview using Matlab',
                  description='Plots tracker measurements over time',
                  authors='Willem Bouten',
                  task=PlotMatLab,
                  ))
