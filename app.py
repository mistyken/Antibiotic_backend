# app.py

import os

import boto3

from flask import Flask, jsonify, request
from flask_cors import cross_origin
from auth import AuthError, requires_auth
app = Flask(__name__)

USERS_TABLE = os.environ['USERS_TABLE']
METRICS_TABLE = os.environ['METRICS_TABLE']
client = boto3.client('dynamodb')


@app.errorhandler(AuthError)
def handle_auth_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response


@app.route("/")
@cross_origin(headers=["Content-Type", "Authorization"])
def hello():
    return "Antibiotic backend v0.1"


@app.route("/users/<string:email>")
@cross_origin(headers=["Content-Type", "Authorization"])
@requires_auth
def get_user(email):
    resp = client.get_item(
        TableName=USERS_TABLE,
        Key={
            'email': {'S': email}
        }
    )
    item = resp.get('Item')
    if not item:
        return jsonify({'error': 'User does not exist'}), 404

    return jsonify({
        'first_name': item.get('first_name').get('S'),
        'last_name': item.get('last_name').get('S'),
        'email': item.get('email').get('S')
    })


@app.route("/users", methods=["POST"])
@cross_origin(headers=["Content-Type", "Authorization"])
@requires_auth
def create_user():
    first_name = request.json.get('first_name')
    last_name = request.json.get('last_name')
    email = request.json.get('email')
    if not first_name or not last_name or not email:
        return jsonify({'error': 'Please provide first name, last name and email'}), 400

    client.put_item(
        TableName=USERS_TABLE,
        Item={
            'first_name': {'S': first_name },
            'last_name': {'S': last_name},
            'email': {'S': email}
        }
    )

    return jsonify({
        'first_name': first_name,
        'last_name': last_name,
        'email': email
    })


@app.route("/metrics", methods=["POST"])
@cross_origin(headers=["Content-Type", "Authorization"])
@requires_auth
def post_metrics():
    deviceId = request.json.get('deviceId')
    datetime = request.json.get('datetime')
    email = request.json.get('email')
    heart_rate = request.json.get('heart_rate')

    if not deviceId or not datetime or not email:
        return jsonify({'error': 'Please provide deviceId, datetime and email'}), 400

    client.put_item(
        TableName=METRICS_TABLE,
        Item={
            'metricId': {'S': '{}-{}'.format(deviceId, email)},
            'datetime': {'S': datetime},
            'heart_rate': {'S': heart_rate}
        }
    )

    return jsonify({
        'metricId': '{}-{}'.format(deviceId, email),
        'datetime': datetime,
        'heart_rate': heart_rate
    })
