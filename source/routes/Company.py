import jwt
import datetime
import numpy as np
import bcrypt
from app import app

from functools import wraps
from models.entities.Company import Company
from flask import Blueprint, jsonify, request

from services.CompanyService import CompanyService

app.config['SECRET_KEY'] = 'ale24key'

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

main = Blueprint('auth-service', __name__)


def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = request.args.get('token')

        if not token:
            return {'message': 'Token is missing', 'statusCode': 406}
        try:
            data = jwt.decode(
                token, app.config['SECRET_KEY'], algorithms=['HS256'])
            # VERIFICAR LA EXISTENCIA DE LA EMPRESA EN LA BD
            #CompanyService.check_exists_company(data, token)
        except:
            return {'message': 'Token is invalid', 'statusCode': 405}

        return f(*args, **kwargs)
    return decorator


@main.route('/company/<id>')
@token_required
def getCompanyById(id):
    try:
        company = CompanyService.get_company_by_id(id)
        return company

    except Exception as ex:
        return jsonify({'message': str(ex)}), 500


@main.route('/verify-images/')
@token_required
def check_coincidence_images():

    # check if the post request has the file part
    if 'file' not in request.files:
        return "File no part"

    files = request.files.getlist("file")

    for file in files:
        if file and allowed_file(file.filename):
            print("File allowed")
        else:
            raise Exception("File not allowed")

    result = CompanyService.check_coincidence(files)
    statusCode = result['statusCode']
    similarity = result['similarity']
    if statusCode != 200:
        return jsonify({'statusCode': statusCode, 'similarity': False})
    if statusCode == 200:
        if similarity == True:
            return jsonify({'statusCode': statusCode, 'similarity': True})
    if statusCode == 200:
        if similarity == False:
            return jsonify({'statusCode': statusCode, 'similarity': False})


@main.route('/register-company/', methods=["POST"])
def register_company():
    crypt = bcrypt.gensalt()
    password = bcrypt.hashpw(request.json["password"].encode('utf-8'), crypt)
    company = Company(
        0, request.json["name"], password, crypt, datetime.datetime.now(), request.remote_addr)
    token = jwt.encode({'company': company.name, 'ip': company.ip, 'exp': datetime.datetime.utcnow(
    ) + datetime.timedelta(hours=24)}, app.config['SECRET_KEY'])
    company.token = token

    CompanyService.add_company(company)

    return jsonify({'token': token, 'company': company.name, 'ip': company.ip})


@main.route('/delete-company/<id>', methods=['DELETE'])
def remove_company(id):
    try:
        result = CompanyService.delete_company(id)
        if result == 1:
            return "SUCCESS"
        # if affected_rows != 0:
        #    return jsonify({'message': 'Company deleted successfuly'}), 200
        # else:
        #    return jsonify({'message': 'Error on delete'})

    except Exception as ex:
        return jsonify({'message': str(ex)}), 500


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
