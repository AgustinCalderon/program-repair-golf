from .file_utils import *

class PythonSourceCode:
  
  def __init__(self, **args):
    path = args.get('path')
    if path is None: #only the code and the filename will be stored
      self.content = args['code']
      self.name = args['name']
    else: #if we have path we can obtain all the other attributes
      self.path = path
      self.content = read_file(path, 'rb')
      self.name = get_filename(path)

  def move_code(self, path):
    #Save code repair
    path_code_repair = path + self.name 
    save_file(path_code_repair, 'wb', self.content)

    self.path = path_code_repair

  def update(self, content, name):
    if content != None: self.content = content
    if name != None: self.name = name

  def get_content(self):
    return self.content.decode()