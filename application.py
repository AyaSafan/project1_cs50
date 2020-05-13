import os
import psycopg2
import requests
import json
from functools import wraps
from flask import abort, jsonify
from functools import wraps
from flask import Flask,g, render_template, request, session, redirect, url_for
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

def login_required(test):
    @wraps(test)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return test(*args, **kwargs)
        else:
            
            return redirect(url_for('index'))
    return wrap


os.environ['DATABASE_URL'] = "postgres://dmeodokjkwgohf:debdfada34c16ca25a7331e3cced7a5b50720e93965e123af6bc33047dfb4bdb@ec2-3-229-210-93.compute-1.amazonaws.com:5432/daegfd1u3frisi"
DATABASE_URL = os.environ['DATABASE_URL']

conn = psycopg2.connect(DATABASE_URL, sslmode='require')
app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    return render_template("intro.html")

@app.route("/Login", methods=["GET", "POST"]) 
def Login():
    return render_template("LogIn.html")
@app.route("/Signup", methods=["GET", "POST"]) 
def Signup():
    return render_template("SignUp.html")

@app.route("/SignUp", methods=["GET", "POST"]) 
def SignUp():
    if request.method == "POST" or request.method == "GET" :
        session["username"]= request.form.get("username")
        session["password"]= request.form.get("password")
        session["passagain"]=request.form.get("passagain")
         
        if session["username"] != None:
            if db.execute("SELECT * FROM users WHERE username = :username", {"username": session["username"]}).rowcount == 0:
                if session["password"]==session["passagain"]:
                    if len(session["password"]) > 5:
                        db.execute("INSERT INTO users (username, password) VALUES (:username, :password)",
                                {"username": session["username"], "password": session["password"]})
                        db.commit()
                        return redirect(url_for('Login'))
                    else:
                        txt="Error! Password must be 5 characters at least."
                        return render_template("SignUp.html" , txt=txt)

                else:
                    txt="Error! Passwords don't match."
                    return render_template("SignUp.html" , txt=txt)
            else: 
                txt="Error! Username Taken."
                return render_template("SignUp.html" , txt=txt)       
        else:
            txt="Error! Provide a Username."
            return render_template("SignUp.html" , txt=txt)

    

@app.route("/Search" , methods=["GET", "POST"]) 

def Search():
    if request.method == "POST":
        username=session["username"]= request.form.get("username")
        session["password"]= request.form.get("password")
        session["books"]=[] 
        
        message=""   
        if db.execute("SELECT * FROM users WHERE username = :username AND password= :password", {"username": session["username"], "password": session["password"]}).rowcount == 0:
            return render_template("LogIn.html", txt="Error! Username and Password don't match.")
        session['logged_in']=True
        session['username'] = username
        return render_template("Search.html", username=session["username"], books=session['books'], message=message)
    if request.method == "GET":
        session["books"]=[]        
        message="" 
        username=session['username']
        if username != None:
            session['logged_in']=True
            return render_template("Search.html", username=username, books=session['books'], message=message)
        
    

@app.route("/Search/<string:username>" , methods=["GET", "POST"]) 
@login_required
def Searched(username):
    if request.method == "POST" or request.method == "GET" :
        session["txtSearch"]= request.form.get("txtSearch")
        session["books"]=[] 
        message=""
        if session["txtSearch"] != None:
            data=db.execute("SELECT * FROM books WHERE author iLIKE '%"+session["txtSearch"]+"%' OR title iLIKE '%"+session["txtSearch"]+"%' OR isbn iLIKE '%"+session["txtSearch"]+"%' ORDER BY year ASC;").fetchall()
            for x in data:
                session['books'].append(x)
                message=""
            if len(session["books"])==0:
                message=('Nothing found. Try again.')
   
        return render_template("Search.html",username=username, books=session['books'], message=message)

    return render_template("intro.html")

@app.route("/MyBooks/<string:username>" , methods=["GET", "POST"]) 
@login_required
def MyBooks(username):
    if request.method == "POST" or request.method == "GET" :
        session["mybooks"]=[]
        session["txtSearch"]= request.form.get("txtSearch")
        session["books"]=[] 
        message=""
        isbns=db.execute("SELECT * FROM reviews WHERE username = :username",{"username":username}).fetchall() 
        for isbn in isbns:
            book= db.execute("SELECT * FROM books WHERE  isbn = :isbn", {"isbn": isbn.isbn}).fetchone()
            session['mybooks'].append(book)    
        if session["txtSearch"] != None:
            for isbn in isbns:
                data=db.execute("SELECT * FROM books WHERE isbn = :isbn AND author iLIKE '%"+session["txtSearch"]+"%' OR isbn = :isbn AND title iLIKE '%"+session["txtSearch"]+"%' OR isbn = :isbn AND isbn iLIKE '%"+session["txtSearch"]+"%' ORDER BY year ASC ", {"isbn": isbn.isbn}).fetchone()
                if data !=None:                
                    session['books'].append(data)
                    message=""
                if len(session["books"])==0:
                    message=('Nothing found. Try again.')
   
        return render_template("mybooks.html",username=username, mybooks=session['mybooks'], books=session['books'], message=message)
    return render_template("intro.html")

    

@app.route("/<string:username>/isbn/<string:book_isbn>" , methods=["GET", "POST"])
@login_required
def BookPage(username, book_isbn):
    """Lists details about a single book."""
    if request.method == "POST" or request.method == "GET" :
        # Make sure book exists.
        book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": book_isbn}).fetchone()
        if book is None:
            return render_template("BookPage.html", message="No such book.")

        # Get book details.
        res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "TdelTd0m8Kjz8s2jZya3A", "isbns": book_isbn})
        average_rating=res.json()['books'][0]['average_rating']
        work_ratings_count=res.json()['books'][0]['work_ratings_count']
        reviews_count=res.json()['books'][0]['reviews_count']

        session["rating"]= request.form.get("rating")
        session["review"]= request.form.get("review")
        
        user = db.execute("SELECT * FROM reviews WHERE username = :username AND isbn= :isbn", {"username": username, "isbn": book_isbn}).fetchone()
        session["reviews"]=[]
        error=""
        my_rate= 0
        #new user review or rating
        if user == None:
            if session["rating"]== None:
                        if session["review"]== None:
                            error=""
                        else:
                            db.execute("INSERT INTO reviews (isbn, review, username) VALUES (:isbn, :review, :username)",
                                    {"isbn": book_isbn, "review": str(session["review"]), "username": username})
                            db.commit()
            else:
                db.execute("INSERT INTO reviews (isbn, rating, username) VALUES (:isbn, :rating, :username)",
                    {"isbn": book_isbn, "rating": str(session["rating"]), "username": username})
                db.commit()
        else: #Update rate and error review
            if session["rating"]== None:
                        if session["review"]== None:
                            error=""
                        else:
                            re = db.execute("SELECT review FROM reviews WHERE username = :username AND isbn= :isbn", {"username": username, "isbn": book_isbn}).fetchone()
                            if re.review == None:
                                db.execute("UPDATE reviews SET review = :review WHERE username = :username AND isbn= :isbn", {"username": username, "isbn": book_isbn, "review":str(session["review"])})
                                db.commit()
                            else:
                                error="You already added a review. You can Edit Review."
            else:
                db.execute("UPDATE reviews SET rating = :rating WHERE username = :username AND isbn= :isbn", {"username": username, "isbn": book_isbn, "rating":int(session["rating"])})
                db.commit()
        #get my rate
        user = db.execute("SELECT * FROM reviews WHERE username = :username AND isbn= :isbn", {"username": username, "isbn": book_isbn}).fetchone()
        my_rate= 0
        if user != None:                    
            rate = db.execute("SELECT rating FROM reviews WHERE username = :username AND isbn= :isbn", {"username": username, "isbn": book_isbn}).fetchone()
            if rate.rating is not None:           
                my_rate= int(rate.rating)
                
        stars=[1,2,3,4,5]
        #get my statistics
        reviews=db.execute("SELECT * FROM reviews WHERE isbn = :isbn",{"isbn":book_isbn}).fetchall() 
        for review in reviews:
            session['reviews'].append(review)
        avg=db.execute("SELECT AVG(rating) FROM reviews WHERE isbn = :isbn AND rating IS NOT NULL" ,{"isbn":book_isbn}).fetchall()
        if avg[0][0] != None:
            avg_r=round(avg[0][0],2)
        else:
            avg_r=0
        rate_count=db.execute("SELECT rating , COUNT(*) FROM reviews WHERE isbn = :isbn AND rating IS NOT NULL GROUP BY rating" ,{"isbn":book_isbn}).fetchall()
        review_count=db.execute("SELECT review , COUNT(*) FROM reviews WHERE isbn = :isbn AND review IS NOT NULL GROUP BY review" ,{"isbn":book_isbn}).fetchall()
        my_review = db.execute("SELECT review FROM reviews WHERE username = :username AND isbn= :isbn", {"username": username, "isbn": book_isbn}).fetchone()
                         
         
        return render_template("BookPage.html",username=username, book=book, average_rating=average_rating,work_ratings_count=work_ratings_count, reviews_count=reviews_count, error=error, rating=my_rate, stars=stars, reviews=session['reviews'], avg=avg_r, rate_count=len(rate_count), review_count=len(review_count), my_review=my_review)
    return render_template("intro.html")


@app.route("/<string:username>//Edit/isbn/<string:book_isbn>" , methods=["GET", "POST"])
@login_required
def Edit(username, book_isbn):
    """Lists details about a single book."""
    if request.method == "POST" or request.method == "GET" :
        book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": book_isbn}).fetchone()
        user = db.execute("SELECT * FROM reviews WHERE username = :username AND isbn= :isbn", {"username": username, "isbn": book_isbn}).fetchone()
        review=""
        error=""        
        if user == None:
            #"You don't have a review. Post Review instead."
            return redirect(url_for('BookPage' ,username=username, book_isbn=book.isbn) , code=307)
        else:
            
            if user.review == None:
                #"You don't have a review. Post Review instead."
                return redirect(url_for('BookPage',username=username, book_isbn=book.isbn) , code=307)
            else:
                review = user.review
                    
                            

        return render_template("Edit.html",username=username, book=book, review=review, error=error)
    return render_template("intro.html")

@app.route("/<string:username>/InEdit/isbn/<string:book_isbn>" , methods=["GET", "POST"])
@login_required
def InEdit(username, book_isbn):
    
    if request.method == "POST" or request.method == "GET" :
        book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": book_isbn}).fetchone()
        session["edit_review"]= request.form.get("edit_review")
        error=""
        if  session["edit_review"] == "":
            error="Your Review is empty. Delete instead"
            return render_template("Edit.html",username=username, book=book, textarea=session["reviews"], error=error)
        else:
            db.execute("UPDATE reviews SET review = :review WHERE username = :username AND isbn= :isbn", {"username": username, "isbn": book_isbn, "review":str(session["edit_review"])})
            db.commit()
            return redirect(url_for('BookPage',username=username, book_isbn=book_isbn) , code=307)   

    return render_template("intro.html")

@app.route("/<string:username>/Delete/isbn/<string:book_isbn>" , methods=["GET", "POST"])
@login_required
def Delete(username, book_isbn):
    
    book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": book_isbn}).fetchone()
    user = db.execute("SELECT * FROM reviews WHERE username = :username AND isbn= :isbn", {"username": username, "isbn": book_isbn}).fetchone()
    session["review"]=[]
    error=""        
    if user == None:
        return redirect(url_for('BookPage' ,username=username, book_isbn=book.isbn) , code=307)
    else:
        re = db.execute("SELECT review FROM reviews WHERE username = :username AND isbn= :isbn", {"username": username, "isbn": book_isbn}).fetchone()
        if re.review == None:
            return redirect(url_for('BookPage',username=username, book_isbn=book.isbn) , code=307)
        else:
            db.execute("UPDATE reviews SET review = :review WHERE username = :username AND isbn= :isbn", {"username": username, "isbn": book_isbn, "review":None})
            db.commit()
            return redirect(url_for('BookPage',username=username, book_isbn=book_isbn) , code=307)   

    return render_template("intro.html")

@app.route("/logout" , methods=["GET", "POST"])
def logout():
    session.pop('logged_in', None)
    session.clear()
    
    return redirect(url_for('index'))

@app.errorhandler(404)
def resource_not_found(e):
    return jsonify(error=str(e)), 404

@app.route("/api/<string:book_isbn>", methods=["GET"])
@login_required
def api(book_isbn):
    book=db.execute("SELECT * FROM books WHERE isbn = :isbn",{"isbn": book_isbn}).fetchone()
    session['reviews']=[]
    if book==None:
        abort(404, description="isbn not found")

#get my statistics
    reviews=db.execute("SELECT * FROM reviews WHERE isbn = :isbn",{"isbn": book_isbn}).fetchall() 
    for review in reviews:
        session['reviews'].append(review)
    avg=db.execute("SELECT AVG(rating) FROM reviews WHERE isbn = :isbn AND rating IS NOT NULL" ,{"isbn": book_isbn}).fetchall()
    if avg[0][0] != None:
        avg_r=round(avg[0][0],2)
    else:
        avg_r=0
    avg_r=str(avg_r)
    rate_count=len(db.execute("SELECT rating , COUNT(*) FROM reviews WHERE isbn = :isbn AND rating IS NOT NULL GROUP BY rating" ,{"isbn":book_isbn}).fetchall())
    review_count=len(db.execute("SELECT review , COUNT(*) FROM reviews WHERE isbn = :isbn AND review IS NOT NULL GROUP BY review" ,{"isbn":book_isbn}).fetchall())
                         
    
    return jsonify({
        "title": book.title,
        "author": book.author,
        "year": book.year,
        "isbn": book_isbn,
        "review_count":review_count,
        "average_rating": avg_r,
        "rate_count": rate_count
        })
    

    
 