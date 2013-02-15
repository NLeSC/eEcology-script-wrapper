class Script(object):
    def __init__(self, id, name, description, authors, task):
        self.id = id
        self.name = name
        self.description = description
        self.authors = authors
        self.task = task
        self.args = {
                     # TODO get db creds from *.ini file
                     'username': 'me',
                     'password': 'pw'
                     }

scripts = {}

def add_script(script):
    scripts[script.id] = script

def find_scripts():
    pass
