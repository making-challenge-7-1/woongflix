from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from pymongo import MongoClient

import random

app = Flask(__name__)

client = MongoClient("mongodb://test:test@54.180.140.177", 27017)
db = client.dbMovies

app.secret_key = "WFLIX"


# main page view
@app.route("/")
def init():
    return render_template("index.html")


# register page view(회원가입)
@app.route("/register")
def register():
    return render_template("register.html")


# login page view(로그인)
@app.route("/login")
def login():
    return render_template("login.html")


# all movie list view
@app.route("/movies", methods=["GET"])
def movie_list():
    return render_template("movielist.html")


# detail page view
@app.route("/detail", methods=["GET"])
def detail():
    return render_template("detail.html")


# 회원가입 진행(db에 저장)
@app.route("/sign_up", methods=["POST"])
def sign_up():
    username_receive = request.form["username_give"]
    password_receive = request.form["password_give"]

    doc = {"username": username_receive, "password": password_receive}
    db.users.insert_one(doc)

    return jsonify({"msg": "저장이 완료되었습니다"})


# id 중복 검사
@app.route("/sign_up/id_check", methods=["POST"])
def id_check():
    username_receive = request.form["username_give"]
    exists = bool(db.users.find_one({"username": username_receive}))
    return jsonify({"result": "success", "exists": exists})


# 로그인
@app.route("/sign_in", methods=["POST"])
def sign_in():

    username_receive = request.form["username_give"]
    password_receive = request.form["password_give"]

    result = db.users.find_one(
        {"username": username_receive, "password": password_receive}
    )

    if result is not None:
        session["username"] = result.get("username")

        return jsonify(
            {"result": "success", "msg": "로그인 성공", "username": username_receive}
        )  # username = sessionstorage에 저장 될 예정
    # 찾지 못하면
    else:
        return jsonify({"result": "fail", "msg": "아이디/비밀번호가 일치하지 않습니다."})


# 로그아웃
@app.route("/logout", methods=["GET"])
def logout():
    session.pop("username", None)
    return redirect(url_for("init"))


# top 4 movie get 기분별 하나씩 랜덤하게 가져오기
@app.route("/recommend/top", methods=["GET"])
def get_recommend_top():
    recommend_top = []

    try:
        happy_list = list(
            db.movieList.find({"genre": "신남"}, {"_id": False}).sort("score", -1)
        )

        happy_recommend_list = []

        for movie in happy_list:
            score = movie["score"]
            score = float(score)
            if score > 8:
                happy_recommend_list.append(movie)

        today_happy = random.sample(happy_recommend_list, 1)[0]
        happy_title = today_happy["title"]
        happy_img = today_happy["img_url"]
        recommend_top.append(happy_title)
        recommend_top.append(happy_img)

        angry_list = list(
            db.movieList.find({"genre": "화남"}, {"_id": False}).sort("score", -1)
        )

        angry_recommend_list = []

        for movie in angry_list:
            score = movie["score"]
            score = float(score)
            if score > 8:
                angry_recommend_list.append(movie)

        today_angry = random.sample(angry_recommend_list, 1)[0]
        angry_title = today_angry["title"]
        angry_img = today_angry["img_url"]
        recommend_top.append(angry_title)
        recommend_top.append(angry_img)

        sad_list = list(db.movieList.find({"genre": "우울"}, {"_id": False}).sort(
                "score", -1
            ))

        sad_recommend_list = []

        for movie in sad_list:
            score = movie["score"]
            score = float(score)
            if score > 8:
                sad_recommend_list.append(movie)

        today_sad = random.sample(sad_recommend_list, 1)[0]
        sad_title = today_sad["title"]
        sad_img = today_sad["img_url"]
        recommend_top.append(sad_title)
        recommend_top.append(sad_img)

        move_list = list(db.movieList.find({"genre": "떠남"}, {"_id": False}).sort(
                "score", -1
            ))

        move_recommend_list = []

        for movie in move_list:
            score = movie["score"]
            score = float(score)
            if score > 8:
                move_recommend_list.append(movie)

        today_move = random.sample(move_recommend_list, 1)[0]
        move_title = today_move["title"]
        move_img = today_move["img_url"]
        recommend_top.append(move_title)
        recommend_top.append(move_img)

    except Exception:
        return jsonify({"ERROR: fail to get top items"})

    return jsonify({"recommendTop": recommend_top})


# get all movie by genre
@app.route("/recommend/list", methods=["POST"])
def get_recommend_list():
    try:
        genre_receive = request.form["genre_name"]

        movie_list = list(
            db.movieList.find({"genre": genre_receive}, {"_id": False}).sort(
                "score", -1
            )
        )
        movie_list_sort = []
        for movie in movie_list:
            score = movie["score"]
            score = float(score)
            if score > 5:
                movie_list_sort.append(movie)

    except Exception:

        return jsonify({"error"})

    return jsonify({"movie_list": movie_list_sort})


# get all genre movie list
@app.route("/find/all/score", methods=["GET"])
def find_all_movie_score():
    try:
        movie_list_all = list(db.movieList.find({}, {"_id": False}).sort("score", -1))

    except Exception:

        return jsonify({"error to find movies"})

    return jsonify({"movie_list": movie_list_all})


@app.route("/find/all/abc", methods=["GET"])
def find_all_movie_abc():
    try:
        movie_list_all = list(db.movieList.find({}, {"_id": False}).sort("title", 1))

    except Exception:

        return jsonify({"error to find movies"})

    return jsonify({"movie_list": movie_list_all})


@app.route("/find/movie", methods=["POST"])
def find_movie_by_title():
    try:
        title_receive = request.form["title_give"]
        movie_list_all = list(
            db.movieList.find(
                {"title": {"$regex": title_receive}}, {"_id": False}
            ).sort("title", 1)
        )

    except Exception:

        return jsonify({"error to find movies"})

    return jsonify({"movie_list": movie_list_all})


# get movie detail
@app.route("/find", methods=["POST"])
def find_movie_detail():
    try:
        title_receive = request.form["title_give"]
        target = db.movieList.find_one({"title": title_receive}, {"_id": False})

    except Exception as e:
        return {"message": "failed to search"}, 401

    return jsonify({"movie_data": target})


# comment 관련 code

## comment 불러오기
@app.route("/comments", methods=["POST"])
def get_comments():
    title_receive = request.form["title_give"]

    # title로 comment 조회
    comments = list(db.comment.find({"title": title_receive}, {"_id": False}))
    return jsonify({"target_comments": comments})


## comment 쓰기
@app.route("/comments/update", methods=["POST"])
def update_comments():

    title_receive = request.form["title_give"]
    ID_receive = request.form["ID_give"]
    comment_receive = request.form["comment_give"]

    if ID_receive == "":  # ID를 찾아 올 수 없는 경우
        session.pop("username", None)
        return jsonify({"msg": "로그인을 다시 해주세요"})
    elif comment_receive == "":  # comment가 없는 경우
        return jsonify({"msg": "내용을 작성해주세요"})
    else:
        doc = {
            "title": title_receive,
            "ID": ID_receive,
            "comment": comment_receive,
        }  # title, ID, comment로 저장
        db.comment.insert_one(doc)
        return jsonify({"msg": "등록 완료"})


## comment 지우기
@app.route("/comments/delete", methods=["POST"])
def delete_comment():

    title_receive = request.form["title_give"]
    ID_receive = request.form["ID_give"]
    doc = {
        "title": title_receive,
        "ID": ID_receive,
    }
    db.comment.delete_one(doc)

    return jsonify({"msg": "삭제 완료"})


if __name__ == "__main__":
    app.run("0.0.0.0", port=5000, debug=True)
