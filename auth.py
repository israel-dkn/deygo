from flask import Flask, Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date, timedelta
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import ValidationError, DataRequired
from os import path
import requests
from flask_login import login_user, UserMixin, LoginManager, login_required, logout_user, current_user
import random, string
import json
from flask_socketio import SocketIO, emit, join_room, leave_room, send
from geopy.geocoders import Nominatim
import geocoder
# from rider import rider_page

db = SQLAlchemy()
app = Flask(__name__)
# app.register_blueprint(rider_page, url_prefix='/rider')
DB_NAME = "database.db"
site_name="DEY GO"
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_NAME}"
secret_key = "IgVnWnSwmS0LN4RtKaaCubIiFCG2Iq0FSFDqJaboBy0eXHakp0jHFQ"
app.config["SECRET_KEY"] = "my secret key"
tomtom_admin_key = "PUuQt6512jSNCD3gdu00VxzYAsKQ7VDo2XrJoPvGhhhNoSl0"
tomtom_api_key = "JoBjMY24siY0bENUY5g52SLXouAaf4FX"
socketio = SocketIO(app)
geolocator = Nominatim(user_agent="deygologapp")
db.init_app(app)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    type = session.get('type')
    if type == 'user':
        user = UserSignup.query.get(int(user_id))
    elif type == 'partner':
        user = PartnerSignup.query.get(int(user_id))
    else:
        user = None
    #return useruser = PartnerSignup.query.get(int(user_id))
    return user




#
#
#
#
#
#



def ran_id():
    return ''.join(random.choice(string.digits) for i in range(10))

# ---- DATABASE MODELS ----


# order = db.Table("user_order",
#                   db.Column('user_id', db.Integer, db.ForeignKey("usersignup.id")),
#                   db.Column('order_id', db.Integer, db.ForeignKey("orders.id")),
#                   db.Column('rider_id', db.Integer, db.ForeignKey("partnersignup.id"))
#     )


class PartnerRegister(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(50), unique=True, nullable=False)
    street_1 = db.Column(db.String(50), nullable=False)
    street_2 = db.Column(db.String(100))
    zip_Code = db.Column(db.Integer)
    city = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    phone = db.Column(db.Integer, unique=True, nullable=False)
    rc_number = db.Column(db.Integer, unique=True)
    vat_number = db.Column(db.Integer, unique=True, nullable=False)
    staff_cap = db.Column(db.String, nullable=False)
    logo  = db.Column(db.String(50))
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    
    
class PartnerRegister1(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(50), unique=True, nullable=False)
    street_1 = db.Column(db.String(50), nullable=False)
    street_2 = db.Column(db.String(100))
    zip_Code = db.Column(db.Integer)
    city = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    phone = db.Column(db.Integer, unique=True, nullable=False)
    rc_number = db.Column(db.Integer, unique=True)
    vat_number = db.Column(db.Integer, unique=True, nullable=False)
    staff_cap = db.Column(db.String, nullable=False)
    logo  = db.Column(db.String(50))
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    
    

class Orders(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pickup = db.Column(db.String) 
    dropoff = db.Column(db.String)
    delivery_time = db.Column(db.String) 
    delivery_distance = db.Column(db.String) 
    delivery_cost = db.Column(db.String) 
    pickup_coord = db.Column(db.String)
    dropoff_coord = db.Column(db.String)
    placed_by = db.Column(db.String) #placed_by=current_user.name
    placed_by_id = db.Column(db.String) #placed_by=current_user.id
    time_created = db.Column(db.DateTime, default=datetime.now)
    track_id = db.Column(db.String, default=ran_id)
    status = db.Column(db.String(20), default='pending')
    driver_id = db.Column(db.Integer, db.ForeignKey('partnersignup.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('usersignup.id'))
    accepted_by = db.Column(db.String)
    
    def accept_order(self, partner_id):
        self.status = 'accepted'
        self.partner_id = partner_id
        db.session.commit()

    def reject_order(self):
        self.status = 'rejected'
        db.session.commit()



class PartnerSignup(db.Model, UserMixin):
    __tablename__ = 'partnersignup'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String)
    con_password = db.Column(db.String)
    driver_lat = db.Column(db.String)
    driver_lon = db.Column(db.String)
    driver = db.relationship('Orders', backref='partner')
    
    


class UserSignup(db.Model, UserMixin):
    __tablename__ = 'usersignup'
    
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String)
    address = db.Column(db.String)
    phone = db.Column(db.Integer, unique=True, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String)
    con_password = db.Column(db.String)
    user = db.relationship('Orders', backref='order')
    
   
    
    def __repr__(self):
        return f' <UserSignup "{self.full_name}"> '


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    track = db.Column(db.String(1000))
    # email = db.Column(db.String)
    
class Trk(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    track1 = db.Column(db.String(1000))
    # email = db.Column(db.String)
    
class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(1000))
    company_email = db.Column(db.String(1000))
    company_phone = db.Column(db.Integer)
    company_addr = db.Column(db.String(1000))
    
class Partner(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    partner_name = db.Column(db.String(1000))
    partner_email  = db.Column(db.String(1000))
    partner_phone = db.Column(db.Integer)
    partner_addr = db.Column(db.String(1000))
    
    
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_title = db.Column(db.String(50))
    post_time = db.Column(db.DateTime, default=datetime.utcnow)
    post_tag = db.Column(db.String(15), default=ran_id)
    post_content = db.Column(db.String(1000))
    
    

    
    
    
with app.app_context():
    # db.drop_all()
    db.create_all()

# <---- END DB MODELS ---->


#
#
#
#
#
#
#


# <---- FORM CLASS ---->

class PartnerRegisterForm(FlaskForm):
    u_name = StringField("Partner Name", validators=[DataRequired()])
    street1 = StringField("e.g 251 Hebert Macaulay Way", validators=[DataRequired()])
    street2 = StringField("e.g 251 Hebert Macaulay Way")
    zip_code = StringField("Partner Address", validators=[DataRequired()])
    city = SelectField("Select City...", choices=[("Abuja", "Abuja"), ("Lagos", "Lagos")], validators=[DataRequired()])
    email = StringField("Business Email", validators=[DataRequired()])
    phone = StringField("Your Business Phone", validators=[DataRequired()])
    rc_number = StringField("Your Business CAC Number", validators=[DataRequired()])
    vat_number = StringField("Business VAT ID")
    staff_cap = SelectField("Number Of Riders", choices=[("1 to 10", "1 ~ 10"), ("10 to 50", "10 ~ 50"), ("50 to 200", "50 ~ 200")], validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    submit = SubmitField("Register")
    

class PartnerSignupForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email (Display Email from Register DB)', validators=[DataRequired()])
    password = PasswordField('Type Your Password', validators=[DataRequired()])
    con_password = PasswordField('Confirm Your Password', validators=[DataRequired()])
    submit = SubmitField("Sign Up")
    

class UserSignupForm(FlaskForm):
    name = StringField('Your Name', validators=[DataRequired()])
    address = StringField('Your Address e.g 251 Hebert Macaulay Way', validators=[DataRequired()])
    phone = StringField('Your Phone Number', validators=[DataRequired()])
    email = StringField('Your Email', validators=[DataRequired()])
    password = PasswordField('Type Your Password', validators=[DataRequired()])
    con_password = PasswordField('Confirm Your Password', validators=[DataRequired()])
    submit = SubmitField("Sign Up")


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField("Login")
    

class PartnerLoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField("Login")
    
    

class PartnerForm(FlaskForm):
    partner_name = StringField("Partner Name", validators=[DataRequired()])
    partner_email = StringField("Partner Email", validators=[DataRequired()])
    partner_phone = StringField("Partner Phone", validators=[DataRequired()])
    partner_addr = StringField("Partner Address", validators=[DataRequired()])
    submit = SubmitField("Register")

class RequestOrderForm(FlaskForm):
    pickup = StringField("Pickup Address", validators=[DataRequired()])
    dropoff = StringField("Delivery Address", validators=[DataRequired()])
    message = StringField("Addidtional message")
    submit = SubmitField("Request Dispatch")


class TrackTestForm(FlaskForm):
    title = StringField("Title")
    submit = SubmitField("Register")



# <---- END FORM CLASS ---->


#
#
#
#
#
#

# <---- All test routes will go here ---->



@app.route("/html1")
def html1():
    return render_template("html1.html")


def total_seconds_filter(td):
    return td.total_seconds()

# Register the custom filter
app.jinja_env.filters['total_seconds'] = total_seconds_filter


def calculate_time_difference(minutes_ago):
    current_time = datetime.now()
    time_difference = current_time - minutes_ago
    minutes = int(time_difference.total_seconds() / 60)
    return minutes


def display_time_ago(minutes):
    if minutes < 1:
        return "Just now"
    elif minutes == 1:
        return "1 min ago"
    elif minutes < 60:
        return "{} mins ago".format(minutes)
    elif minutes < 1440:
        hours = minutes // 60
        return "{} hours ago".format(hours)
    else:
        days = minutes // 1440
        return "{} days ago".format(days)




@app.route("/index1")
def index1():
    trk_id = Trk.query.order_by(Trk.id.desc()).first()
    return render_template("tracking.html", trk_id=trk_id)

# code snippet from https://tutorial101.blogspot.com/2020/03/python-flask-sqlalchemy-search-like.html?m=1
@app.route('/db', methods=['GET', 'POST'], defaults={"page1": 1}) 
@app.route('/db/<int:page1>', methods=['GET', 'POST'])
def db_pg(page1):
    page1=page1
    employees = Partner.query.order_by(Partner.id.desc()).paginate(page=page1, per_page=5) #desc() 
    if request.method == 'POST' and 'tag' in request.form:
        tag = request.form["tag"]
        search = "%{}%".format(tag)
        employees = Partner.query.filter(Partner.partner_name.like(search)).paginate(per_page=5, error_out=True) # OR: from sqlalchemy import or_  filter(or_(User.name == 'ednalan', User.name == 'caite'))
        return render_template('dbpg.html', employees=employees, tag=tag)
    return render_template('dbpg.html', 
                        employees=employees)
    
   
   
@app.route('/Partner/Register', methods=[ "POST", "GET"])
def create_account():
    form = PartnerRegisterForm()
    if form.validate_on_submit():
        # Query database for existing data
        name = PartnerRegister1.query.filter_by(company_name=form.u_name.data).first()
        email = PartnerRegister1.query.filter_by(email=form.email.data).first()
        phone = PartnerRegister1.query.filter_by(phone=form.phone.data).first()
        rc_number = PartnerRegister1.query.filter_by(rc_number=form.rc_number.data).first()
        vat_number = PartnerRegister1.query.filter_by( vat_number=form.vat_number.data).first()
        if name:
            flash("Business Name already exist! Try again!")
            # If form data raises error, make other form input empty 
            form.u_name.data = ''
            form.street1.data = ''
            form.street2.data = ''
            form.zip_code.data = ''
            form.city.data = ''
            form.email.data = ''
            form.phone.data = ''
            form.rc_number.data = ''
            form.vat_number.data = ''
            form.staff_cap.data = ''
           
        elif email:
            flash("Email has already been registered!")
            form.email.data = ''
        
        elif phone:
            flash("Phone Number has already been registered!")
            form.phone.data = ''
        
        elif rc_number:
            flash("Address has already been registered!")
            form.rc_number.data = ''
        
        elif vat_number:
            flash("Address has already been registered!")
            form.vat_number.data = ''
            
        else:
            # If form data doesn't exist in database, Add partner to database
            partner_reg = PartnerRegister1(company_name=form.u_name.data, 
                                    email=form.email.data,
                                    phone=form.phone.data,
                                    street_1=form.street1.data,
                                    street_2=form.street1.data,
                                    zip_Code=form.zip_code.data,
                                    rc_number=form.rc_number.data,
                                    vat_number=form.vat_number.data,
                                    staff_cap=form.staff_cap.data,
                                    city=form.city.data,
                                    username=form.username.data)
            db.session.add(partner_reg)
            db.session.commit()
            flash("Hurray!!! Partner has already been registered!")
        #return redirect(url_for('partner_signup'))
     #partners = Partner_Register.query.order_by(Partner_Register.id.desc()).paginate(page=1, per_page=10)        
    return render_template('partner-create-account.html', form=form)



@app.route('/partner/sign-Up', methods=["POST", "GET"])
def partner_signup():
    form = PartnerSignupForm()
    if form.validate_on_submit():
        email = PartnerSignup.query.filter_by(email=form.email.data).first()
        if email:
            flash("Email Already Exist!")
            
        elif form.con_password.data != form.password.data:
            flash("Password does not match!")
            form.con_password.data = ''  
             
        else:    
            form_data = PartnerSignup(username=form.username.data,
                                    email=form.email.data,
                                    password=form.password.data,
                                    con_password=form.con_password.data)
            db.session.add(form_data)
            db.session.commit()
            flash("Partner Created Successfully!")
            return redirect(url_for('login'))
        
    return render_template("partner-register.html", form=form)





@app.route('/users/sign-up', methods=["POST", "GET"])
def user_signup():
    form = UserSignupForm()
    if form.validate_on_submit():
        user_mail = UserSignup.query.filter_by(email=form.email.data).first()
        user_phone = UserSignup.query.filter_by(phone=form.phone.data).first()
        if user_mail:
            flash("Email already exist!")
            # If form data raises error, make other form input empty 
            form.email.data = ''
        elif user_phone:
            flash("Phone Number already exist!")
            # If form data raises error, make other form input empty 
            form.phone.data = ''
        else:
            form_data = UserSignup(full_name=form.name.data,
                                email=form.email.data,
                                address=form.address.data,
                                phone=form.phone.data,
                                password=form.password.data,
                                con_password=form.con_password.data)
            db.session.add(form_data)
            db.session.commit()
            flash("You have successfully registered to {}".format(site_name))
            return redirect(url_for('login'))

    return render_template("user-register.html", form=form)






@app.route('/login', methods=["POST", "GET"])
def login():
    form = LoginForm()
    form2 = PartnerLoginForm()
    if request.method == "POST" and form.validate_on_submit():
        user_mail = UserSignup.query.filter_by(email=form.email.data).first()
        user_pass = UserSignup.query.filter_by(password=form.password.data).first()
        if user_mail and user_pass:
            login_user(user_mail, remember=True)
            session.permanent = True
            session['type'] = 'user'
            flash("Logged in successfully!")
            return redirect(url_for('user-dash'))
        else:
            flash("Email or password is incorrect! Try again...")
            form.email.data = '' 
            form.password.data = ''
            
    if request.method == "POST" and form2.validate_on_submit():
        partner_username = PartnerSignup.query.filter_by(username=form2.username.data).first()
        partner_mail = PartnerSignup.query.filter_by(email=form2.email.data).first()
        partner_pass = PartnerSignup.query.filter_by(password=form2.password.data).first()
        if partner_username and partner_mail and partner_pass:
            login_user(partner_mail, remember=True)
            session.permanent = True
            session['type'] = 'partner'
            flash("Logged in successfully!")
            return redirect(url_for('partner_dashboard', id=current_user.id))
        else:
            flash("Email or password is incorrect! Try again...")
            form2.username.data = '' 
            form2.email.data = '' 
            form2.password.data = ''
        
           
    return render_template('login.html', form=form, form2=form2)



def format_number_with_commas(number):
    # Convert the number to a string
    number_str = str(number)
    
    # Reverse the string to make it easier to add commas
    reversed_str = number_str[::-1]
    
    # Split the reversed string into chunks of three characters
    chunks = [reversed_str[i:i+3] for i in range(0, len(reversed_str), 3)]
    
    # Reverse the chunks and join them with commas
    formatted_str = ','.join(chunks)[::-1]
    
    return formatted_str




@app.route('/save_location', methods=['POST', 'GET'])
def save_location():
    data = request.get_json()
    partner_id = current_user.id
    new_coord = PartnerSignup.query.get(partner_id)
    
    latitude = data['latitude']
    longitude = data['longitude']
    
    new_coord.driver_lat = latitude
    new_coord.driver_lon = longitude
    try:
        db.session.commit()
    except:
        flash("oops, There was an error accepting this order...", category='error')
    
    return 'Location saved successfully'




@app.route("/company", methods=["POST", "GET"])
# @app.route("/company/<int:id>", methods=["POST", "GET"])
@login_required
def partner_dashboard():
    # redirect to home page if the user current session is "user"
    if session['type'] == "user" or None:
        flash("You Must be a partner to access this page", category="error")
        return redirect(url_for("home"))
    elif session['type'] == "partner":
        
       
        # def a func to say, if rider current lat,lon == nearest_rider_index
        # automatically assign order to the particular rider
        ses = session['type']
        orders = Orders.query.filter_by(status='pending').order_by(Orders.id.desc())
        orders_count = Orders.query.filter_by(driver_id=current_user.id, status='accepted').count()
        orders_sum_req = db.session.query(db.func.sum(Orders.delivery_cost)).filter_by(driver_id=current_user.id, status='accepted').scalar()
        
        timestamp = datetime.now()
        
        orders_sum = format_number_with_commas(orders_sum_req)
        
        return render_template('company.html', 
                            orders=orders,
                            orders_count=orders_count,
                            ses=ses,
                            orders_sum=orders_sum, 
                            timestamp=timestamp) 
        
    return render_template('company.html')
    




@app.route('/logout', methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    session.clear()
    flash("You have successfully logged out!")
    return redirect(url_for("login"))



@app.route("/track-create", methods=["POST", "GET"])
@login_required
def track_create():
    form=TrackTestForm()
    user_name = current_user.full_name
    user_id = current_user.id
    if request.method == "POST":
        add_item = Orders(title=form.title.data,
                          placed_by=user_name,
                          user_id=user_id)
        db.session.add(add_item)
        db.session.commit()
        flash("Successful")
    return render_template("track-create.html", form=form)






# @app.route("/rider-dash")
# def rider_dash():
#     orders = Orders.query.all()
#     # rider_accepted = Orders.query.filter(Orders.rider.has(id=1, status=accepted)).all()
#     return render_template("r-dash.html", orders=orders)





@app.route('/admin', methods=["POST", "GET"])
def admin_dahsboard():
     partners = Partner.query.order_by(Partner.id.desc()).paginate(page=1, per_page=10)        
     return render_template('admin.html', partners=partners)



@app.route("/main")
def main_pg():
    return render_template("base.html")


@app.route("/tables", methods=['GET', 'POST'], defaults={"page": 1})
@app.route('/tables/<int:page>', methods=["POST", "GET"])
def tables_css(page):
    page = page
    form = LoginForm()
    partners = PartnerRegister1.query.order_by(PartnerRegister1.id.desc()).paginate(page=page, per_page=5)
    
    return render_template("tables.html", form=form, 
                           partners=partners)


@app.route("/sign-up", methods=["GET", "POST"])
def sign_up():
    form = PartnerForm(request.form)
    if form.validate_on_submit():
        # Query database for existing data
        partner_name = Partner.query.filter_by(partner_name=form.partner_name.data).first()
        partner_email = Partner.query.filter_by(partner_email=form.partner_email.data).first()
        partner_phone = Partner.query.filter_by(partner_phone=form.partner_phone.data).first()
        partner_addr = Partner.query.filter_by(partner_addr=form.partner_addr.data).first()
        if partner_name:
            flash("Partner has already been registered!")
            # If form data raises error, make other form input empty 
            form.partner_email.data = ''
            form.partner_phone.data = ''
            form.partner_addr.data = ''
            
        elif partner_email:
            flash("Email has already been registered!")
            form.partner_email.data = ''
        
        elif partner_phone:
            flash("Phone Number has already been registered!")
            form.partner_phone.data = ''
        
        elif partner_addr:
            flash("Address has already been registered!")
            form.partner_addr.data = ''
            
        else:
            # If form data doesn't exist in database, Add partner to database
            partner = Partner(partner_name=form.partner_name.data, 
                              partner_email=form.partner_email.data,
                              partner_phone=form.partner_phone.data,
                              partner_addr=form.partner_addr.data)
            db.session.add(partner)
            db.session.commit()
            flash("Hurray!!! Partner has been registered!")
            
            form.partner_name.data = ''
            form.partner_email.data = ''
            form.partner_phone.data = ''
            form.partner_addr.data = ''
            
            
    return render_template("partner-signup.html", form=form)



# Route to add blog post
@app.route("/add-post", methods=["POST", "GET"])
def add_post():
    if request.method == "POST":
        blog_post= Post(post_title=request.form.get("post_title"),
                                post_tag=request.form.get("post_tag"),
                                post_content=request.form.get("post_content")
                                )
        db.session.add(blog_post)
        db.session.commit()
        flash("Post has been added successfully!")
    blog_posts = Post.query.order_by(Post.id.desc()).paginate(per_page=5)
    return render_template("add-post.html", blog_posts=blog_posts )

@app.route("/blog")
def blog():
    return render_template("blog.html")

# ---- End test routes ----


#
#
#
#
#
#


   

# Done! Completed
@app.route("/order/accept/<int:id>")
def order_accepted(id):
    accepted_by = current_user.id
    order_accept = Orders.query.get(id)
    # to ensue rides are not accepted by multiple drivers
    if order_accept.status == "accepted":
        flash("Oopss! Order Accepted by another rider...", category="error")
        return redirect(url_for("partner_dashboard"))
    else:
        order_accept.status = 'accepted'
        order_accept.driver_id = accepted_by
        order_accept.accepted_by = accepted_by
        try:
            db.session.commit()
            flash("Order Accepted!", category='success')
            return redirect(url_for("partner_dashboard"))
        except:
            flash("oops, There was an error accepting this order...", category='error')
        
    return redirect(url_for("partner_dashboard"))




    
    
# this is the main home landing page
# i will create a column on the database to generate and store tracking id which the user can always track their package
@app.route("/", methods=["POST", "GET"])
@app.route("/home", methods=["POST", "GET"])
def home():
    form = RequestOrderForm(request.form)
    blog_posts = Post.query.order_by(Post.id.desc()).paginate(per_page=2)
    # if session['type'] == "NONE" or "none":
    #     pass
    #ses = session['type']
    
    
    # redirect to home page if the user current session is "partner"
    # if session['type'] == "partner":
    #     flash("You Must login as a User to access this page", category="error")
    #     return redirect(url_for("login"))
    
    
    return render_template("index.html", 
                            blog_posts=blog_posts, 
                            form=form)
    
    

@app.route("/user-dash", methods=["POST", "GET"])
@login_required
def user_dash():
    
    if session['type'] != 'user':
        flash("You currently do not have permission to access this page!", category='error')
        return redirect(url_for('home'))
    
    # query db to get particular user ride requests
    user_id = current_user.id
    order_qry = Orders.query.filter(Orders.order.has(id=user_id)).order_by(Orders.id.desc()).all()

    #values in naira
    basecharge = 300
    cost_per_min = 30
    cost_per_km = 70 

    timestamp = datetime.now()

    form = RequestOrderForm(request.form)
    
    if request.method == "POST" and form.validate:
        
        address = form.pickup.data
        address2 = form.dropoff.data

        #get location and convert input to lon,lat
        location = requests.request("GET", f"https://api.tomtom.com/search/2/search/{address}%20abuja.json?key=JoBjMY24siY0bENUY5g52SLXouAaf4FX")
        location2 = requests.request("GET", f"https://api.tomtom.com/search/2/search/{address2}%20abuja.json?key=JoBjMY24siY0bENUY5g52SLXouAaf4FX")
        response = location.json()
        response2 = location2.json()
        #query the json and get the lat and lon
        lat = response['results'][0]['position']['lat']
        lon = response['results'][0]['position']['lon']
        
        lat2 = response2['results'][0]['position']['lat']
        lon2 = response2['results'][0]['position']['lon']
        
        
        # TEST TOM TOM API
        url = "https://api.tomtom.com/routing/matrix/2"

        querystring = {"key":"JoBjMY24siY0bENUY5g52SLXouAaf4FX"}

        payload = {
            "origins": [{"point": {
                        "latitude": lat,
                        "longitude": lon
                    }}],
            "destinations": [{"point": {
                        "latitude": lat2,
                        "longitude": lon2
                    }}],
            "options": {
                "departAt": "now",
                "routeType": "fastest",
                "traffic": "live",
                "travelMode": "car",
                "vehicleMaxSpeed": 80,
                "vehicleWeight": 0,
                "vehicleAxleWeight": 0,
                "vehicleLength": 0,
                "vehicleWidth": 0,
                "vehicleHeight": 0,
                "vehicleCommercial": False
            }
        }
        headers = {"Content-Type": "application/json"}

        request2 = requests.request("POST", url, json=payload, headers=headers, params=querystring)
        response2 = request2.json()
        
        #query the json and get the travel distance and time
        testdistance_api = response2['data'][0]['routeSummary']['lengthInMeters']
        testtime_api = response2['data'][0]['routeSummary']['travelTimeInSeconds']
        
        #format the values and round to whole number
        testdistance = (round(testdistance_api /1000))
        testtime = (round(testtime_api /60))
        
        #calculate the cost formular 
        testcost1 = int(testdistance *cost_per_km) + int(testtime *cost_per_min) + int(basecharge)
        testcost = format_number_with_commas(testcost1)
        
        timestamp = datetime.now()
        minutes_ago = calculate_time_difference(timestamp)
        time_ago = display_time_ago(minutes_ago)
        
        try:
            # Add new order to db
            order = Orders(placed_by=user_id,
                        pickup=address,
                        dropoff=address2,
                        user_id=user_id,
                        delivery_time=testtime,
                        delivery_distance=testdistance,
                        delivery_cost=testcost,
                        pickup_coord=lat+lon,
                        dropoff_coord=lat2+lon2,
                        placed_by_id=time_ago)
            db.session.add(order)
            db.session.commit()
            flash("Order Request Created Successfully!", category='success')
        except:
            flash("Oops, there was an error somewhere...", category='error')
            

    return render_template("user-dash.html",
                           order_qry=order_qry,
                           form=form,
                           timestamp=timestamp)


# @app.route('/order/<int:order_id>/accept')
# def accept_order(order_id):
#     ride = Orders.query.get_or_404(order_id)
#     driver_id = 1  # Replace with the actual driver ID
#     ride.accept_ride(driver_id)
    
#     # Send driver details to the user
#     driver = Driver.query.get(driver_id)
#     driver_details = {
#         'name': driver.name,
#         'phone': driver.phone,
#         'vehicle': driver.vehicle
#     }
    
#     return jsonify(driver_details)


# @app.route('/order/<int:order_id>/reject')
# def reject_order(order_id):
#     ride = Ride.query.get_or_404(order_id)
#     ride.reject_ride()
#     return redirect('/')

# this is meant to be the directions page for the rider receiving the package
@app.route("/contact")
def contact():
    return render_template("index9.html")



@app.route("/api", methods=["POST", "GET"])
def test():
    url = "https://api.mapbox.com/styles/v1/examples/cjikt35x83t1z2rnxpdmjs7y7?access_token=pk.eyJ1IjoiaXNyYWVsZGtuIiwiYSI6ImNsZ2I5ajg5dzAxc2EzZ3BnYzJsYzFidWMifQ.kHIs7ohcJ-ddu250O92saw"
    res = requests.get(url).json()
    rep = print(res)
    api1 = {
        res['zoom']
    }
    return render_template("api.html", api1=api1)
    
    
    

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404



@socketio.on("message")
def message(data):
    room = session.get("room")
   
    content = {
        "name": session.get("name"),
        "message": data["data"]
    }
    send(content, to=room)
    #rooms[room]["messages"].append(content)
    print(f"{session.get('name')} said: {data['data']}")


@socketio.on("connect")
def connect(auth):
    if session['type'] == "partner":
        idd = current_user.id
        partner = PartnerSignup.query.get(idd)
        join_room(partner)


@socketio.on("disconnect")
def disconnect():
    if session['type'] == "partner":
        idd = current_user.id
        partner = PartnerSignup.query.get(idd)
        leave_room(partner)



if __name__ == '__main__':
    app.run(debug=True)
