from werkzeug.wrappers import response
from app.java.models_java import Challenge_java
from . import client
import json
from app.java.views import *
import os

urlClass = 'example-challenges/java-challenges/Median.java'
urlTest = 'example-challenges/java-challenges/MedianTest.java'

exampleClass = 'tests/java/example_java/Prueba.java'
exampleTest = 'tests/java/example_java/PruebaTest.java'


def createQuery():
	fileClass = open(urlClass, 'rb')
	fileTest = open(urlTest, 'rb')
	
	challenge = {
		'source_code_file': fileClass,
		'test_suite_file': fileTest,
		'challenge':'{ \
            "challenge":{\
                "source_code_file_name": "Median",\
                "test_suite_file_name": "MedianTest",\
                "repair_objective": "algo para acomodar",\
                "complexity": "1"\
            }\
        }'
	}
	return challenge

def createQuery2(urlClass, urlTest):
	fileClass = open(urlClass, 'rb')
	fileTest = open(urlTest, 'rb')
	
	challenge = {
		'source_code_file': fileClass,
		'test_suite_file': fileTest,
		'challenge':'{ \
            "challenge":{\
                "source_code_file_name": "Prueba",\
                "test_suite_file_name": "PruebaTest",\
                "repair_objective": "Pasa los test",\
                "complexity": "3"\
            }\
        }'
	}
	return challenge

def test_post_java(client):
	db.session.query(Challenge_java).delete()
	
	url = 'http://localhost:5000/java/java-challenges'

	data = createQuery()
	resp = client.post(url, data=data)
	
	assert resp.status_code == 200
	
def test_post_get_all(client):
	db.session.query(Challenge_java).delete()
	url = 'http://localhost:5000/java/java-challenges'

	data = createQuery()
	client.post(url, data=data)
	resp = client.get(url)
	response = json.loads(json.dumps(resp.json))
	a = response['challenges'][0]
	
	assert resp.status_code == 200
	assert len(response['challenges']) == 1
	assert a['repair_objective'] == 'algo para acomodar'
	assert a['complexity'] == 1
	assert a['id'] != 0
	
def test_many_loads(client):
	db.session.query(Challenge_java).delete()
	url = 'http://localhost:5000/java/java-challenges'

	data = createQuery()
	data2 = createQuery2(exampleClass, exampleTest)
	client.post(url, data=data)
	p = client.post(url, data=data2)

	resp = client.get(url)
	response = json.loads(json.dumps(resp.json))
	b = response['challenges']
	
	assert p.status_code == 200
	assert resp.status_code == 200
	assert len(response['challenges']) == 2
	assert b[0]['repair_objective'] == 'algo para acomodar'
	assert b[1]['repair_objective'] == 'Pasa los test'

def test_upload_exist(client):
	db.session.query(Challenge_java).delete()
	url = 'http://localhost:5000/java/java-challenges'
	data = createQuery()
	datab = createQuery()
	resp = client.post(url, data=data)
	resp2 = client.post(url, data=datab)

	assert resp.status_code == 200
	assert resp2.status_code == 404

	
def test_get_java(client):
	db.session.query(Challenge_java).delete()
	url = 'http://localhost:5000/java/java-challenges'
	resp = client.get(url)
	a = resp.json
	
	assert resp.status_code == 200
	assert a['challenges'] == []
	
def test_get_Id_after_post(client):
	db.session.query(Challenge_java).delete()
	url = 'http://localhost:5000/java/java-challenges'
	data = createQuery()

	p = client.post(url, data=data)
	json = p.json['challenge']
	id = json['id']

	url2 = f'http://localhost:5000/java/java-challenges/{id}'
	p2 = client.get(url2)
	json2 = p2.json['challenge']
	id2=json2['id']

	assert p.status_code == 200
	assert p2.status_code == 200
	assert id == id2

def test_get_Id_noesxite(client):
	db.session.query(Challenge_java).delete()
	id=1
	url2 = f'http://localhost:5000/java/java-challenges/{id}'
	p2 = client.get(url2)
	
	assert p2.status_code == 404
	