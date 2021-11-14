from posixpath import basename
from . import cSharp
from json import loads
from app import db
from .models import CSharpChallengeModel
from .models import *
from .c_sharp_src import CSharpSrc
from .c_sharp_challenge import CSharpChallenge 
from flask import jsonify, make_response, json, request
import subprocess, os
from subprocess import PIPE
import nltk
import shutil


CHALLENGE_SAVE_PATH = "example-challenges/c-sharp-challenges/"
CHALLENGE_VALIDATION_PATH = "./public/challenges/"
UPLOAD_FOLDER = "./example-challenges/c-sharp-challenges/"


@cSharp.route('/login')
def login():
    return {'result': 'Ok'}


@cSharp.route('/c-sharp-challenges/<int:id>', methods=['PUT'])
def put_csharp_challenges(id):
    update_request = {}
    update_request['source_code_file'] = request.files.get('source_code_file')
    update_request['test_suite_file'] = request.files.get('test_suite_file')
    update_request['repair_objective'] = request.form.get('repair_objective')
    update_request['complexity'] = request.form.get('complexity')

    challenge = get_challenge_db(id)
    if not exist(id):
        return make_response(jsonify({"challenge": "There is no challenge for this id"}), 404)
    files_keys = ("source_code_file", "test_suite_file")

    challenge_name = os.path.basename(challenge['code'])
    test_name = os.path.basename(challenge['tests_code'])
    challenge_exe = challenge_name.replace('.cs', '.exe')
    test_dll = test_name.replace('.cs', '.dll')
    challenge_dir = CHALLENGE_SAVE_PATH + challenge_name.replace('.cs', '/')
    old_challenge_path = challenge_dir + challenge_name
    old_test_path = challenge_dir + test_name
    new_challenge_path = CHALLENGE_VALIDATION_PATH + challenge_name
    new_test_path = CHALLENGE_VALIDATION_PATH + test_name
    new_challenge_exe_path = CHALLENGE_VALIDATION_PATH + challenge_exe
    new_test_dll_path = CHALLENGE_VALIDATION_PATH + test_dll
    new_challenge = update_request['source_code_file']
    new_test = update_request['test_suite_file']

    if new_challenge is not None and new_test is not None:
        new_ch = CSharpChallenge(new_challenge, 
                                 new_test, 
                                 challenge_name, 
                                 test_name, 
                                 new_challenge_path, 
                                 new_test_path)
        val_status = new_ch.validate()
        handle_put_files(val_status, new_ch.code.path, new_ch.test.path,
                         old_challenge_path, old_test_path)
        if val_status != 1:
            return code_validation_response(val_status)
    elif new_challenge is not None:
        new_ch = CSharpChallenge(new_challenge, 
                                 open(old_test_path, "rb"), 
                                 challenge_name, 
                                 test_name, 
                                 new_challenge_path, 
                                 old_test_path)
        val_status = new_ch.validate()
        handle_put_files(val_status, new_ch.code.path,
                         prev_src_path=old_challenge_path,
                         prev_test_path=new_ch.test.path)
        if val_status != 1:
            return code_validation_response(val_status)
    elif new_test is not None:
        new_ch = CSharpChallenge(open(old_challenge_path, "rb"), 
                                 new_test, 
                                 challenge_name, 
                                 test_name, 
                                 old_challenge_path, 
                                 new_test_path)
        val_status = new_ch.validate()
        handle_put_files(val_status, test_path=new_ch.test.path,
                         prev_src_path=new_ch.code.path,
                         prev_test_path=old_test_path)
        if val_status != 1:
            return code_validation_response(val_status)

    if update_request['repair_objective'] is not None:
        update_challenge_data(id, {'repair_objective': update_request['repair_objective']})

    if update_request['complexity'] is not None:
        complexity = int(update_request['complexity'])
        if complexity < 1 or complexity > 5 :
            return make_response(jsonify({'Complexity': 'Must be between 1 and 5'}), 409)
        else:
            update_challenge_data(id, {'complexity': complexity})
    return make_response(jsonify({'challenge': get_challenge_db(id, show_files_content=True)}), 200)


@cSharp.route('/c-sharp-challenges', methods=['POST'])
def post_csharp_challenges():
    # Get new challenge data
    try:
        new_challenge = loads(request.form.get('challenge'))['challenge']
        new_challenge['source_code_file'] = request.files['source_code_file']
        new_challenge['test_suite_file'] = request.files['test_suite_file']
    except Exception:
        return make_response(jsonify({"challenge": "Data not found"}), 404)
    finally:
        if 'source_code_file' not in new_challenge or 'test_suite_file' not in new_challenge:
            return make_response(jsonify({"challenge": "Data not found"}), 404)

    # Validate challenge data
    required_keys = ('source_code_file_name', 'test_suite_file_name',
                     'source_code_file', 'test_suite_file',
                     'repair_objective', 'complexity')
    if all(key in new_challenge for key in required_keys):
        challenge_dir = CHALLENGE_SAVE_PATH + new_challenge['source_code_file_name']
        try:
            os.mkdir(challenge_dir)
        except FileExistsError:
            return make_response(jsonify({'Challenge': 'Already exists'}), 409)
        new_source_code_path = challenge_dir + "/" + new_challenge['source_code_file_name'] + ".cs"
        new_test_suite_path = challenge_dir + "/" + new_challenge['test_suite_file_name'] + ".cs"
        challenge = CSharpChallenge(new_challenge['source_code_file'],
                                    new_challenge['test_suite_file'],
                                    new_challenge['source_code_file_name'],
                                    new_challenge['test_suite_file_name'],
                                    new_source_code_path,
                                    new_test_suite_path)
        validate_response = challenge.validate()
        new_code_exe_path = challenge.code.path.replace('.cs', '.exe')
        new_test_dll_path = challenge.test.path.replace('.cs', '.dll')
        if validate_response == 0:
            shutil.rmtree(challenge_dir)
            return make_response(jsonify({'Test': 'At least one has to fail'}), 409)

        elif validate_response == 1:
            remove_path([new_code_exe_path, new_test_dll_path])
            complexity = int(new_challenge['complexity'])
            if complexity < 1 or complexity > 5:
                shutil.rmtree(challenge_dir)
                return make_response(jsonify({'Complexity': 'Must be between 1 and 5'}), 409)
            new_challenge['complexity'] = complexity
            new_data_id = save_challenge(new_challenge, 
                                         challenge.code.path,
                                         challenge.test.path)
            content = get_challenge_db(new_data_id, show_files_content=True)
            return make_response(jsonify({'challenge': content}))

        elif validate_response == 2:
            shutil.rmtree(challenge_dir)
            return make_response(jsonify({'Test': 'Sintax errors'}), 409)

        else:
            shutil.rmtree(challenge_dir)
            return make_response(jsonify({'Challenge': 'Sintax errors'}), 409)

    else:
        return make_response(jsonify({'challenge': 'Data not found'}), 404)


@cSharp.route('c-sharp-challenges/<int:id>/repair', methods=['POST'])
def repair_Candidate(id):
    # verify challenge's existence
    if exist(id):
        challenge = get_challenge_db(id)
        challenge_name = os.path.basename(challenge['code'])
        test_name = os.path.basename(challenge['tests_code'])
        try: 
            file = request.files['source_code_file']
        except Exception:
            return make_response(jsonify({'Repair candidate': 'Not found'}), 404)
        repair_path = CHALLENGE_VALIDATION_PATH + challenge_name
        repair = CSharpChallenge(file, open(challenge['tests_code'], "rb"),
                                 challenge_name, test_name, repair_path, 
                                 challenge['tests_code'])
        code = CSharpSrc(open(challenge['code'], "rb"), challenge_name, challenge['code'])
        validation_result = repair.validate()
        if validation_result == -1:
            repair.code.rm()
            return make_response(jsonify({'Repair candidate': 'Sintax error'}), 409)

        elif validation_result == 1:
            repair.code.rm()
            remove_path([repair.code.path.replace('.cs', '.exe'),
                         repair.test.path.replace(".cs", ".dll")])
            return make_response(jsonify({'Repair candidate': 'Tests not passed'}), 409)
        else:
            score = calculate_score(code.path, repair.code.path)

            if save_best_score(score, challenge['best_score'], id) == 0:
                challenge['best_score'] = score

            challenge_data = {
                "repair_objective": challenge['repair_objective'],
                "best_score": challenge['best_score']
            }
            repair.code.rm()
            remove_path([repair.code.path.replace('.cs', '.exe'),
                         repair.test.path.replace(".cs", ".dll")])
            return make_response(jsonify({'Repair': {'challenge': challenge_data, 'score': score}}), 200)
    else:
        return make_response(jsonify({"challenge": "There is no challenge for this id"}), 404)

@cSharp.route('/c-sharp-challenges/<int:id>', methods=['GET'])
def get_challenge(id):
    if exist(id):
        return jsonify({'Challenge': get_challenge_db(id, show_files_content=True)})
    else:
        return make_response(jsonify({'Challenge': 'Not found'}), 404)


@cSharp.route('/c-sharp-challenges', methods=['GET'])
def get_csharp_challenges():
    challenge = {'challenges': []}
    show = []
    challenge['challenges'] = db.session.query(CSharpChallengeModel).all()
    for i in challenge['challenges']:
        show.append(CSharpChallengeModel.__repr__(i))
        j = show.index(CSharpChallengeModel.__repr__(i))
        show[j]['code'] = open(show[j]['code'], "r").read()
        show[j]['tests_code'] = open(show[j]['tests_code'], "r").read()
    if show != []:
        return jsonify({'challenges': show})
    else:
        return jsonify({'challenges': 'None Loaded'})


def remove_path(path_list):
    for path in path_list:
        os.remove(path)


def calculate_score(challenge_path, repair_candidate_path):
    challenge_script = open(challenge_path, "r").readlines()
    repair_script = open(repair_candidate_path, "r").readlines()
    return nltk.edit_distance(challenge_script, repair_script)


def save_best_score(score, previous_best_score, chall_id):
    if previous_best_score == 0 or previous_best_score > score:
        challenge = db.session.query(CSharpChallengeModel).filter_by(id=chall_id)
        challenge.update(dict(best_score=score))
        db.session.commit()
        return 0
    else:
        return 1


def handle_put_files(result, src_path=None, test_path=None, prev_src_path=None, prev_test_path=None):
    if src_path is not None:
        exe_new = src_path.replace('.cs', '.exe')
    if test_path is not None:
        dll_new = test_path.replace('.cs', '.dll')
    if prev_src_path is not None:
        exe_prev = prev_src_path.replace('.cs', '.exe')
    if prev_test_path is not None:
        dll_prev = prev_test_path.replace('.cs', '.dll')

    if result == -1:
        if test_path is not None:
            remove_path([src_path, test_path])
        else:
            remove_path([src_path])
    elif result == 0:
        if test_path is not None and src_path is not None:
            remove_path([src_path, test_path, exe_new, dll_new])
        elif src_path is not None:
            remove_path([src_path, exe_new, dll_prev])
        else:
            remove_path([test_path, exe_prev, dll_new])
    elif result == 2:
        if src_path is not None:
            remove_path([src_path, test_path, exe_new])
        else:
            remove_path([test_path, exe_prev])
    elif result == 1:
        if test_path is not None and src_path is not None:
            remove_path([exe_new, dll_new, prev_src_path, prev_test_path])
            shutil.move(src_path, prev_src_path)
            shutil.move(test_path, prev_test_path)
        elif src_path is not None:
            remove_path([exe_new, dll_prev, prev_src_path])
            shutil.move(src_path, prev_src_path)
        else:
            remove_path([dll_new, exe_prev, prev_test_path])
            shutil.move(test_path, prev_test_path)


def code_validation_response(val_status):
    if val_status == -1:
        return make_response(jsonify({'Source code': 'Sintax errors'}), 409)
    elif val_status == 0:
        return make_response(jsonify({'Challenge': 'Must fail at least one test'}), 409)
    elif val_status == 2:
        return make_response(jsonify({'Test': 'Sintax errors'}), 409)
