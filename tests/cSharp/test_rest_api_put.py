import os
import pytest
from app import create_app, db
from . import *
from app.cSharp.models import CSharpChallengeModel
import shutil

def test_update_incorrect_complexity(client, create_test_data, auth):
    #Arrange
    url_post = 'cSharp/c-sharp-challenges'
    data = create_test_data['data']

    data_put = create_challenge(complexity=8)
    #Act
    resp_post = client.post(url_post, data=data, headers={'Authorization': f'JWT {auth}'})
    challenge_id = resp_post.json['challenge']['id']
    
    url_put = 'cSharp/c-sharp-challenges/' + str(challenge_id) 
    resp_put = client.put(url_put, data=data_put, headers={'Authorization': f'JWT {auth}'})

    #Assert
    assert resp_put.status_code == 409
    assert resp_put.json == {'Complexity': 'Must be between 1 and 5'}
    cleanup()

def test_update_code_w_sintax_error(client,create_test_data, auth):
    #Arrange
    url_post = 'cSharp/c-sharp-challenges'
    data = create_test_data['data']
    data_put = {'source_code_file': open('tests/cSharp/test-files/ExampleSintaxErrors.cs', 'rb')}
    
    #Act
    resp_post = client.post(url_post, data=data, headers={'Authorization': f'JWT {auth}'})
    challenge_id = resp_post.json['challenge']['id'] 

    url_put = 'cSharp/c-sharp-challenges/' + str(challenge_id) 
    resp_put = client.put(url_put, data=data_put, headers={'Authorization': f'JWT {auth}'})
    
    #Assert
    assert resp_put.status_code == 409
    assert resp_put.json == {'Source code': 'Sintax errors'}
    cleanup()

def test_update_complexity_and_repair_objective(client, create_test_data, auth):
    url_post = 'cSharp/c-sharp-challenges'
    data = create_test_data['data']
    data_put = create_challenge(repair_objective='Test this method', complexity='4')
    expected_response = {"challenge": { "code": create_test_data['content_code'],
                                        "tests_code":  create_test_data['content_tests_code'],
                                        "repair_objective": "Test this method",
                                        "complexity": 4,
                                        "best_score": 0
                                       }
                        }

    resp_post = client.post(url_post, data=data, headers={'Authorization': f'JWT {auth}'})
    challenge_id = resp_post.json['challenge']['id']
     
    url_put = 'cSharp/c-sharp-challenges/' + str(challenge_id) 
    resp_put = client.put(url_put, data=data_put, headers={'Authorization': f'JWT {auth}'})
    resp_put_json = resp_put.json
    del resp_put_json['challenge']['id']
    print(resp_put.json)
    
    #Assert
    assert resp_put.status_code == 200
    assert resp_put_json == expected_response
    cleanup()

def test_update_code_passes_all_tests(client, create_test_data, auth):
    # Arrange
    url = 'cSharp/c-sharp-challenges'

    data_put = create_challenge(code_name='Example1', code='ExampleNoFails')
    expected_response = {'Challenge': 'Must fail at least one test'}

    # Act
    resp_post = client.post(url, data=create_test_data['data'], headers={'Authorization': f'JWT {auth}'})
    ch_id = resp_post.json['challenge']['id']
    url += '/' + str(ch_id)

    resp_put = client.put(url, data=data_put, headers={'Authorization': f'JWT {auth}'})
    resp_json = resp_put.json
    resp_code = resp_put.status_code

    # Assert
    assert resp_code == 409
    assert resp_json == expected_response

    # Cleanup
    cleanup()


def test_put_non_existent_challenge(client, auth):
    # Arrange
    url = 'cSharp/c-sharp-challenges/1'
    expected_response = {"challenge": "There is no challenge for this id"}
    data_put={}

    # Act
    resp = client.put(url, data=data_put, headers={'Authorization': f'JWT {auth}'})
    resp_json = resp.json

    # Assert
    assert resp_json == expected_response
    assert resp.status_code == 404

    # Cleanup
    cleanup()

def test_put_with_code_and_test_and_without_challenge(client, create_test_data, auth):
    # Arrange
    url = 'cSharp/c-sharp-challenges'
    data_post = create_test_data['data']
    data_put = create_challenge(code="BaseExample3", tests_code="BaseTest3")
    with open('tests/cSharp/test-files/BaseExample3.cs') as f:
        new_content_code = f.read()
    with open('tests/cSharp/test-files/BaseTest3.cs') as f:
        new_content_tests_code = f.read()

    # Act
    resp_post = client.post(url, data=data_post, headers={'Authorization': f'JWT {auth}'})
    challenge_id = resp_post.json["challenge"]["id"]
    url_put = 'cSharp/c-sharp-challenges/' + str(challenge_id)
    resp_put = client.put(url_put, data=data_put, headers={'Authorization': f'JWT {auth}'})

    # Assert
    resp_put_json = resp_put.json
    del resp_put_json ['challenge']['id']
    
    assert resp_put.status_code == 200
    assert resp_put_json == {"challenge": { "best_score": 0,
                                            "code": new_content_code,
                                            "complexity": 5,
                                            "repair_objective": "Testing",
                                            "tests_code":new_content_tests_code                                                  
                                          }
                            }
    
    # Cleanup
    cleanup()

def test_put_with_only_test(client, create_test_data, auth):
    # Arrange
    url = 'cSharp/c-sharp-challenges'

    data_post = create_test_data['data']
    data_put = create_challenge(tests_name='Example1Test', tests_code="BaseTest")
    with open('tests/cSharp/test-files/BaseTest.cs') as f:
        new_content_tests_code = f.read()
    expected_response = {"challenge": { "best_score": 0,
                                        "code":create_test_data['content_code'],
                                        "complexity": 5,
                                        "repair_objective": "Testing",
                                        "tests_code":new_content_tests_code                                                  
                                       }
                        }
    # Act
    resp_post = client.post(url, data=data_post, headers={'Authorization': f'JWT {auth}'})
    challenge_id = resp_post.json["challenge"]["id"]
    url_put = 'cSharp/c-sharp-challenges/' + str(challenge_id)
    resp_put = client.put(url_put, data=data_put, headers={'Authorization': f'JWT {auth}'})
    # Assert
    resp_put_json = resp_put.json
    del resp_put_json ['challenge']['id']
    
    assert resp_put.status_code == 200
    assert resp_put_json == expected_response
    
    # Cleanup
    cleanup()

def test_update_test_with_sintax_error(client,create_test_data, auth):
    #todo implement
    pass
