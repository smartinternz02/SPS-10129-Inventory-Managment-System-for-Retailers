from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
from sendemail import sendmail

app = Flask(__name__)
  
app.secret_key = 'a'

  
app.config['MYSQL_HOST'] = 'remotemysql.com'
app.config['MYSQL_USER'] = 'NZSi4Ojpfv'
app.config['MYSQL_PASSWORD'] = '8CJOAzNpsf'
app.config['MYSQL_DB'] = 'NZSi4Ojpfv'
mysql = MySQL(app)


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/login',methods =['GET', 'POST'])
def login():
    global userid
    msg = ''
    if request.method == 'POST' :
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM users WHERE username = % s AND password = % s', (username, password ),)
        account = cursor.fetchone()
        print (account)
        if account:
            session['loggedin'] = True
            session['id'] = account[0]
            userid=  account[0]
            session['username'] = account[1]
            session['email'] = account[2]
            msg = 'Logged in successfully !'
            
            msg = 'Logged in successfully !'
            return render_template('product.html', msg = msg)
        else:
            msg = 'Incorrect username / password !'
    elif request.method == 'GET' :
        msg = 'Enter the details'
    return render_template('login.html', msg = msg)


@app.route('/register', methods =['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' :
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        

        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM users WHERE username = % s', (username, ))
        account = cursor.fetchone()
        print(account)
        if account:
            msg = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'name must contain only characters and numbers !'
        else:
            msg = 'Registered successfully'
            cursor.execute('INSERT INTO users VALUES (NULL, % s, % s, % s)', (username, email,password))
            mysql.connection.commit()
            return render_template('login.html', msg = msg)
    elif request.method == 'GET':
        msg = 'Please fill out the form !'
    return render_template('register.html', msg = msg)



@app.route('/logout')
def logout():
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   session.pop('email',None)
   return render_template('home.html')

@app.route('/product')
def product():
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM product')
    record = cursor.fetchall()
    if cursor.rowcount == 0:
        msg="Add Products to view"
        return render_template('product.html',msg =msg)
    else:
        return render_template('product.html',record =record)  

@app.route('/add',methods =['GET','POST'])
def add():
    if request.method == 'POST' :
        prod_name = request.form['prod_name']
        prod_qty = int(request.form['prod_qty'])
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM product WHERE prod_name = % s', (prod_name, ))
        record = cursor.fetchone()
        print (record)
        if record:
            prod_qty=prod_qty+int(record[2])
            cursor.execute('UPDATE product SET prod_qty = % s WHERE prod_name = % s', ( int(prod_qty), prod_name))
            mysql.connection.commit()
            cursor = mysql.connection.cursor()
            cursor.execute('SELECT * FROM product')
            record = cursor.fetchall()
            return render_template('product.html',record=record)
        else:
            cursor.execute('INSERT INTO product VALUES (NULL, % s, % s)', (prod_name, int(prod_qty)))
            mysql.connection.commit()
            cursor = mysql.connection.cursor()
            cursor.execute('SELECT * FROM product')
            record = cursor.fetchall()
            return render_template('product.html',record=record)
    return render_template('add.html')

@app.route('/sell',methods =['GET','POST'])
def sell():
    if request.method == 'POST' :
        prod_name = request.form['prod_name']
        prod_qty = int(request.form['prod_qty'])
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM product WHERE prod_name = % s', (prod_name, ))
        record = cursor.fetchone()
        print (record) 
        if record:
            if((int(record[2])-prod_qty)<=0):
                if(int(record[2])==0):
                    TEXT = "Hello "+session['username'] + ",\n\n "+ " The "+ prod_name + " is out of stock." 
                    msg ="The product is out of stock."
                else :
                    remaining = record[2]
                    TEXT = "Hello "+session['username'] + ",\n\n "+ " The "+ prod_name +" is having only "+str(remaining)+" quantity so arrange it quickly. "  
                    msg = "We have only "+ str(record[2]) + " quantity of "+ prod_name +" do u want."
                sendmail(session['email'],TEXT)
                cursor = mysql.connection.cursor()
                cursor.execute('SELECT * FROM product')
                record = cursor.fetchall()
                return render_template('product.html',msg =msg,record=record)
            else:
                prod_qty=int(record[2])-prod_qty
                cursor.execute('UPDATE product SET prod_qty = % s WHERE prod_name = % s', ( int(prod_qty), prod_name))
                mysql.connection.commit()
                cursor = mysql.connection.cursor()
                cursor.execute('SELECT * FROM product')
                record = cursor.fetchall()
                return render_template('product.html',record=record)
        else:
            msg="There is no such item"
            cursor = mysql.connection.cursor()
            cursor.execute('SELECT * FROM product')
            record = cursor.fetchall()
            return render_template('product.html',msg =msg,record=record)
    return render_template('sell.html')


        
if __name__ == '__main__':
    app.run(host='0.0.0.0',debug = True,port = 8080)