import re
from flask.helpers import make_response
from app.java import *
from app.java.controller import *
from . import java
from app import db
import os
from flask import Flask, flash, request, redirect, url_for, jsonify, json
from werkzeug.utils import secure_filename
from json import loads
from types import TracebackType
import subprocess
import os.path
from subprocess import STDOUT, PIPE
from os import remove
from os import path


UPLOAD_FOLDER = './public/challenges/'
PATHLIBRERIA = 'app/java/lib/junit-4.13.2.jar:public/challenges'
PATHEXECUTE = 'org.junit.runner.JUnitCore'
ALLOWED_EXTENSIONS = {'java'}
EJECUTARFILE= 'app/java/lib/hamcrest-all-1.3.jar:app/java/lib/junit-4.13.2.jar:public/challenges/'

@java.route('/prueba')
def login():
    return { 'result': 'funciona' }


@java.route('/java-challenges',methods=['GET'])
def ViewAllChallenges():
    return controller.list_challenges_java()
    
@java.route('/java-challenges/<int:id>',methods=['GET'])
def View_Challenges(id):
    return controller.challenges_id_java(id)
    

@java.route('/java-challenges/<int:id>', methods=['PUT'])
def UpdateChallenge(id):
    return controller.challenge_upd_java(id)


@java.route('/java-challenges', methods=['POST'])
def create_challenge():
   return controller.add_challenge_java()



@java.route('/java-challenges/<int:id>/repair', methods=['POST'])
def repair_challenge(id):
    file = request.files['source_code_file']
    challenge = Challenge_java.query.filter_by(id = id).first()
   # if challenge is not None:
        #si file es sintacticamente correcta, entonces compara file con los test suite
        #es decir file con challenge['tests_code']
        #si pasa todos los test
        #calcula puntuacion
        #score_curr = calculo_score()
        #if score_curr < challenge.score:
         #   challenge.score = score_curr
    #        db.session.add(challenge)
     #       db.session.commit()
    #else:
     #   return make_response(jsonify("Error al seleccionar archivo"))

"""
# given an path file, if not compile class java remove class and return exception
def class_java_compile(path_file_java):
    try:
        compile_java(path_file_java)
    except Exception:
        delete_path(path_file_java)
        return False
    return True

# given an path file test and path file class
# if not compile file test remove the files and return exception
def file_compile(path_test_java, path_file_java):
    try:
        compile_java_test(path_test_java)
    except Exception:
        delete_path(path_file_java)
        delete_path(path_test_java)
        return False
    return True

# if pass all test not save file and remove all files in public/challenges
def execute_test(name, code_file_name):
    rm_java = UPLOAD_FOLDER + name + '.java'
    rm_class = UPLOAD_FOLDER + name + '.class'
    rm_java_class = UPLOAD_FOLDER + code_file_name + '.java'
    rm_java_java = UPLOAD_FOLDER + code_file_name + '.class'
    if execute_java_test(name):
        # remove all files
        delete_path(rm_java)
        delete_path(rm_class)
        # remove class java
        delete_path(rm_java_class)
        delete_path(rm_java_java)
        return True
    else:
        delete_path(rm_class)
        delete_path(rm_java_java)
    return False

############## Service compilation ###################
def compile_java(java_file):
    subprocess.check_call(['javac', java_file])

def execute_java(java_file):
    cmd=['java', java_file]
    proc=subprocess.Popen(cmd, stdout = PIPE, stderr = STDOUT)
    input = subprocess.Popen(cmd, stdin = PIPE)
    print(proc.stdout.read())

def compile_java_test(java_file):
    subprocess.check_call(['javac', '-cp', PATHLIBRERIA, java_file])
    
# return True if pass all test alse false
def execute_java_test(java_file):
    cmd=['java', '-cp', EJECUTARFILE , PATHEXECUTE, java_file]
    proc=subprocess.Popen(cmd, stdout = PIPE, stderr = STDOUT)
    child = subprocess.Popen(cmd, stdin = PIPE)
    streamdata = child.communicate()[0]
    rc = child.returncode
    if rc == 0:
        return True
    else:
        return False
"""
    

