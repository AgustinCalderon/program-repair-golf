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

# GET 'http://localhost:4000/api/v1/java-challenges'

@java.route('/java-challenges',methods=['GET'])
def ViewAllChallenges():
    return controller.list_challenges_java()
    

# Get Assignment by ID
@java.route('/java-challenges/<int:id>',methods=['GET'])
def View_Challenges(id):
    challenge=Challenge_java.query.filter_by(id=id).first()
    if challenge is None:
        return make_response(jsonify({"challenge": "Not exist this id"}))
    challengeaux=Challenge_java.__repr__(challenge)
    if (challengeaux is None):
        return make_response(jsonify({"challenge":"Not found prueba"}),404)   
    else: 
        #recupero el codigojava del challenge
        nombre_code = challengeaux['code']
        path='public/challenges/' + nombre_code + '.java'
        file = open (path,mode='r',encoding='utf-8')
        filemostrar=file.read()
        file.close()
        challengeaux['code']=filemostrar


        #recupero el codigojava del test
        nombre_test =challengeaux['tests_code']
        path='public/challenges/' + nombre_test + '.java'
        file = open (path,mode='r',encoding='utf-8')
        filemostrar=file.read()
        file.close()
        challengeaux['tests_code']=filemostrar

       # challenge.append(challenge)
           
        return jsonify({"challenge":challengeaux})
        
@java.route('/java-challenges/<int:id>', methods=['PUT'])
def UpdateChallenge(id):
    challenge= Challenge_java.query.filter_by(id=id).first()
    if challenge is None:
        return make_response(jsonify({"challenge":"Not Found!"}),404)
    else:
        challenge_json = loads(request.form.get('challenge'))
        challenge_upd= challenge_json['challenge']
        
        if 'repair_objective' in request.form.get('challenge'):
            repair_objective_upd=challenge_upd['repair_objective']
            challenge.repair_objective=repair_objective_upd
            
        if 'complexity' in request.form.get('challenge'):
            complexity_upd=challenge_upd['complexity']
            challenge.complexity=complexity_upd

        if 'source_code_file_name' in request.form:    
            code_file_upd_name=challenge_upd['source_code_file_name']

        if 'test_suite_file_name' in request.form:
            test_suite_upd_name=challenge_upd['test_suite_file_name']

        if 'source_code_file' in request.files:
            code_file_upd = request.files['source_code_file']
            path_file_java = UPLOAD_FOLDER + code_file_upd.filename
            if class_java_compile(path_file_java):
                challenge.code=os.path.split(code_file_upd.filename)[-1].split('.')[0]
                print(challenge.code)
                upload_file_1(code_file_upd, UPLOAD_FOLDER)
            else:
                return make_response(jsonify("Class java not compile"))

        if 'test_suite_file' in request.files:
            test_suite_upd = request.files['test_suite_file']
            path_test_java = UPLOAD_FOLDER +  test_suite_upd.filename
            if file_compile(path_test_java, path_file_java):
                if execute_test(code_file_upd_name, test_suite_upd_name):
                        return make_response(jsonify("La test suite debe fallar en almenos un caso de test para poder subirlo"))
                else:
                    challenge.tests_code=os.path.split(test_suite_upd.filename)[-1].split('.')[0]
                    upload_file_1(test_suite_upd, UPLOAD_FOLDER)

        
        db.session.commit()
        return jsonify({"challenge":Challenge_java.__repr__(challenge)})


@java.route('/java-challenges', methods=['POST'])
def create_challenge():
    aux = request.form['challenge']
    to_dict = json.loads(aux)
    dict_final = to_dict['challenge']

    if dict_final is not None:
        code_file_name = dict_final['source_code_file_name']
        test_suite_file_name = dict_final['test_suite_file_name']
        objective = dict_final['repair_objective']
        complex = dict_final['complexity']
        challenge = Challenge_java.query.filter_by(code=code_file_name).first()

        if challenge is None:
            # check if the post request has the file part
            file = request.files['source_code_file']
            test_suite = request.files['test_suite_file']
            
            # upload class java and compile
            upload_file_1(file, UPLOAD_FOLDER)
            path_file_java = UPLOAD_FOLDER + file.filename
            if class_java_compile(path_file_java):
                
                # upload test suite java and compile
                upload_file_1(test_suite, UPLOAD_FOLDER)
                path_test_java = UPLOAD_FOLDER + test_suite.filename
                #file_compile(path_test_java, path_file_java)
            
                # excute test suite java
                # excute_java_test return true if pass all test
                if file_compile(path_test_java, path_file_java):
                    if execute_test(test_suite_file_name, code_file_name):
                        return make_response(jsonify("La test suite debe fallar en almenos un caso de test para poder subirlo"))
                    else:
                        #upload_file(file, test_suite)
                        new_chan = Challenge_java(code=code_file_name, tests_code=test_suite_file_name, repair_objective=objective, complexity=complex, score=0)
                        db.session.add(new_chan)
                        db.session.commit()
                    
                        # show_codes return a dict with code class java and code test
                        output = show_codes(code_file_name)
                        return make_response(jsonify({"challenge": output}))
                else:
                    return make_response(jsonify("Test suite not compile"))
            else:
                return make_response(jsonify("Class java not compile"))
        else:
            return make_response(jsonify("Nombre de archivo existente, cargue nuevamente"), 404)
    else:
        return make_response(jsonify("No ingreso los datos de los archivos java"))


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


# given an id it gets the code of the file
def get_code_file_by_id(id):
    challenge_id = Challenge_java.query.filter_by(id = id).first()
    if challenge_id is not None:
        new_id = Challenge_java.__repr__(challenge_id)
        name_code = new_id['code']
        path = 'public/challenges/' + name_code + '.java'
        file_show = get_code_file_by_path(path)
        return file_show
    return make_response(jsonify({"ERROR": "id not exits"}))
    

# given an path file gets the code of the file
def get_code_file_by_path(file):
    f = open(file, mode='r', encoding='utf-8')
    resp = f.read()
    f.close()
    return resp


# given a file name it returns a dictionary with the code and test_code fields as a string
def show_codes(name_file):
    challenge_aux = Challenge_java.query.filter_by(code = name_file).first()
    if challenge_aux is not None:
        new_var = Challenge_java.__repr__(challenge_aux)
        name_code = new_var['code']
        path = 'public/challenges/' + name_code + '.java'
        file_show = get_code_file_by_path(path)
        new_var['code'] = file_show

        name_test = new_var['tests_code']
        path_test = 'public/challenges/' + name_test + '.java'
        file_show_test = get_code_file_by_path(path_test)
        new_var['tests_code'] = file_show_test
        return new_var
    return make_response(jsonify({"ERROR": "name of file no exist"}))


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

# remove the of file in directory
def delete_path(file_rm):
    if path.exists(file_rm):
        remove(file_rm)


def upload_file_1(file, path):
    if file is None:
        return make_response(jsonify({"error_message": "One of the provided files has syntax errors."}))
    if file.filename == '' :
        return make_response(jsonify("No name of file"), 404)
    if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(path, filename))



def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


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
    
    
    

