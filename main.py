from flask import Flask, redirect,render_template,request,flash,session
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin,login_required,logout_user,login_user,login_manager,LoginManager,current_user
from flask.helpers import url_for
from werkzeug.security import generate_password_hash,check_password_hash
import json
from flask_mail import Mail
# server connection
local_server = True
app=Flask(__name__)
app.secret_key = "dineshchoudhary"   #secret key for the app

# accesing the config.json file 
with open('project/config.json', 'r') as c:
    params=json.load(c)["params"]       #fetching the data from json file


#configuring mail 
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT='465',
    MAIL_USE_SSL=True,
    MAIL_USERNAME=params['gmail-user'],
    MAIL_PASSWORD=params['gmail-password']
)
mail = Mail(app)


#this is for getting the unique user access
login_manager=LoginManager(app)
login_manager.login_view='login'



#  my database connection     URI--> universal resourse identifier
# app.config['SQLALCHEMY_DATABASE_URI']='mysql://username:password@localhost/databaseanme'
app.config['SQLALCHEMY_DATABASE_URI']='mysql://root:@localhost/cancer'

# connecting database to app
db=SQLAlchemy(app)



# keeping track of the user that who is logged in.
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id)) or Hospitaluser.query.get(int(user_id))



class Test(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(50))



@app.route("/")
def home():
    return render_template("index.html")

# @app.route("/usersignup")    used for checking    we have already specified below
# def usersignup():
#     return render_template("usersignup.html")

# @app.route("/userlogin")
# def userlogin():
#     return render_template("userlogin.html")

class User(UserMixin,db.Model):
    id=db.Column(db.Integer,primary_key=True)
    mrfid=db.Column(db.String(20),unique=True)
    email=db.Column(db.String(100))
    dob=db.Column(db.String(1000))

# 	id	Hoscode	 email	password	

class Hospitaluser(UserMixin,db.Model):
    id=db.Column(db.Integer,primary_key=True)
    Hoscode=db.Column(db.String(20),unique=True)
    email=db.Column(db.String(100))
    password=db.Column(db.String(1000))


class Hospitaldata(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    Hoscode=db.Column(db.String(20),unique=True)
    hname=db.Column(db.String(50))
    normalbed=db.Column(db.Integer)
    eicubed=db.Column(db.Integer)
    icubed=db.Column(db.Integer)
    vbed=db.Column(db.Integer)

class Bookingpatient(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    mrfid=db.Column(db.String(20),unique=True)
    bedtype=db.Column(db.String(50))
    Hoscode=db.Column(db.String(20))
    spo2=db.Column(db.Integer)
    pname=db.Column(db.String(50))
    pphone=db.Column(db.String(50))
    paddress=db.Column(db.String(100))



class Trig(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    Hoscode=db.Column(db.String(20),)
    normalbed=db.Column(db.Integer)
    eicubed=db.Column(db.Integer)
    icubed=db.Column(db.Integer)
    vbed=db.Column(db.Integer)
    querys=db.Column(db.String(50))
    date=db.Column(db.String(50))


#to get user data
@app.route('/signup',methods=['POST','GET'])
def signup():
    if request.method=='POST':  #taking the input data
        mrfid=request.form.get('mrf')       #getting the information from the form of signup from usersignup.html
        email=request.form.get('email')    
        dob=request.form.get('dob')
        # print(mrfid,email,dob)                      just for testing wether its printing for not
        encpassword=generate_password_hash(dob)  # encrypting the password of users dob
        user=User.query.filter_by(mrfid=mrfid).first()
        emailUser=User.query.filter_by(email=email).first()
        if user or emailUser:                           #puting data into the database
            flash("Email or MRFID already taken","warning")
            return render_template("usersignup.html")
        new_user=db.engine.execute(f"INSERT INTO `user` (`mrfid`,`email`,`dob`) VALUES ('{mrfid}','{email}','{encpassword}')")
          
        flash("SignUp Success Please Login","success")
        return render_template("userlogin.html")

    return render_template("usersignup.html")    #rendering back to usersignup



@app.route('/login',methods=['POST','GET'])
def login():
    if request.method=='POST':            #taking input data from the user
        mrfid=request.form.get('mrf')       #getting the information from the form of login from userlogin.html    
        dob=request.form.get('dob')
        user=User.query.filter_by(mrfid=mrfid).first()  #extracing all the values of user

        if user and check_password_hash(user.dob,dob):  #giving login access
            login_user(user)
            flash("Login Success", "info")
            return render_template("index.html")
        else:
            flash("Invalid Credentials", "danger")
            return render_template("userlogin.html")

    return render_template("userlogin.html")       #rendering back to userlogin


@app.route('/hospitallogin',methods=['POST','GET'])
def hospitallogin():
    if request.method=='POST':            #taking input data from the user
        email=request.form.get('email')     #getting the information from the form of login from userlogin.html    
        password=request.form.get('password')
        user=Hospitaluser.query.filter_by(email=email).first()  #extracing all the values of user

        if user and check_password_hash(user.password,password):  #giving login access
            login_user(user)
            flash("Login Success", "info")
            return render_template("index.html")
        else:
            flash("Invalid Credentials", "danger")
            return render_template("hospitallogin.html")

    return render_template("hospitallogin.html")


@app.route('/admin',methods=['POST','GET'])
def admin():
    if request.method=='POST':            #taking input data from the user
        username=request.form.get('username')#getting the information from the form of login from userlogin.html    
        password=request.form.get('password')
        if(username==params['user'] and password==params['password']):
            session['user']=username
            flash("login success", "info")
            return render_template("addHosUser.html")
        else:
            flash("Invalid Credentials", "danger")

    return render_template("admin.html")       #rendering back to userlogin

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logout Successfull","primary")
    return redirect(url_for('login'))


@app.route('/addHospitalUser',methods=['POST','GET'])
def hospitalUser():
    if('user' in session and session['user']==params['user']):
        if request.method=="POST":
            Hoscode=request.form.get('Hoscode')    
            email=request.form.get('email')    
            password=request.form.get('password')          
            encpassword=generate_password_hash(password) 
            Hoscode = Hoscode.upper() 
            emailUser=Hospitaluser.query.filter_by(email=email).first()

            if emailUser:                         
                flash("Email or MRFID already taken","warning")
                
            db.engine.execute(f"INSERT INTO `hospitaluser` (`Hoscode`,`email`,`password`) VALUES ('{Hoscode}','{email}','{encpassword}')")

            mail.send_message('CANCER PATIENT BED SLOT ALLOTEMENT',sender=params['gmail-user'],recipients=[email],body=f"Welcome to\nCANCER PATIENT BED SLOT ALLOTEMENT\nThanks for choosing us\nAs per your request we are providing the Email-id and password for your login to our website\n\nYour Login Credentials Are:\nEmail: {email}\nPassword: {password} \n and your Hospital Code is: {Hoscode}\n\n\nDO NOT SHARE YOUR PASSWORD\n\nThank You....")
            flash("Data Sent And Inserted Successfully","warning")
            return render_template('addHosUser.html')
    else:
        flash("Login and try Again","warning")
        return redirect('/addHosUser.html')
    
# query for testing of database connection with app or not
@app.route("/test")
def test():
    try:
        a = Test.query.all()    #query of Test 
        print(a)
        return f"THE DATABASE IS CONNECTED {a.name}"
    except Exception as e:
        print(e)
        return f"THE DATABASE IS NOT CONNECTED {e}"


@app.route('/logoutadmin')
@login_required
def logoutadmin():
    session.pop('user')
    flash("Admin Logout Successfull","primary")
    return redirect('/admin')


@app.route('/addhospitalinfo',methods=['POST','GET'])
def addhospitalinfo():
    email=current_user.email
    posts=Hospitaluser.query.filter_by(email=email).first()
    code=posts.Hoscode
    # print(code)
    postsdata=Hospitaldata.query.filter_by(Hoscode=code).first()

    if request.method=="POST":
        Hoscode=request.form.get('Hoscode')    
        hname=request.form.get('hname') 
        nbed=request.form.get('normalbed') 
        ebed=request.form.get('eicubeds') 
        ibed=request.form.get('icubeds') 
        vbed=request.form.get('ventbeds') 
        Hoscode=Hoscode.upper()
        huser=Hospitaluser.query.filter_by(Hoscode=Hoscode).first()   
        hduser=Hospitaldata.query.filter_by(Hoscode=Hoscode).first()   
        if hduser:
            flash("Data is already Present you can update it..", "primary")
            return render_template("hospitaldata.html")
        if huser:
            db.engine.execute(f"INSERT INTO `hospitaldata` (`Hoscode`,`hname`,`normalbed`,`eicubed`,`icubed`,`vbed`) VALUES ('{Hoscode}','{hname}','{nbed}','{ebed}','{ibed}','{vbed}')")
            flash("Data Added","info")
        else:
            flash("Hospital Code not Exists","warning")   #if hoscode is not present in database this prints



    return render_template("hospitaldata.html",postsdata=postsdata)


@app.route("/hedit/<string:id>",methods=['POST','GET'])
@login_required
def hedit(id):
    posts=Hospitaldata.query.filter_by(id=id).first()
    if request.method=="POST":
        Hoscode=request.form.get('Hoscode')    
        hname=request.form.get('hname') 
        nbed=request.form.get('normalbed') 
        ebed=request.form.get('eicubeds') 
        ibed=request.form.get('icubeds') 
        vbed=request.form.get('ventbeds') 
        Hoscode=Hoscode.upper()
        db.engine.execute(f"UPDATE `hospitaldata` SET `Hoscode` ='{Hoscode}',`hname` ='{hname}',`normalbed` ='{nbed}',`eicubed` ='{ebed}',`icubed` ='{ibed}',`vbed` ='{vbed}'WHERE `hospitaldata`.`id`={id}")
        flash("Slot Updated","info")
        return redirect("/addhospitalinfo")


    return render_template('hedit.html',posts=posts)




@app.route("/hdelete/<string:id>",methods=['POST','GET'])
@login_required
def hdelete(id):
    db.engine.execute(f"DELETE FROM `hospitaldata` WHERE `hospitaldata`.`id`={id}")
    flash("Data Deleted","danger")
    return redirect("/addhospitalinfo")


@app.route("/pdetails",methods=['GET'])
@login_required
def pdetails():
    code=current_user.mrfid
    print(code)
    data = Bookingpatient.query.filter_by(mrfid=code).first()

    return render_template("details.html",data=data)

@app.route("/slotbooking",methods=['POST','GET'])
@login_required
def slotbooking():
    query=db.engine.execute(f"SELECT * FROM `hospitaldata` ")
    if request.method=='POST':
        mrfid=request.form.get('mrfid')
        bedtype=request.form.get('bedtype')
        Hoscode=request.form.get('Hoscode')
        spo2=request.form.get('spo2')
        pname=request.form.get('pname')
        pphone=request.form.get('pphone')
        paddress=request.form.get('paddress')
        check2 = Hospitaldata.query.filter_by(Hoscode=Hoscode).first()
        if not check2:
            flash("Hospital Code not exist", "warning")
        code=Hoscode
        dbb=db.engine.execute(f"SELECT * FROM `hospitaldata` WHERE `hospitaldata`.`Hoscode`='{code}' ")
        bedtype=bedtype
        if bedtype == "NormalBed":
            for d in dbb:
                seat=d.normalbed
                print(seat)
                ar = Hospitaldata.query.filter_by(Hoscode=code).first()
                ar.normalbed = seat-1
                db.session.commit()

        elif bedtype == "EICUBed":
            for d in dbb:
                seat = d.eicubed
                print(seat)
                ar = Hospitaldata.query.filter_by(Hoscode=code).first()
                ar.eicubed = seat-1
                db.session.commit()

        elif bedtype == "ICUBed":
            for d in dbb:
                seat = d.icubed
                print(seat)
                ar = Hospitaldata.query.filter_by(Hoscode=code).first()
                ar.icubed = seat-1
                db.session.commit()

        elif bedtype == "VENTILATORBed":
            for d in dbb:
                seat = d.vbed
                ar = Hospitaldata.query.filter_by(Hoscode=code).first()
                ar.vbed = seat-1
                db.session.commit()
        else:
            pass
        
        check = Hospitaldata.query.filter_by(Hoscode=Hoscode).first()
        if(seat > 0 and check):
            res = Bookingpatient(mrfid=mrfid, bedtype=bedtype, Hoscode=Hoscode,
                                 spo2=spo2, pname=pname, pphone=pphone, paddress=paddress)
            db.session.add(res)
            db.session.commit()
            flash("Slot is Booked kindly Visit Hospital for Further Procedure", "success")
        else:
            flash("Something Went Wrong", "danger")


    return render_template("booking.html",query=query)


@app.route("/triggers")
def triggers():
    query=Trig.query.all()
    return render_template("triggers.html",query=query)


app.run(debug = True)