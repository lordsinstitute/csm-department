from django.shortcuts import render
from django.template import RequestContext
from django.contrib import messages
import pymysql
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage
import datetime
from datetime import date
import os
from ecies.utils import generate_eth_key, generate_key
from ecies import encrypt, decrypt
import os
import json
from base64 import b64encode
from Crypto.Cipher import ChaCha20
from Crypto.Random import get_random_bytes
import timeit
from hashlib import sha256
import matplotlib.pyplot as plt
import io
import base64
import numpy as np

global username, propose, existing

#function to generate public and private keys for ECC algorithm
def ECCKeys():
    if os.path.exists("pvt.key"):
        with open("pvt.key", 'rb') as f:
            private_key = f.read()
        f.close()
        with open("pri.key", 'rb') as f:
            public_key = f.read()
        f.close()
        private_key = private_key.decode()
        public_key = public_key.decode()
    else:
        secret_key = generate_eth_key()
        private_key = secret_key.to_hex()  # hex string
        public_key = secret_key.public_key.to_hex()
        with open("pvt.key", 'wb') as f:
            f.write(private_key.encode())
        f.close()
        with open("pri.key", 'wb') as f:
            f.write(public_key.encode())
        f.close()
    return private_key, public_key

#ECC will encrypt data using plain text adn public key
def EccEncrypt(plainText, public_key):
    ecc_encrypt = encrypt(public_key, plainText)
    return ecc_encrypt

#ECC will decrypt data using private key and encrypted text
def EccDecrypt(encrypt, private_key):
    ecc_decrypt = decrypt(private_key, encrypt)
    return ecc_decrypt

def UploadFileAction(request):
    if request.method == 'POST':
        global propose, existing, username
        filedata = request.FILES['t1'].read()
        filename = request.FILES['t1'].name
        access = request.POST.get('t2', False)

        start = timeit.default_timer()
        private_key, public_key = ECCKeys()
        encrypted = EccEncrypt(filedata, public_key)
        end = timeit.default_timer()
        existing = end - start

        start = timeit.default_timer()
        key = get_random_bytes(32)
        cipher = ChaCha20.new(key=key)
        ciphertext = cipher.encrypt(filedata)
        end = timeit.default_timer()
        propose = end - start
        msg = "Error in file upload"
        db_connection = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'Authentication',charset='utf8')
        db_cursor = db_connection.cursor()
        student_sql_query = "INSERT INTO share(owner,filename,access_type) VALUES('"+username+"','"+filename+"','"+access+"')"
        db_cursor.execute(student_sql_query)
        db_connection.commit()
        print(db_cursor.rowcount, "Record Inserted")
        if db_cursor.rowcount == 1:
            with open("AuthenticationApp/static/files/"+filename, "wb") as file:
                file.write(encrypted)
            file.close()
            msg = "File successfully loaded to cloud"
        context= {'data': msg}
        return render(request, 'UploadFile.html', context)

def DownloadAction(request):
    if request.method == 'GET':
        filename = request.GET.get('name', False)
        with open("AuthenticationApp/static/files/"+filename, "rb") as file:
            content = file.read()
        file.close()
        private_key, public_key = ECCKeys()
        decrypted = EccDecrypt(content, private_key)
        response = HttpResponse(decrypted,content_type='application/force-download')
        response['Content-Disposition'] = 'attachment; filename='+filename
        return response

def Graph(request):
    if request.method == 'GET':
        global existing, propose
        labels = ['ECC Computation', 'CHACHA Computation']
        height = [existing, propose]
        bars = labels
        y_pos = np.arange(len(bars))
        plt.figure(figsize = (4, 3)) 
        plt.bar(y_pos, height)
        plt.xticks(y_pos, bars)
        plt.xlabel("Technique Names")
        plt.ylabel("Computation Time")
        plt.title("Propose & Extension Computation Time Graph")
        plt.xticks()
        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        plt.close()
        img_b64 = base64.b64encode(buf.getvalue()).decode()
        context= {'data': img_b64}
        return render(request, 'ViewGraph.html', context)   

def DownloadFile(request):
    if request.method == 'GET':
        global username
        output = '<table border=1 align=center>'
        output+='<tr><th><font size=3 color=black>Owner Name</font></th>'
        output+='<th><font size=3 color=black>File Name</font></th>'
        output+='<th><font size=3 color=black>Access Type</font></th>'
        output+='<th><font size=3 color=black>Download File</font></th></tr>'
        mysqlConnect = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'Authentication',charset='utf8')
        with mysqlConnect:
            result = mysqlConnect.cursor()
            result.execute("select * from share")
            lists = result.fetchall()
            for ls in lists:
                output+='<tr><td><font size=3 color=black>'+str(ls[0])+'</font></td>'
                output+='<td><font size=3 color=black>'+ls[1]+'</font></td>'
                output+='<td><font size=3 color=black>'+ls[2]+'</font></td>'
                if ls[2] == 'Public':
                    output+='<td><a href=\'DownloadAction?name='+str(ls[1])+'\'><font size=3 color=black>Click Here to Download</font></a></td></tr>'
                if ls[2] == 'Private' and username == ls[0]:
                    output+='<td><a href=\'DownloadAction?name='+str(ls[1])+'\'><font size=3 color=black>Click Here to Download</font></a></td></tr>'
                if ls[2] == 'Private' and username != ls[0]:
                    output+='<td><font size=3 color=black>Not Allowed to Download</font></td></tr>'    
        context= {'data':output}        
        return render(request,'UserScreen.html', context)     

def UploadFile(request):
    if request.method == 'GET':
       return render(request, 'UploadFile.html', {})

def ChangePassword(request):
    if request.method == 'GET':
       return render(request, 'ChangePassword.html', {})

def ChangePasswordAction(request):
    if request.method == 'POST':
        old = request.POST.get('t1', False)
        new = request.POST.get('t2', False)
        conirm = request.POST.get('t3', False)
        db_connection = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'Authentication',charset='utf8')
        db_cursor = db_connection.cursor()
        student_sql_query = "update newuser set password='"+new+"' where password='"+old+"'"
        db_cursor.execute(student_sql_query)
        db_connection.commit()
        msg = "Password did not match with database. Please try again"
        print(db_cursor.rowcount, "Record Inserted")
        if db_cursor.rowcount == 1:
            msg = "Password Changed Successfully"
        context= {'data': msg}
        return render(request, 'ChangePassword.html', context)                 

def index(request):
    if request.method == 'GET':
       return render(request, 'index.html', {})

def Login(request):
    if request.method == 'GET':
       return render(request, 'Login.html', {})

def Register(request):
    if request.method == 'GET':
       return render(request, 'Register.html', {})   

def Signup(request):
    if request.method == 'POST':
        username = request.POST.get('username', False)
        password = request.POST.get('password', False)
        contact = request.POST.get('contact', False)
        email = request.POST.get('email', False)
        address = request.POST.get('address', False)
        finger = request.FILES['finger'].read()
        status = "none"
        username = sha256(username.encode()).hexdigest()
        con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'Authentication',charset='utf8')
        with con:
            cur = con.cursor()
            cur.execute("select username FROM newuser where username='"+username+"'")
            rows = cur.fetchall()
            for row in rows:
                status = "exists"
        if status == "none":
            hashing = sha256(finger).hexdigest()
            db_connection = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'Authentication',charset='utf8')
            db_cursor = db_connection.cursor()
            student_sql_query = "INSERT INTO newuser(username,password,contact_no,address,email,finger_img) VALUES('"+username+"','"+password+"','"+contact+"','"+address+"','"+email+"','"+hashing+"')"
            db_cursor.execute(student_sql_query)
            db_connection.commit()
            print(db_cursor.rowcount, "Record Inserted")
            if db_cursor.rowcount == 1:
                context= {'data':'Signup Process Completed'}
                return render(request, 'Register.html', context)
            else:
                context= {'data':'Error in signup process'}
                return render(request, 'Register.html', context)
        else:
            context= {'data':'Username already exists'}
            return render(request, 'Register.html', context) 
        
def UserLogin(request):
    if request.method == 'POST':
        global username
        username = request.POST.get('username', False)
        password = request.POST.get('password', False)
        finger = request.FILES['finger'].read()
        hashing = sha256(finger).hexdigest()
        usernames = sha256(username.encode()).hexdigest()
        utype = 'none'
        con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'Authentication',charset='utf8')
        with con:
            cur = con.cursor()
            cur.execute("select * FROM newuser")
            rows = cur.fetchall()
            for row in rows:
                if row[0] == usernames and row[1] == password and row[5] == hashing:
                    utype = "success"
                    break
        if utype == 'success':
            context= {'data':'welcome '+username}
            return render(request, 'UserScreen.html', context)
        if utype == 'none':
            context= {'data':'Invalid login details'}
            return render(request, 'Login.html', context)        
        
        
