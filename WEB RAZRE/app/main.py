import os
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

import requests
from flask import Flask, request, render_template, jsonify, session, redirect, url_for, send_from_directory, abort
import base64
from requests import get
from flask import send_from_directory
from flask import Response, url_for
from flask_dance.contrib.github import make_github_blueprint, github
import db as db
import redis
import time
import base64
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from random import randint
import datetime

app = Flask(__name__)
app.secret_key = 'uernverovnri'

UPLOAD_FOLDER = 'app/static/uploads'
PROFILE_FOLDER = 'app/static/uploads/users_profile_images'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

db.create_tables()

admins = ['Ilyas687']
# docker-compose up --build

github_blueprint = make_github_blueprint(
    client_id="Ov23li8YDj0jQSUcAF0L",
    client_secret="0deb34bd7c10408df4c196eed16f7393f29fc6e7"
)
app.register_blueprint(github_blueprint, url_prefix="/")



@app.route('/')
def sight_login():
    session["post"] = {}

    return render_template('login.html')

@app.route('/register/', methods=['POST'])
def register():
    data = request.get_json()
    nickname = data.get('nickname')
    email = data.get('email')
    password = data.get('password')
        
    user_info = db.select_user(email)

    if not user_info:
        # Данные для подключения
        smtp_server = "smtp.yandex.ru"
        smtp_port = 465  # или 587 для TLS
        sender_email = "gogoose247@yandex.ru"  # Ваш email на Яндексе
        sender_password = "wjwxlrdqjotosnrr"   # Ваш пароль или пароль от приложения
        recipient_email = email # Email получателя

        
        text = randint(100000, 999999)
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = recipient_email
        message["Subject"] = "Код подтверждения"

        db.add_user(nickname, email, password, text)
        
        # Тело письма
        body = f"Введите на сайте данный код: {text}"
        message.attach(MIMEText(body, "plain"))

        
        session["user"] = [email, nickname]

        # Подключение к серверу и отправка письма
        try:
            with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
                server.login(sender_email, sender_password)
                server.sendmail(sender_email, recipient_email, message.as_string())
                return jsonify({'status': 'OK'})
        except Exception as e:
            return jsonify({'status': 'error'})
    else:
        return jsonify({'status': 'registered'})


@app.route('/login/', methods=['GET', 'POST'])
def submit1():
    if request.method == 'POST':
        email = request.form.get('email3')
        password = request.form.get('password1')

        # cur.execute(' SELECT email, password, nickname FROM user_info WHERE email = ?', [email])
        # result = cur.fetchone()
        
        user_info = db.select_user(email)

        if not user_info:
            return render_template('login_error.html')
        elif email == user_info[0] and password == user_info[1]:

            session["user"] = [email, user_info[2]]
            return render_template('index.html', email=user_info[0])
        
        elif email == user_info[0] and password != user_info[1]:
            return render_template('login_error.html')
    else:
        if session["user"]:
            return render_template('index.html', email=session["user"][0])
        
        return render_template('index.html', email=None)

@app.route("/sight/", methods=['POST'])
def subm():
    email = request.form.get('email1')

    user_info = db.find_user(email)
    
    right_code = user_info[4]
    code = request.form.get('code')

    if int(code) == right_code:
        return render_template('index.html')
    
    return render_template('login_error.html')




@app.route("/make-post/")
def make_post():
    return render_template('make-post.html', button='Выложить')

@app.route("/edit-post/", methods=['POST'])
def change_post():
    title = request.form.get('title')
    text = request.form.get('text')

    session["post"] = {
        "email": session["user"][0],
        "title": title,
        "text": text
    }

    return render_template('make-post.html', button='Изменить')

@app.route('/post-check/', methods=['POST'])
def check_post():
    try:
        data = request.get_json()
        action = data.get('action')
        
        post = {}
        if not session["post"]:
            return jsonify({'status': 'None'})
        
        images = db.get_imgs(session['post']['email'], session['post']['title'])

        if action == 'Выложить':
            status = 'upload'
        elif action == 'Изменить':
            status = 'change'
            post = {"title": session['post']['title'], "text": session['post']['text'], "imgs": images}


        return jsonify({'status': status, "post": post})
    except Exception as e:
        return jsonify({'status': e})




@app.route('/add-post/', methods=['POST'])
def add_post():
    try:
        # Получаем список всех файлов
        files = request.files.getlist('images[]')

        if not files:
            return jsonify({"status": "error", "error": "Файлы не найдены"}), 400

        saved_files = []

        file_number = db.get_user_images_number(session["user"][0])

        for file in files:
            if file.filename == '':
                continue  # пропускаем пустые файлы
            filepath = os.path.join(UPLOAD_FOLDER, f'{session["user"][0]}_{str(file_number)}.png')
            file.save(filepath)
            saved_files.append(f'{session["user"][0]}_{str(file_number)}.png')
            file_number += 1

        db.update_images_number(session["user"][0], file_number)


        title = request.form.get('post_title')
        text = request.form.get('post_text')
        
        email = session["user"][0]
        nickname = session['user'][1]

        is_exists = db.add_post(title, text, {"imgs": saved_files}, nickname, email)


        if not saved_files:
            return jsonify({"status": "error", "error": "Нет выбранных файлов"}), 400
        
        if is_exists:
            return({'status': 'already_exists'})

        return jsonify({"status": "OK"})
    except Exception as e:
        return jsonify({"status": e})
    


@app.route('/show_posts/', methods=['POST'])
def show_posts():
    try:
        posts_info = db.get_posts(session["user"][0])

        posts = posts_info[0]

        session["posts"] = posts_info[1]

        return jsonify({"status": "OK", "posts": posts})
    except Exception as e:
        return jsonify({"status": e})

@app.route('/increase_likes/', methods=['POST'])
def likes_incr():
    try:
        data = request.get_json()
        email = data.get('email')
        title = data.get('title')
        sign = data.get('sign')

        db.increase_likes(email, title, sign, session['user'][0])

        return jsonify({"status": "OK"})
    except Exception as e:
        return jsonify({"status": e})

@app.route('/get_other_posts/', methods=['POST'])
def get_another():
    try:
        posts_info = db.get_posts(session["user"][0])

        posts = posts_info[0]

        session["posts"] = posts_info[1]

        return jsonify({"status": "OK", "posts": posts})
    except Exception as e:
        return jsonify({"status": e})
    
@app.route('/subs/')
def subscribed():
    return render_template('subs.html')

@app.route('/show_liked_posts/', methods=['POST'])
def show_liked_posts():
    try:
        posts_info = db.get_liked_posts(session["user"][0])

        posts = posts_info[0]

        return jsonify({"status": "OK", "posts": posts})
    except Exception as e:
        return jsonify({"status": e})
    
@app.route('/account/')
def acc():
    return render_template('account.html')

@app.route('/get_profile/', methods=['POST'])
def get_profile():
    try:
        user_info = {}

        user_info["posts"] = db.get_posts_by_email(session["user"][0])
        user_info["nickname"] = session["user"][1]

        posts = db.get_user_posts(session["user"][0])

        return jsonify({"status": "OK", "user_info": user_info, "posts": posts[0]})
    except Exception as e:
        return jsonify({"status": e})
    

@app.route('/delete_post/', methods=['POST'])
def deleting():
    try:
        data = request.get_json()
        title = data.get('title')

        email = session["user"][0]

        db.delete_post(email, title)

        return jsonify({'status': 'OK'})
    except Exception as e:
        return jsonify({'status': e})
    

@app.route('/change-post/', methods=['POST'])
def changing():
    try:
        images_number = request.form.get('post_images_n')
        
        files = request.files.getlist('images[]')

        if files:
            saved_files = []

            file_number = db.get_user_images_number(session["user"][0])

            for file in files:
                if file.filename == '':
                    continue  # пропускаем пустые файлы
                filepath = os.path.join(UPLOAD_FOLDER, f'{session["user"][0]}.png')
                file.save(filepath)
                saved_files.append(f'{session["user"][0]}_{str(file_number)}.png')
                file_number += 1

            db.update_images_number(session["user"][0], file_number)


            title = request.form.get('post_title')
            text = request.form.get('post_text')
            
            email = session["user"][0]

            is_exists = db.change_post(session['post']['title'], title, text, saved_files, email)
            
            if is_exists:
                return({'status': 'already_exists'})

            session['post'] = {
                "email": email,
                "title": title,
                "text": text
            }

            return jsonify({"status": "OK"})

        elif not files and int(images_number) > 0:
            title = request.form.get('post_title')
            text = request.form.get('post_text')
            
            email = session["user"][0]

            saved_files = []

            is_exists = db.change_post(session['post']['title'], title, text, saved_files, email)
            
            if is_exists:
                return({'status': 'already_exists'})

            session['post'] = {
                "email": email,
                "title": title,
                "text": text
            }

            return jsonify({"status": "OK"})
        
        else:
            return({'status': 'Выберите изображения'})
    except Exception as e:
        return jsonify({'status': e})

@app.route('/change_profile_img/', methods=['POST'])
def change_profileimg():
    try:
        files = request.files.getlist('images[]')

        for file in files:
            if file.filename == '':
                continue  # пропускаем пустые файлы
            filepath = os.path.join('app/static/uploads/users_profile_images', f'{session["user"][0]}.png')
            file.save(filepath)
            saved_file = f'{session["user"][0]}.png'
            db.set_profile_img(session['user'][0], saved_file)

        return jsonify({'status': 'OK', 'filename': saved_file})
    except Exception as e:
        return jsonify({'status': e})
    
@app.route('/check_profile_img/', methods=['POST'])
def check_profile_img():
    try:
        profile_img = db.get_profile_img(session['user'][0])

        return jsonify({'status': 'OK', 'profile_img': profile_img})
    except Exception as e:
        return jsonify({'status': e})

    
#  Обработки ошибок
        
@app.errorhandler(404)
def not_found(error):
    return render_template('error_404.html'), 404

@app.errorhandler(403)
def forbidden(error):
    return render_template('error_403.html'), 403

@app.errorhandler(500)
def forbidden(error):
    return render_template('error_500.html'), 500


# Для WebMaster

@app.route('/robots.txt')
def robots_txt():
    return send_from_directory(app.static_folder, 'robots.txt')

@app.route('/sitemap.xml')
def sitemap():
    return send_from_directory(app.static_folder, 'sitemap.xml')


app.run(host='0.0.0.0', port=4996, debug=True)

# Redis = redis.Redis(host='localhost', port=6379, decode_responses=True)

    # Redis.sadd("test: hello", str(test))
    # item = Redis.smembers("test: hello")



# '2025-09-07 12:00:00'
# VALUES ('{ "customer": "John Doe", "items": {"product": "Beer","qty": 3}}');



# https://codepen.io/vzkagyhr-the-scripter/pen/KwdOEyB?editors=1000