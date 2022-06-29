import jwt
import datetime
import numpy as np
from app import app
from functools import wraps
from models.entities.Company import Company
from flask import Blueprint, jsonify, request

from models.CompanyModel import CompanyModel

app.config['SECRET_KEY'] = 'ale24key'

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'JPG'}

main = Blueprint('auth-service', __name__)

def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = request.args.get('token')

        if not token:
            return jsonify({'message': 'Token is missing'}), 403
        try:
            data = jwt.decode(
                token, app.config['SECRET_KEY'], algorithms=['HS256'])
            # VERIFICAR LA EXISTENCIA DE LA EMPRESA EN LA BD
            CompanyModel.check_exists_company(data, token)
        except:
            return jsonify({'message': 'Token is invalid'}), 403

        return f(*args, **kwargs)
    return decorator


@main.route('/company/<id>')
@token_required
def getCompanyById(id):
    try:
        company = CompanyModel.get_company_by_id(id)
        return jsonify(company)

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

    similarity = CompanyModel.check_coincidence(files)

    return jsonify({'statusCode': 200, 'similarity': similarity})


@main.route('/register-company/', methods=["POST"])
def register_company():
    #auth = request.authorization
    # if auth and auth.password == 'password':
    # token = jwt.encode({'company': auth.username, 'exp': datetime.datetime.utcnow(
    # ) + datetime.timedelta(hours=24)}, app.config['SECRET_KEY'])

    company = Company(
        0, request.json["name"], datetime.datetime.now(), request.remote_addr)
    token = jwt.encode({'company': company.name, 'ip': company.ip, 'exp': datetime.datetime.utcnow(
    ) + datetime.timedelta(hours=24)}, app.config['SECRET_KEY'])
    company.token = token

    CompanyModel.add_company(company)

    return jsonify({'token': token, 'company': company.name, 'ip': company.ip})
    # return jsonify({'token': token})

    # return make_response('Could not verify!', 401, {'WWW-Authenticate': 'Basic realm="Login Required"'})

    # name = request.json['name']
   # password = request.json['password']

    # company = Company(0, '', name, password, datetime.now())
    # affected_rows = CompanyModel.add_company(company)

   # if affected_rows != 0:
    # return jsonify({'message': 'Company registered successfuly'}), 200
    # else:
    # return jsonify({'message': 'Error on insert'})


@main.route('/delete-company/<id>', methods=['DELETE'])
def remove_company(id):
    try:
        affected_rows = CompanyModel.delete_company(id)

        if affected_rows != 0:
            return jsonify({'message': 'Company deleted successfuly'}), 200
        else:
            return jsonify({'message': 'Error on delete'})

    except Exception as ex:
        return jsonify({'message': str(ex)}), 500


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
