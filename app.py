from flask import *
from flask_sqlalchemy import *
from flask_login import login_required, logout_user, current_user, login_user, UserMixin, current_user
from werkzeug.security import *
from datetime import datetime
from sqlalchemy import *
from pytz import timezone
from flask_login import LoginManager
from flask_admin import *
from flask_admin.contrib.sqla import ModelView
import random
import string
import smtplib
from flask_migrate import Migrate

format = "%d-%m-%Y"
now_utc = datetime.now(timezone('UTC'))


upload_profile = "./static/images/profile"
upload_media = "./static/posts"

app = Flask(__name__, static_folder='./static') 
app.secret_key = ""
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['UPLOAD_PROFILE'] = upload_profile
app.config['UPLOAD_MEDIA'] = upload_media
login_manager = LoginManager()
login_manager.init_app(app)
db=SQLAlchemy(app)
migrate = Migrate(app, db)
class posts(db.Model):
    __tablename__="Post"
    id=db.Column(db.Integer, primary_key=True)
    title=db.Column(db.String(100,), nullable=True)
    content=db.Column(db.Text)
    author=db.Column(db.String, default="N/A")
    username=db.Column(db.String) # For Personal Posts Identification making it easy to delete only your posts logic
    date=db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return "Blog Post " + str(self.id)

class User(db.Model, UserMixin):
    __tablename__="Login"
    id=db.Column(db.Integer, primary_key=True)
    username=db.Column(db.String, unique=True)
    firstname=db.Column(db.String)
    lastname=db.Column(db.String)
    password=db.Column(db.String)
    email=db.Column(db.String, unique=True)
    gender=db.Column(db.String)
    dob=db.Column(db.String)
    about_me = db.Column(db.String(140), default="Not Available")
    location = db.Column(db.String, default="Not Defined")
    last_seen = db.Column(db.String, default="N/A")
    profile_pic = db.Column(db.String, default="/static/images/profile/404.jpg")
    friend_array = db.Column(db.String)
    isprivate = db.Column(db.Integer, default = 0)
    isverified = db.Column(db.Integer, default = 0)

    def __repr__(self):
        return "Registered User " + str(self.id)
    def set_password(self, password):
        self.password = generate_password_hash(password)
    def check_password(self, password):
        return check_password_hash(self.password, password)
    
class emailverification(db.Model):
    __tablename__ = 'emailverify'
    id=db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String)
    uid = db.Column(db.Integer)
    ehash = db.Column(db.String)
    def __repr__(self):
        return "Email Verification " + str(self.id)

class friend_requests(db.Model):
    __tablename__="friend_resquests"
    id=db.Column(db.Integer, primary_key=True)
    user_from=db.Column(db.String)
    user_to=db.Column(db.String)

class comments(db.Model):
    __tablename__= "comments"
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(140))
    username = db.Column(db.String(32))
    pid= db.Column(db.Integer) #post id of comment to be linked
    time = db.Column(db.DateTime(), default=datetime.utcnow, index=True)

class likes(db.Model):
    __tablename__ = "likes"
    id = db.Column(db.Integer, primary_key=True)
    pid= db.Column(db.Integer) #post id of comment to be linked
    total = db.Column(db.Integer)
    liked_by = db.Column(db.String, nullable=True)

#----------------Admin model(The first registered user or a specific username can be set to be the admin)-------
class myadminmodel(ModelView):
    def is_accessible(self):
        if current_user.username == "admin": #or current_user.id == 1:
            return True
        else:
            #return False
            return render_template('notp.html')

#cleaning variables so it wont show error again(check the code to understand how ive used this)
def errorclean():
    global msg
    global mssg
    global errmsg
    global emailv
    global msg2
    global passmsg
    msg = ''
    mssg = ''
    errmsg = ''
    emailv=''
    msg2=''
    passmsg=''
    return ''
#-------------------------------Email Verification(Not yet implimented)-------------------
def genhash():
    hash = random.getrandbits(128)
    return hash

def vemail():
    user="flaskbook1@gmail.com"
    passwd=""
    receiver_address = current_user.email
    session = smtplib.SMTP('smtp.gmail.com', 587) #use gmail with port
    session.starttls() #enable security
    session.login(user, passwd) #login with mail_id and password
    hash1=genhash()
    link = "localhost.com/emailverify/hash="+str(hash1)
    text="Verify FlaskBook acc By clicking the link :-  localhost:5000/emailverify/hash="+str(hash1)
    session.sendmail(user, receiver_address, link)
    session.quit()
    a=emailverification(email=current_user.email,uid=current_user.id,ehash=hash1)
    db.session.add(a)
    db.session.commit()
    print(hash1)
#-------------------------------------------------------------------------------------------

#Admin Dashboard to check db(Simpliefied one)
admin = Admin(app)
admin.add_view(myadminmodel(User, db.session))
admin.add_view(myadminmodel(posts, db.session))
admin.add_view(myadminmodel(friend_requests, db.session))
admin.add_view(myadminmodel(comments, db.session))
admin.add_view(myadminmodel(likes, db.session))
admin.add_view(myadminmodel(emailverification, db.session))
# ------------------------------------ALL INITIATIONS DONE------------------------------------------
#INDEX
@app.route('/')
@app.route('/index')
def index():
    try:
        msg = mssg
    except NameError:
        msg = ''
    try:
        errmsg = passmsg
    except NameError:
        errmsg = ""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    else:
        return render_template("index.html",msg=msg,clean=errorclean(),errmsg=errmsg)

#POST REATION AND DISPLAY
@app.route('/posts', methods=["GET", "POST"])

def posts1():

    if request.method == "POST":
        post_title = request.form['title']
        post_content = request.form['content']
        post_author = request.form['author']
        new_post = posts(title=post_title, content=post_content,author=post_author, username=current_user.username)
        db.session.add(new_post)
        db.session.commit()
        return redirect('/posts')
    else:
        all_post = posts.query.order_by(posts.date.desc())
        return render_template('posts.html', posts=all_post) 

#New Post

@app.route('/dashboard/new', methods=["GET", "POST"])
@login_required
def new_post():

    if request.method == "POST":
        post_title = "Post by "+current_user.username
        post_content = request.form['content']
        post_author = current_user.firstname+" "+current_user.lastname
        post_media = request.files.get('media')
        #If the user uploads or chooses to upload images
        if post_media:
            if post_content != "":
                file=request.files['media']
                filename = file.filename
                extension = filename.split('.')[1]
                letters = string.ascii_lowercase
                random1 = ''.join(random.choice(letters) for i in range(10)) 
                medianame = random1+"."+extension
                pathtomedia = "/static/posts/"+medianame
                new_post = posts(title=post_title, content="media,"+pathtomedia+","+post_content,author=post_author, username=current_user.username)
                file.save(os.path.join(app.config['UPLOAD_MEDIA'], medianame))
                db.session.add(new_post)
                db.session.commit()
                getd=posts.query.all()[-1].id
                like= likes(pid=int(getd),total=0)
                db.session.add(like)
                db.session.commit()
                return redirect(request.referrer)
            else:
                file=request.files['media']
                filename = file.filename
                extension = filename.split('.')[1]
                letters = string.ascii_lowercase
                random1 = ''.join(random.choice(letters) for i in range(10)) 
                medianame = random1+"."+extension
                pathtomedia = "/static/posts/"+medianame
                new_post = posts(title=post_title, content="media,"+pathtomedia,author=post_author, username=current_user.username)
                file.save(os.path.join(app.config['UPLOAD_MEDIA'], medianame))
                db.session.add(new_post)
                db.session.commit()
                getd=posts.query.all()[-1].id
                like= likes(pid=int(getd),total=0)
                db.session.add(like)
                db.session.commit()
                return redirect(request.referrer)
        #If no photo is chosen
        else:
            if post_content != "":
                new_post = posts(title=post_title, content=post_content,author=post_author, username=current_user.username)
                db.session.add(new_post)
                db.session.commit()
                getd=posts.query.all()[-1].id
                like= likes(pid=int(getd),total=0)
                db.session.add(like)
                db.session.commit()
                return redirect(request.referrer)
            else:
                global errmsg
                errmsg = "Cannot Post Somethig Not written! "
                return redirect(request.referrer)
    else:
        all_post = posts.query.all()
        return render_template('new_post.html')


#POST DELETING
@app.route("/dashboard/delete/<int:id>")
@login_required
def delete_post(id):
    post = posts.query.get(id)
    if "media" in post.content:
        file = post.content.split(',')[1]
        os.remove("."+file)
    like = likes.query.filter_by(pid=id).all()
    com = comments.query.filter_by(pid=id).all()
    db.session.delete(post)
    for l in like:
        db.session.delete(l)
    for comm in com:
        db.session.delete(comm)
    db.session.commit()
    return redirect(request.referrer)


#POST EDITING
@app.route('/dashboard/edit/<int:id>', methods=["GET", "POST"])
@login_required
def edit(id):
    post = posts.query.get(id)
    if request.method == "POST":
        post.title = request.form['title']
        post.content = request.form['content']
        post.author = request.form['author']
        db.session.commit()
        return redirect(request.referrer)
    else:
        return render_template("edit_post.html", post=post)

# Dashboard
@app.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    try:
        msg = errmsg
    except NameError:
        msg = ''
    try:
        msg2 = emailv
    except NameError:
        msg2 = ''
    user_posts = posts.query.order_by(posts.date.desc()).all()
    friends=current_user.friend_array
    requests = friend_requests.query.filter_by(user_to=current_user.username).all()
    if friends != None:
        splitf=friends.split(',')
    else:
        splitf = ''
    return render_template("home.html", splitf=splitf, posts=user_posts, blogposts=posts.query.order_by(posts.date.desc()),comment=comments(),likes=likes(),r=requests,User=User(),msg=msg,clean=errorclean(),msg2=msg2)

#New comments


@app.route("/dashboard/new_comment/<int:pid>",methods=["POST"])
@login_required
def addcomment(pid):
    if request.method == "POST":
        comment=request.form.get("comment")
        new_comment=comments(text=comment, username=current_user.username, pid=pid)
        db.session.add(new_comment)
        db.session.commit()
        return redirect(request.referrer)

#Delete Comments

@app.route("/dashboard/del_comment/<int:id>",methods=['GET','POST'])
@login_required
def delcomment(id):
    com=comments.query.get(id)
    db.session.delete(com)
    db.session.commit()
    return redirect(request.referrer)

#Add likes
@app.route("/addlike/<int:pid>",methods=['GET','POST'])
@login_required
def likes1(pid):
    query=likes.query.filter_by(pid=pid).first()
    likedby = query.liked_by
    if likedby == None:
        query.liked_by = current_user.username
        totalno=int(query.total)+1
        query.total=int(totalno)
        db.session.commit()
    #if the user has already liked the post it will just ignoreee
    else:
        splitf=likedby.split(',')
        if current_user.username not in splitf:
            totalno=int(query.total)+1
            query.total=int(totalno)
            query.liked_by = likedby +","+current_user.username
            db.session.commit()
    
    return redirect(request.referrer)
    
#Profile Information
@app.route("/profile",methods=["GET","POST"])
@login_required
def profile_info():
    try:
        msg=errmsg
    except NameError:
        msg = ''
    posts1 = posts.query.filter_by(username=current_user.username).order_by(posts.date.desc()).all()
    friends=current_user.friend_array
    if (friends != '') and (friends != None):
        splitf=friends.split(',')
    else:
        splitf=friends
    return render_template("profile.html",posts=posts1,friends=splitf,User=User(),likes=likes(),comment=comments(),msg=msg,clean=errorclean())

#Change Profile Info
@app.route("/profile/edit/<int:id>",methods=['GET','POST'])
def profile_info_change(id):
    if request.method == "POST":
        info = User.query.get(id)
        info.username = request.form['username']
        info.firstname=request.form['firstname']
        info.lastname=request.form['lastname']
        info.email=request.form['email']
        info.about_me = request.form['about_me']
        profilepic=request.files.get('file')
        if profilepic: 
            file=request.files.get('file')
            filename= file.filename
            new_filename=current_user.username+"."+filename.split('.')[1]
            file.save(os.path.join(app.config['UPLOAD_PROFILE'], new_filename))
            info.profile_pic="/static/images/profile/"+new_filename
            db.session.commit()
            return redirect(request.referrer)
        db.session.commit()
        return redirect(request.referrer)
    else:
        return redirect("/profile")

#Edit Profile
@app.route("/profile/edit1/<int:id>",methods=['GET','POST'])
@login_required
def edittt(id):
    if request.method == "POST":
        a=User.query.get(id)
        about=request.form.get("status")
        location=request.form.get("location1")
        private = request.form.get("private")
        if private == "yes":
            a.isprivate = 1
        else:
            a.isprivate = 0

        a.about_me = about
        a.location = location
        db.session.commit()
        return redirect(request.referrer)
    
    return render_template("edit_profile.html")

#change profile password
@app.route("/profile/passchange/<int:id>",methods=['GET','POST'])
@login_required
def profile_pass_change(id):
    if request.method == "POST":
        password = current_user.password
        user = User.query.get(id)
        old_pass = request.form['pass1']
        new_pass = request.form['pass2']
        conf_pass = request.form['pass3']
        if password == old_pass :
            if new_pass == conf_pass:
                user.password = new_pass
                db.session.commit()
                return redirect('/profile')
        else :
            flash ("Both Passwords Dont Match")
    return redirect('/profile')


@app.route("/file", methods=["GET", "POST"])
@login_required
def file_upload():
    if request.method == "POST":
        file=request.files['file']
        filename=file.filename
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return render_template('file.html')
    else:
        return render_template('file.html')

#Register Part

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        global passmsg
        first = request.form["first"]
        last = request.form["last"]
        username = request.form['username']
        email = request.form["email"]
        gender = request.form["gen"]
        password = request.form["pass1"]
        confirm = request.form["pass2"]
        date = request.form['date']
        existing_user = User.query.filter_by(email=email).first()
        existing_user1 = User.query.filter_by(username=username).first()
        if existing_user is None:
            if existing_user1 is None:
                if password == confirm:
                    user=User(firstname=first, lastname=last, email=email, gender=gender, username=username, dob=date)
                    user.set_password(password)
                    db.session.add(user)
                    db.session.commit()
                    login_user(user)
                    #vemail()
                    return redirect(url_for('login1'))
                else:
                    passmsg = "Password & Confirm Password dont match"
                    return redirect(request.referrer)
            else:
                passmsg = "Username already Exists!"
                return redirect(request.referrer)
        else:
            passmsg = "Email already exists!"
            return redirect(request.referrer)
    return redirect("/index")


#Email Verification(Not t impimented)
@app.route('/emailv/hash=<hash1>',methods=(['GET','POST']))
def verifyemail(hash1):
    getd=emailverification.query.filter_by(ehash=hash1).first()
    if getd:
        if getd.uid == current_user.id:
            current_user.isverified = 1
            db.session.delete(getd)
            db.session.commit()
        else:
            return '''You were not the one i was gonna verify'''
    else:
        '''Wrong Code Verification failed'''

#Login part
@app.route("/login",methods=['GET','POST'])
def login1():
    msg = ''
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        user1 = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=user1).first()
        if user:
            if user.check_password(password):
                login_user(user)
                next = request.args.get('next')
                return redirect(next or url_for('dashboard'))
                if current_user.isverified == 0:
                    global emailv
                    emailv = "You Havent verified your email do it asap"
            else:
                global mssg
                mssg = " Wrong Password I guess"
                return redirect(request.referrer)
        else:
            mssg = "Wrong Username/Password"
            return redirect(request.referrer)
        return redirect(url_for('login1')) 
    return redirect("/")     

    
    return render_template("/")
#Search Part
@app.route('/search',methods=['GET','POST'])
def search1():
    if request.method == "POST":
        query = str(request.form.get('search'))
        ab=User.query.filter(User.firstname.like(query))
        a=ab.all()
        return render_template('search.html',search=a,f=friend_requests())
    else:
        return redirect('/')

@app.route('/s')
def s():
    return render_template('user.html')
    

#Search a User using username
@app.route('/user/<username>')
def fbuser(username):
    user=User.query.filter_by(username=username).first()
    posts1 = posts.query.filter_by(username=username).order_by(posts.date.desc()).all()
    friends=user.friend_array
    if (friends != '') and (friends != None):
        splitf=friends.split(',')
    else:
        splitf=''
    return render_template("user1.html",user=user,f=friend_requests(),friends=splitf,posts=posts1,User=User,likes=likes(),comment=comments())
# Add Friend Send Friend request
@app.route('/addfriend/<username>',methods=['GET','POST'])
def addfriend(username):
    a=User.query.filter_by(username=username).first()
    if request.method == "POST":
        user_to=a.username
        user_from=current_user.username
        addf=friend_requests(user_from=user_from,user_to=user_to)
        db.session.add(addf)
        b="/user/"+username
        db.session.commit()
        return redirect(request.referrer)

#Check Friend Requests
@app.route('/friendreq')
def friendreq():
    requests = friend_requests.query.filter_by(user_to=current_user.username).all()
    return render_template("requests.html", r=requests)

#if accept
@app.route("/accept/<int:id>",methods=['GET',"POST"])
def acceptreq(id):
    if request.method == "POST":
        accept_id=friend_requests.query.get(id)
        user_from=accept_id.user_from
        allfriends=current_user.friend_array
        user_to=accept_id.user_to
        if allfriends == None:
            addf=user_from    
        else:
            addf=allfriends+","+user_from
        con=User.query.filter_by(username=current_user.username).first()
        con.friend_array=addf
        allfriends2 = User.query.filter_by(username=user_from).first().friend_array
        if (allfriends2 == None) or (allfriends2 == ""):
            addf = user_to
        else:
            addf=allfriends2+","+user_to
        con=User.query.filter_by(username=user_from).first()
        con.friend_array=addf
        friend_requests.query.filter_by(user_from=user_from).delete()
        db.session.commit()
        return redirect(request.referrer)
    return redirect('/friendreq')
        #conact and save the old names with the new friend name in variable and then split it with split() and then  view each post using for loop

#if reject
@app.route("/reject/<int:id>", methods=['GET','POST'])
def rejectreq(id):
    user= friend_requests.query.get(id)
    db.session.delete(user)
    db.session.commit()
    return redirect(request.referrer)



#friends
@app.route("/friends",methods=['GET','POST'])
def friends():
    friends=current_user.friend_array
    if friends != '':
        splitf=friends.split(',')
    else:
        splitf=[]
    print (splitf)
    return render_template('friends.html',friends=splitf, User=User())

#remove friends
@app.route("/remfriend/<username>")
def remfriend(username):
    a=User.query.filter_by(username=current_user.username).first()
    b=a.friend_array
    d=username+","
    e=username
    if d in b:
        c=b.replace(d, "")
    elif e in b:
        c=b.replace(e, "")
    a.friend_array = c
    f=current_user.username+","
    g=current_user.username
    user2 = User.query.filter_by(username=username).first()
    h = user2.friend_array
    if f in h :
        i = h.replace(f,"")
    elif g in h:
        i = h.replace(g,"")
    user2.friend_array = i
    db.session.commit()
    return redirect(request.referrer)
    
#Logout
@app.route("/logout")
@login_required
def logout_page():
    """User log-out logic."""
    logout_user()
    return redirect("/")

#Made just for Making it possible to edit profile information
@app.route("/logout1")
@login_required
def logout1():
    logout_user()

@login_manager.user_loader
def load_user(user_id):
    """Check if user is logged-in on every page load."""
    if user_id is not None:
        return User.query.get(user_id)
    return None    

@login_manager.unauthorized_handler
def unauthorized():
    """Redirect unauthorized users to Login page."""
    return redirect(url_for('index'))

#Make it compatible to deploy on heroku
'''if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)'''
