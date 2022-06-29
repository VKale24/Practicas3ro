import io
import os
import cv2
import numpy as np
from app import app
import face_recognition
from database.db import get_connection
from werkzeug.exceptions import NotFound


from models.entities import Company, CompanyDB
from models.entities.CompanyDB import init_db, db_session



init_db()

class CompanyModel():
    @classmethod
    def get_company_by_id(self, id):
        try:
            connection = get_connection()
            company = None
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM public.empresa WHERE id = %s", (id,))
                row = cursor.fetchone()

                if row != None:
                    company = Company(row[0], row[1], row[2], row[3])
                    company = company.to_JSON()
                    connection.close()
                    return company
                else:
                    connection.close()
                    raise NotFound("Not found company with id: " + id)

        except Exception as ex:
            raise Exception(ex)

    @classmethod
    def check_exists_company(self, data, token):
        try:
            connection = get_connection()
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT token FROM public.empresa WHERE name = %s AND ip = %s", (data["company"], data["ip"]))
                row = cursor.fetchone()
                if row != None:
                    if token == row[0]:
                        connection.close()
                        return True
                    else:
                        connection.close()
                        raise NotFound(
                            "Not found any company with name: " + data.name + "and ip: " + data.ip)
                else:
                    connection.close()
                    raise NotFound("Not found any company with name: " +
                                   data.name, "and ip: " + data.ip)

        except Exception as ex:
            raise Exception(ex)

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

            #cv2.rectangle(image1, (x, y), (x+w, y+h), (0, 0, 255), 2)
            cv2.rectangle(image1, (x, y), (x+w, y+h), (0, 0, 0), 5)

            faces1 = image1[y:y + h, x:x + w]
            #cv2.imshow("faces1", faces1)
            cv2.waitKey()

        for (x, y, w, h) in faces2:

            cv2.rectangle(image2, (x, y), (x+w, y+h), (0, 0, 0), 5)

            faces2 = image2[y:y + h, x:x + w]

        new_width = int(160)
        new_height = int(160)
        resized1 = cv2.resize(faces1, (new_width, new_height))
        cv2.imwrite('face1.jpg', resized1)
        resized2 = cv2.resize(faces2, (new_width, new_height))
        cv2.imwrite('face2.jpg', resized2)

        img = cv2.imread("face1.jpg")
        rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_encoding = face_recognition.face_encodings(rgb_img)[0]

        img2 = cv2.imread("face1.jpg")
        rgb_img2 = cv2.cvtColor(img2, cv2.COLOR_BGR2RGB)
        img_encoding2 = face_recognition.face_encodings(rgb_img2)[0]

        result = face_recognition.compare_faces([img_encoding], img_encoding2)
        os.remove("face1.jpg")
        os.remove("face2.jpg")
        return result

    @classmethod
    def add_company(self, company):
        u = CompanyDB(company.name, company.register_date, company.ip, company.token)
        db_session.add(u)
        db_session.commit()
        #try:
         #   connection = get_connection()
         #   with connection.cursor() as cursor:
         #       CompanyModel.verify_conflict_name(company.name)
          #      cursor.execute(
          #          "INSERT INTO public.empresa(name, register_date, ip, token) VALUES (%s, %s, %s, %s)", (company.name, company.register_date, company.ip, company.token))
         #       affected_row = cursor.rowcount
         #      connection.commit()
          #      return affected_row

       # except Exception as ex:
          #  raise Exception(ex)

    @classmethod
    def delete_company(self, id):
        try:
            connection = get_connection()
            CompanyModel.get_company_by_id(id)
            with connection.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM public.empresa WHERE id = %s", (id,))
                affected_row = cursor.rowcount
                connection.commit()

                return affected_row

        except Exception as ex:
            raise Exception(ex)

    @classmethod
    def verify_conflict_name(self, name):
        try:
            connection = get_connection()
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT name FROM public.empresa WHERE name = %s", (name,))
                row = cursor.fetchone()
                if row != None:
                    raise Exception("Conflict name")

        except Exception as ex:
            raise Exception(ex)