import json
from flask import jsonify, request, make_response, json
from app import db
from . import go
from .models_go import GoChallenge
import os, subprocess, math, nltk, shutil
from .go_challenge_dao import goChallengeDAO
from .go_src import Go_src
from .go_challenge import GoChallengeC


goDAO = goChallengeDAO()


@go.route('api/v1/go-challenges/<int:id>/repair', methods=['POST'])
def repair_challenge_go(id):
    code_solution_file = request.files['source_code_file']
    subprocess.run(["mkdir","solution"],cwd="public/challenges",stderr=subprocess.STDOUT, stdout=subprocess.DEVNULL)
    code_solution_path = os.path.abspath('public/challenges/solution/code_solution.go')
    code_solution_file.save(code_solution_path)
    
    is_good_code_solution_file = subprocess.run(["go build"], cwd=os.path.abspath("public/challenges/solution"),stderr=subprocess.STDOUT, stdout=subprocess.DEVNULL, shell=True)
    if is_good_code_solution_file.returncode == 2:
        return make_response((jsonify({"code_solution_file":"with errors"}),409))
    
    challenge_original = GoChallenge.query.filter_by(id=id).first()
    if challenge_original is None:
        return make_response(jsonify({'Challenge' : 'this challenge does not exist'}), 404)
    challenge_to_dict = challenge_original.convert_dict()
    tests_code = challenge_to_dict["tests_code"]
    
    shutil.copy (tests_code,"public/challenges/solution/code_test.go")
    
    the_challenge_is_solved = subprocess.run(["go test"],cwd=os.path.abspath("public/challenges/solution"),stderr=subprocess.STDOUT, stdout=subprocess.DEVNULL, shell=True)
    if the_challenge_is_solved.returncode == 1:
        return make_response((jsonify({"the challenge":"not solved"}),409))  
    
    challenge_original_code = challenge_to_dict["code"]
    
    f = open (challenge_original_code,'r')
    original_code = f.read()
    f.close()

    f = open (code_solution_path,'r')
    solution_code = f.read()
    f.close()

    edit_distance = nltk.edit_distance(original_code,solution_code)

    current_best_score = challenge_to_dict["best_score"]
    if edit_distance < current_best_score:
        challenge_original.best_score = edit_distance
        db.session.commit()

    challenge_original_updated = GoChallenge.query.filter_by(id=id).first()
    challenge_to_dict_updated = challenge_original_updated.convert_dict()
        

    request_return = {
        "repair":{
            "challenge":{
                "repair_objective": challenge_to_dict["repair_objective"],
                "best_score": challenge_to_dict_updated["best_score"]
            },
            "score": edit_distance
        }
    }

    subprocess.run(["rm" "-r" "solution"],cwd=os.path.abspath("public/challenges"),stderr=subprocess.STDOUT, stdout=subprocess.DEVNULL, shell=True)
    
    return jsonify(request_return)


@go.route('/api/v1/go-challenges', methods=['GET'])
def get_all_challenges():
    #challenges = db.session.query(GoChallenge).all()
    challenges = goDAO.get_all_challenges()
    if not challenges:
        return make_response(jsonify({'challenges' : 'not found'}), 404)
    
    challenges_to_show = []
    i = 0   
    for challenge in challenges:
        challenge_dict = challenge.convert_dict()
        from_file_to_str(challenge_dict, 'code')
        challenges_to_show.append(challenge_dict)
        del challenges_to_show[i]['tests_code']
        i+=1

    return jsonify({"challenges" : challenges_to_show})



@go.route('/api/v1/go-challenges/<id>', methods=['GET'])
def return_single_challenge(id):
    #challenge_by_id=GoChallenge.query.filter_by(id=id).first()
    challenge_by_id = goDAO.get_challenge_by_id(id)
    if challenge_by_id is None:
        return "ID Not Found", 404
    challenge_to_return=challenge_by_id.convert_dict()
    from_file_to_str(challenge_to_return, "code")
    from_file_to_str(challenge_to_return, "tests_code")
    del challenge_to_return["id"]
    return jsonify({"challenge":challenge_to_return})


@go.route('/api/v1/go-challenges/<id>', methods=['PUT'])
def update_a_go_challenge(id):

    challenge = goDAO.get_challenge_by_id(id)
    if not goDAO.exists(id):
        return make_response(jsonify({'challenge' : 'not found'}), 404)
    
    directory  = 'tmp'
    parent_dir = 'example-challenges/go-challenges'
    path_directory = Go_src.create_path(parent_dir, directory)
    temporary_directory = Go_src(path=path_directory)
    if request.files and not(temporary_directory.is_dir()):
        temporary_directory.create_dir()

    challenge_old = GoChallengeC(challenge.id, challenge.code, challenge.tests_code, challenge.repair_objective, challenge.complexity)
    old_code_path = Go_src(path=challenge_old.get_code())
    old_test_path = Go_src(path=challenge_old.get_tests_code())
    request_data = json.loads(request.form.get('challenge'))['challenge']
    ########
    ##La info nueva es un challenge?
    ########
    new_challenge = GoChallengeC()

    new_code = 'source_code_file' in request.files 
    if new_code:
        if not ('source_code_file_name' in request_data):
            return make_response(jsonify({"file name" : "conflict"}), 409)

        new_code_name = request_data['source_code_file_name']
        new_code_path = Go_src.create_path(temporary_directory.get_path(), new_code_name)
        new_code_file = Go_src(path=new_code_path, file=request.files['source_code_file'])
        new_challenge.set_code(new_code_file.get_path())
        new_code_file.save()

        if not new_challenge.code_compiles():
            new_challenge.remove_code_file()
            return make_response(jsonify({"code_file":"code with sintax errors"}),409)           

    new_test = 'test_suite_file' in request.files
    if new_test: 
        if not ('test_suite_file_name' in request_data):
            return make_response(jsonify({"file name" : "conflict"}),409)
        
        new_test_name = request_data['test_suite_file_name']
        new_test_path = Go_src.create_path(temporary_directory.get_path(), new_test_name)
        new_test_file = Go_src(path=new_test_path, file=request.files['test_suite_file'])
        new_challenge.set_tests_code(new_test_file.get_path())
        new_test_file.save()

        if not new_challenge.tests_compiles():
            new_challenge.remove_test_file()
            return make_response(jsonify({"test_code_file":"test with sintax errors"}),409)

    if new_code and new_test:
        if not new_challenge.tests_fail():
            #podria borrar la carpeta?
            new_challenge.remove_code_file()
            new_challenge.remove_test_file()
            return make_response(jsonify({'error' : 'test must fails'}), 412)  

    elif new_code and not new_test:
        directory_to_tests = 'temp_test.go'
        path_to_tests = Go_src.create_path(temporary_directory.get_path(), directory_to_tests)
        #deberia darle el file??
        temp_test_file = Go_src(path=path_to_tests)
        temp_test_file.rewrite_file(old_test_path.get_path())
        
        #no estoy seguro de que sea correcto llamarlo con temp_test_file
        if not temp_test_file.tests_fail():
            temporary_directory.delete_files()
            return make_response(jsonify({'error' : 'test must fails'}), 412)

    elif not new_code and new_test:
        directory_to_code = 'temp.go'
        path_to_temp_code_file = Go_src.create_path(temporary_directory.get_path(), directory_to_code)
        temp_code_file = Go_src(path=path_to_temp_code_file)
        temp_code_file.rewrite_file(old_code_path.get_path())
        
        if not temp_code_file.tests_fail():
            temporary_directory.delete_files()
            return make_response(jsonify({'error' : 'test must fails'}), 412)

    if new_code:
        old_code_path.rewrite_file(new_code_file.get_path())
        new_challenge.set_code(old_code_path.get_path) 
        new_code_file.remove_file()

    if new_test:
        old_test_path.rewrite_file(new_test_file.get_path())
        new_challenge.set_tests_code(old_test_path.get_path())
        new_test_file.remove_file()
    
    if request.files:
        temporary_directory.remove_dir()

    if 'repair_objective' in request_data and request_data['repair_objective'] != challenge.repair_objective:
        new_challenge.set_repair_objective(request_data['repair_objective'])

    if 'complexity' in request_data and request_data['complexity'] != challenge.complexity:
       new_challenge.set_complexity(request_data['complexity'])

    #goDAO.update_challenge(id, new_challenge.get_content_post())
    #challenge_updated = goDAO.get_challenge_by_id(id)

    db.session.commit()
    challenge_dict = challenge.convert_dict()
    from_file_to_str(challenge_dict, 'code')
    from_file_to_str(challenge_dict, 'tests_code')
    del challenge_dict['id']

    return jsonify({'challenge':challenge_dict})
    

@go.route('/api/v1/go-challenges', methods=['POST'])
def create_go_challenge():
    challenge_data = json.loads(request.form.get('challenge'))['challenge']

    code_file = request.files["source_code_file"]
    code_path = 'public/challenges/' + challenge_data['source_code_file_name']
    code_file.save(code_path)

    test_suite_file = request.files["test_suite_file"]
    test_suite_path = 'public/challenges/' + challenge_data['test_suite_file_name']
    test_suite_file.save(test_suite_path)

    new_challenge = GoChallenge(
        code=code_path,
        tests_code=test_suite_path,
        repair_objective=challenge_data['repair_objective'],
        complexity=challenge_data['complexity'],
        best_score=math.inf)

    #all_the_challenges = db.session.query(GoChallenge).all()
    all_the_challenges = goDAO.get_all_challenges()
    for every_challenge in all_the_challenges:
        if every_challenge.code == new_challenge.code:
            return make_response(jsonify({"challenge": "repeated"}), 409)

    test_pass = subprocess.run(["go" "test"], cwd=os.path.abspath("public/challenges"), shell=True)
    test_compilation = subprocess.run(["go" "test" "-c"], cwd=os.path.abspath("public/challenges"),shell=True)
    code_compilation = subprocess.run(["go" "build", code_path], stderr=subprocess.STDOUT, stdout=subprocess.DEVNULL,shell=True)

    codigo = Go_src(path=code_path)
    tests = Go_src(path="public/challenges")

    if code_compilation == 1:
        return make_response(jsonify({"code_file": "The code has syntax errors"}), 412)
    elif test_compilation == 1 or test_compilation.returncode == 2:
        return make_response(jsonify({"test_code_file": "The test code has syntax errors"}), 412)
    elif test_pass.returncode == 0:
        return make_response(jsonify({"ERROR: tests": "There must be at least one test that fails"}), 412)

    db.session.add(new_challenge)
    db.session.commit()

    new_challenge_to_dicc = new_challenge.convert_dict()
    from_file_to_str(new_challenge_to_dicc, "code")
    from_file_to_str(new_challenge_to_dicc, "tests_code")
    return jsonify({"challenge": new_challenge_to_dicc})


def from_file_to_str(challenge, attribute):
    file= open(str(os.path.abspath(challenge[attribute])),'r')
    content=file.readlines()
    file.close()
    challenge[attribute]=content
    return challenge

def compiles(commands, path):
    return (subprocess.run(commands, cwd=path, stderr=subprocess.STDOUT, stdout=subprocess.DEVNULL).returncode == 0)

def compiles(command):
    return (subprocess.call(command, shell=True, stderr=subprocess.STDOUT, stdout=subprocess.DEVNULL) == 0)

def content(path):
    f = open(path, 'r')
    return f.read()

def rewrite_file(path_to_file_used_to_update, path_to_file_to_update):
    with open(path_to_file_used_to_update) as file_used_to_update:
            with open(path_to_file_to_update, 'w') as file_to_update:
                for line in file_used_to_update:
                    file_to_update.write(line)

def delete_files(path):
    for file in os.listdir(path):
      os.remove(os.path.join(path, file))

