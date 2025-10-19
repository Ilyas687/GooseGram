import os
import psycopg2
import math
from datetime import datetime
import json
import math


PROFILE_FOLDER = 'app/static/uploads/users_profile_images'


# дата_1_str = "2024-01-01 10:00:00"
# дата_2_str = "2024-01-01 12:30:00"
# формат = "%Y-%m-%d %H:%M:%S"

# дата_1 = datetime.strptime(дата_1_str, формат)
# дата_2 = datetime.strptime(дата_2_str, формат)

# # Вычисляем разницу между датами
# разница = дата_2 - дата_1

# # Получаем общую разницу в секундах
# общая_секунд = разница.total_seconds()

# # Получаем разницу в днях, секундах и микросекундах
# дни = разница.days
# секунды = разница.seconds

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", 5432)
DB_NAME = os.getenv("DB_NAME", "postgres")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "wqtpad57")

def get_connection():
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )

def create_tables():
    conn = get_connection()
    cur = conn.cursor()

    # cur.execute('''DROP TABLE user_info_insta''')
    # cur.execute('''DROP TABLE posts''')

    cur.execute('''CREATE TABLE IF NOT EXISTS user_info_insta (
        id SERIAL PRIMARY KEY,
        nickname VARCHAR(30),
        email VARCHAR(100),
        password VARCHAR(20),
        code NUMERIC(6),
        subs BIGINT DEFAULT 0,
        profile_img VARCHAR,
        min_rating BIGINT DEFAULT 900,
        max_rating BIGINT DEFAULT 1100,
        images_number BIGINT DEFAULT 0,
        posts_id JSONB DEFAULT '{"ids": []}'::jsonb
    )''')

    cur.execute('''CREATE TABLE IF NOT EXISTS posts (
        id SERIAL PRIMARY KEY,
        title VARCHAR(100),
        text VARCHAR,
        imgs JSONB,
        author_nickname VARCHAR(30),
        author_email VARCHAR(100),
        likes BIGINT DEFAULT 0,
        commentaries JSONB DEFAULT '{}'::jsonb,
        time TIMESTAMP,
        rating BIGINT DEFAULT 1000,
        liked_users JSONB DEFAULT '{"users": []}'::jsonb
    )''')

    conn.commit()

def find_user(email):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute('SELECT * FROM user_info_insta WHERE email = %s', [email])
    result = cur.fetchone()

    return result

def add_user(nickname, email, password, code) -> None:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute('INSERT INTO user_info_insta(nickname, email, password, code) VALUES(%s, %s, %s, %s)', [nickname, email, password, code])
    conn.commit()

def select_user(email):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute('SELECT email, password, nickname FROM user_info_insta WHERE email = %s', [email])
    return cur.fetchone()

def add_post(title, text, imgs, nickname, email) -> bool:
    conn = get_connection()
    cur = conn.cursor()

    time = datetime.now()

    cur.execute('SELECT * FROM posts WHERE author_email = %s AND title = %s', [email, title])
    is_exists = cur.fetchone()

    if is_exists:
        return True
    
    cur.execute('INSERT INTO posts (title, text, imgs, author_nickname, author_email, time) VALUES (%s, %s, %s, %s, %s, %s)', [title, text, json.dumps(imgs), nickname, email, time])
    conn.commit()

    return False

def get_user_images_number(email):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute('SELECT images_number FROM user_info_insta WHERE email = %s', [email])
    return cur.fetchone()[0]

def update_images_number(email, number) -> None:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute('UPDATE user_info_insta SET images_number = %s WHERE email = %s', [number, email])
    conn.commit()
    
def get_posts(email):
    conn = get_connection()
    cur = conn.cursor()

    posts_normalized = []
    all_posts = []

    cur.execute('SELECT min_rating, max_rating FROM user_info_insta WHERE email = %s', [email])
    minn, maxx = cur.fetchone()

    if not all_posts:
        cur.execute('SELECT * FROM posts WHERE %s <= rating AND rating <= %s', [minn, maxx])
    else:
        cur.execute('SELECT * FROM posts WHERE %s <= rating AND rating <= %s AND id NOT IN %s', [minn, maxx, tuple(all_posts)])
    posts = cur.fetchmany(10)

    for post in posts:
        all_posts.append(post[0])
        
        if email in post[10]["users"]:
            is_liked = True
        else:
            is_liked = False

        format = '%Y-%m-%d %H:%M:%S'

        dt_str = f'{post[8]}'.split('.')[0]
        
        date1 = datetime.strptime(dt_str, format)
        date2 = datetime.now()

        dates = date2 - date1

        seconds = math.floor(dates.total_seconds())
        
        if seconds < 60:
            time = f'{seconds} секунд'
        elif seconds < 3600:
            time = f'{math.floor(seconds / 60)} минут'
        elif seconds < 86400:
            time = f'{math.floor(seconds / 3600)} часов'
        elif seconds < 2678400:
            time = f'{dates.days} дней'
        elif seconds < 31536000:
            time = f'{date2.month - date1.month} месяцев'
        else:
            time = f'{date2.year - date1.year} лет'

        if os.path.exists(f'{PROFILE_FOLDER}/{post[5]}.png'):
            file_exists = True
        else:
            file_exists = False

        posts_normalized.append({"title": post[1], "text": post[2], "imgs": post[3]['imgs'], "nickname": post[4], "email": post[5], "likes": post[6], "commentaries": post[7], "time": time, "liked": is_liked, "has_profile_img": file_exists})
    
    cur.execute('SELECT posts_id FROM user_info_insta WHERE email = %s', [email])
    postss = cur.fetchone()

    for post in all_posts:
        if post not in postss[0]["ids"]:
            postss[0]["ids"].append(post)
    
    cur.execute('UPDATE user_info_insta SET posts_id = %s WHERE email = %s', [json.dumps({"ids": postss[0]["ids"]}), email])
    conn.commit()

    return [posts_normalized, postss[0]["ids"]]

def increase_likes(email, title, sign, user_email):
    conn = get_connection()
    cur = conn.cursor()
    
    if sign == '+':
        cur.execute('UPDATE posts SET likes = likes + 1 WHERE author_email = %s AND title = %s', [email, title])
        cur.execute('UPDATE posts SET rating = rating + 20 WHERE author_email = %s AND title = %s', [email, title])
        conn.commit()

        cur.execute('SELECT liked_users FROM posts WHERE author_email = %s AND title = %s', [email, title])
        jsonb = cur.fetchone()
        jsonb[0]['users'].append(user_email)

        cur.execute('''UPDATE posts SET liked_users = %s WHERE author_email = %s AND title = %s''', [json.dumps(jsonb[0]), email, title]) # Изменение liked_users формата JSONB
        conn.commit()
    elif sign == '-':
        cur.execute('UPDATE posts SET likes = likes - 1 WHERE author_email = %s AND title = %s', [email, title])
        cur.execute('UPDATE posts SET rating = rating - 20 WHERE author_email = %s AND title = %s', [email, title])
        conn.commit()

        cur.execute('SELECT liked_users FROM posts WHERE author_email = %s AND title = %s', [email, title])
        jsonb = cur.fetchone()
        jsonb[0]['users'].remove(user_email)
        

        cur.execute('''UPDATE posts SET liked_users = %s WHERE author_email = %s AND title = %s''', [json.dumps(jsonb[0]), email, title]) # Изменение liked_users формата JSONB
        conn.commit()



    
def get_liked_posts(email):
    conn = get_connection()
    cur = conn.cursor()

    posts_normalized = []

    cur.execute('''SELECT * FROM posts WHERE (liked_users -> 'users')::jsonb @> %s::jsonb''', [f'["{email}"]'])
    posts = cur.fetchall()

    is_liked = True

    for post in posts:
        format = '%Y-%m-%d %H:%M:%S'

        dt_str = f'{post[8]}'.split('.')[0]
        
        date1 = datetime.strptime(dt_str, format)
        date2 = datetime.now()

        dates = date2 - date1

        seconds = math.floor(dates.total_seconds())
        
        if seconds < 60:
            time = f'{seconds} секунд'
        elif seconds < 3600:
            time = f'{math.floor(seconds / 60)} минут'
        elif seconds < 86400:
            time = f'{math.floor(seconds / 3600)} часов'
        elif seconds < 2678400:
            time = f'{dates.days} дней'
        elif seconds < 31536000:
            time = f'{date2.month - date1.month} месяцев'
        else:
            time = f'{date2.year - date1.year} лет'

        posts_normalized.append({"title": post[1], "text": post[2], "imgs": post[3]['imgs'], "nickname": post[4], "email": post[5], "likes": post[6], "commentaries": post[7], "time": time, "liked": is_liked})

    return [posts_normalized]


def get_posts_by_email(email):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute('SELECT id FROM posts WHERE author_email = %s', [email])
    return len(cur.fetchall())

    
def get_user_posts(email):
    conn = get_connection()
    cur = conn.cursor()

    posts_normalized = []

    cur.execute('''SELECT * FROM posts WHERE author_email = %s''', [email])
    posts = cur.fetchall()

    for post in posts:
        if email in post[10]["users"]:
            is_liked = True
        else:
            is_liked = False

        format = '%Y-%m-%d %H:%M:%S'

        dt_str = f'{post[8]}'.split('.')[0]
        
        date1 = datetime.strptime(dt_str, format)
        date2 = datetime.now()

        dates = date2 - date1

        seconds = math.floor(dates.total_seconds())
        
        if seconds < 60:
            time = f'{seconds} секунд'
        elif seconds < 3600:
            time = f'{math.floor(seconds / 60)} минут'
        elif seconds < 86400:
            time = f'{math.floor(seconds / 3600)} часов'
        elif seconds < 2678400:
            time = f'{dates.days} дней'
        elif seconds < 31536000:
            time = f'{date2.month - date1.month} месяцев'
        else:
            time = f'{date2.year - date1.year} лет'

        posts_normalized.append({"title": post[1], "text": post[2], "imgs": post[3]['imgs'], "nickname": post[4], "email": post[5], "likes": post[6], "commentaries": post[7], "time": time, "liked": is_liked})

    return [posts_normalized]

def delete_post(email, title) -> None:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute('DELETE FROM posts WHERE author_email = %s AND title = %s', [email, title])
    conn.commit()

def get_imgs(email, title):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute('SELECT imgs FROM posts WHERE author_email = %s AND title = %s', [email, title])
    return cur.fetchone()[0]['imgs']

def change_post(old_title, new_title, text, imgs, email) -> bool:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute('SELECT * FROM posts WHERE author_email = %s AND title = %s', [email, new_title])
    is_exists = cur.fetchone()

    if is_exists and old_title != new_title:
        return True

    if not imgs:
        cur.execute('UPDATE posts SET title = %s, text = %s WHERE author_email = %s AND title = %s', [new_title, text, email, old_title])
    else:
        cur.execute('SELECT imgs FROM posts WHERE author_email = %s AND title = %s', [email, old_title])
        images = cur.fetchone()[0]
        
        for img in imgs:
            images['imgs'].append(img)

        cur.execute('UPDATE posts SET title = %s, text = %s, imgs = %s WHERE author_email = %s AND title = %s', [new_title, text, json.dumps(images), email, old_title])
    conn.commit()

    return False

def set_profile_img(email, filename) -> None:
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute('UPDATE user_info_insta SET profile_img = %s WHERE email = %s', [filename, email])
    conn.commit()

def get_profile_img(email):
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute('SELECT profile_img FROM user_info_insta WHERE email = %s', [email])
    img = cur.fetchone()

    if not img[0]:
        return 'None'
    else:
        return img[0]


# jsonb_set(liked_users, '{users}', %s)