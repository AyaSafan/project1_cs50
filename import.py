import os
import csv
import psycopg2
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

os.environ['DATABASE_URL'] = "postgres://dmeodokjkwgohf:debdfada34c16ca25a7331e3cced7a5b50720e93965e123af6bc33047dfb4bdb@ec2-3-229-210-93.compute-1.amazonaws.com:5432/daegfd1u3frisi"
DATABASE_URL = os.environ['DATABASE_URL']
conn = psycopg2.connect(DATABASE_URL, sslmode='require')

engine= create_engine(os.getenv("DATABASE_URL"))
db =scoped_session(sessionmaker(bind=engine))

def main():
    db.execute("CREATE TABLE users (id SERIAL PRIMARY KEY, username VARCHAR NOT NULL, password VARCHAR NOT NULL)")

    db.execute("CREATE TABLE reviews (isbn VARCHAR NOT NULL,review VARCHAR , rating INTEGER ,username VARCHAR NOT NULL)")
    db.execute("CREATE TABLE books (isbn VARCHAR PRIMARY KEY,title VARCHAR NOT NULL,author VARCHAR NOT NULL,year VARCHAR NOT NULL)")
    f=open("books.csv")
    reader =csv.reader(f)
    for isbn,title,author,year in reader:
        if year != "year":        
            db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:a,:b,:c,:d)",{"a":isbn,"b":title,"c":author,"d":year})
        
    print("done")            
    db.commit()    







if __name__ == "__main__":
    main()