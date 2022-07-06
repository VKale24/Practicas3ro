import io
import os
import cv2
import numpy as np
import face_recognition
from flask import jsonify
from werkzeug.exceptions import NotFound

from database.db import db_session, Base, engine
from models.CompanyModel import CompanyBase

Base.metadata.create_all(engine)


class CompanyService():
    @classmethod
    def check_coincidence(self, images):
        band = True
        for image in images:
            in_memory_file = io.BytesIO()
            image.save(in_memory_file)
            data = np.fromstring(in_memory_file.getvalue(), dtype=np.uint8)
            color_image_flag = 1
            img = cv2.imdecode(data, color_image_flag)
            if band == True:
                image1 = img
            else:
                image2 = img
            band = False

        # Convert into grayscale
        gray1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)

        # Load the cascade
        face_cascade = cv2.CascadeClassifier(
            'haarcascade_frontalface_default.xml')

        # Detect faces
        faces1 = face_cascade.detectMultiScale(gray1, 1.1, 4)
        faces2 = face_cascade.detectMultiScale(gray2, 1.1, 4)

        # Draw rectangle around the faces and crop the faces
        for (x, y, w, h) in faces1:

            cv2.rectangle(image1, (x, y), (x+w, y+h), (0, 0, 0), 5)

            faces1 = image1[y:y + h, x:x + w]
            cv2.waitKey()

        for (x, y, w, h) in faces2:

            cv2.rectangle(image2, (x, y), (x+w, y+h), (0, 0, 0), 5)

            faces2 = image2[y:y + h, x:x + w]

        try:
            new_width = int(160)
            new_height = int(160)
            resized1 = cv2.resize(faces1, (new_width, new_height))
            cv2.imwrite('face1.jpg', resized1)
            resized2 = cv2.resize(faces2, (new_width, new_height))
            cv2.imwrite('face2.jpg', resized2)
        
            img = cv2.imread("face1.jpg")
            rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img_encoding = face_recognition.face_encodings(rgb_img)[0]

            img2 = cv2.imread("face2.jpg")
            rgb_img2 = cv2.cvtColor(img2, cv2.COLOR_BGR2RGB)
            img_encoding2 = face_recognition.face_encodings(rgb_img2)[0]

            result = face_recognition.compare_faces(
                [img_encoding], img_encoding2)
            os.remove("face1.jpg")
            os.remove("face2.jpg")
            for res in result:
                equalFace = res
            if equalFace == True:
                return {'similarity': equalFace, 'statusCode': 200}
            else:
                return {'similarity': equalFace, 'statusCode': 501}

        except Exception as ex:
            return {'error': str(ex), 'message': 'Bad Image Quality', 'statusCode': 502, 'similarity': False}

    @classmethod
    def add_company(self, company):
        CompanyService.check_name_used(company.name)
        u = CompanyBase(company.name, company.password, company.crypt, company.register_date,
                        company.ip, company.token)
        db_session.add(u)
        db_session.commit()

    @classmethod
    def check_name_used(self, name):

        company = db_session.query(CompanyBase)\
            .filter(CompanyBase.name == name).first()

        if company:
            raise Exception("Conflict name")

    @classmethod
    def get_company_by_id(self, id):

        company = db_session.query(CompanyBase)\
            .filter(CompanyBase.id == id).first()
        if company:
            return jsonify({"name": company.name, "register_date": company.register_date, "ip": company.ip, "token": company.token})
        raise NotFound("No se encontró ninguna compañía con id: " + id)

    @classmethod
    def delete_company(self, id):
        CompanyService.get_company_by_id(id)

        result = db_session.query(CompanyBase)\
            .filter(CompanyBase.id == id).delete()
        db_session.commit()
        return result

    @classmethod
    def check_exists_company(self, data, token):

        company = db_session.query(CompanyBase)\
            .filter(CompanyBase.name == data["name"], CompanyBase.ip == data["ip"]).first()

        if company:
            if token == company.token:
                return company
            raise NotFound("No se encontró ninguna compañía con id: " + id)
        raise NotFound("No se encontró ninguna compañía con id: " + id)
