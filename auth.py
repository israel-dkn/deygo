from flask import Flask, Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date, timedelta
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, RadioField
from wtforms.validators import ValidationError, DataRequired
from os import path
import requests
from flask_login import login_user, UserMixin, LoginManager, login_required, logout_user, current_user
import random, string
import json
from flask_socketio import SocketIO, emit, join_room, leave_room, send
from flask_migrate import Migrate
import math
from functools import wraps




db = SQLAlchemy()
app = Flask(__name__)
migrate = Migrate(app, db)
# app.register_blueprint(rider_page, url_prefix='/rider')
DB_NAME = "database.db"
site_name="DEY GO"
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_NAME}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
paystack_secret_key = 'sk_test_528e1a3543582b47f670ae934becaff87fb12dca'
secret_key = "IgVnWnSwmS0LN4RtKaaCubIiFCG2Iq0FSFDqJaboBy0eXHakp0jHFQ"
app.config["SECRET_KEY"] = "my secret key"
tomtom_admin_key = "PUuQt6512jSNCD3gdu00VxzYAsKQ7VDo2XrJoPvGhhhNoSl0"
tomtom_api_key = "JoBjMY24siY0bENUY5g52SLXouAaf4FX"
async_mode = None
#socketio = SocketIO(app, async_mode=async_mode)
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

def login_required_partner(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if session.get('type') == None:
            flash("Login to access this page", category="error")
            return redirect(url_for("login"))
        if session.get('type') != 'partner':
            flash(f"Hello {current_user.first_name}, You must be a partner to access this page!", category="error")
            return redirect(url_for("user_dash"))
        return view_func(*args, **kwargs)
    return wrapper


def login_required_user(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if session.get('type') == None:
            flash("Login to access this page", category="error")
            return redirect(url_for("login"))
        if session.get('type') != 'user':
            flash(f"Hello {current_user.username}, You do not have permission to access this URL!", category="error")
            return redirect(url_for("partner_dashboard"))
        return view_func(*args, **kwargs)
    return wrapper


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
    delivery_cost = db.Column(db.Integer) 
    pickup_lat = db.Column(db.Float)
    pickup_lon = db.Column(db.Float)
    dropoff_lat = db.Column(db.Float)
    dropoff_lon = db.Column(db.Float)
    test_col = db.Column(db.String) 
    delivery_mode = db.Column(db.String, default="bike") 
    placed_by_id = db.Column(db.String) #placed_by=current_user.id
    time_created = db.Column(db.DateTime, default=datetime.now)
    track_id = db.Column(db.String, default=ran_id)
    status = db.Column(db.String(20), default='pending') 
    available_riders = db.Column(db.Integer)
    driver_id = db.Column(db.Integer, db.ForeignKey('partnersignup.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('usersignup.id'))
    accepted_by = db.Column(db.String)
    date_edited = db.Column(db.DateTime)
    
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
    date_registered = db.Column(db.DateTime, default=datetime.utcnow)
    username = db.Column(db.String)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String)
    con_password = db.Column(db.String)
    good_review = db.Column(db.Integer, default=0)
    bad_review = db.Column(db.Integer, default=0)
    driver_lat = db.Column(db.Float)
    driver_lon = db.Column(db.Float)
    driver_status = db.Column(db.String(20), default='available') # on-ride, offline
    delivery_status = db.Column(db.String(20), default='null')
    date_edited = db.Column(db.DateTime)
    driver = db.relationship('Orders', backref='partner')
    
    


class UserSignup(db.Model, UserMixin):
    __tablename__ = 'usersignup'
    
    id = db.Column(db.Integer, primary_key=True)
    date_registered = db.Column(db.DateTime, default=datetime.utcnow)
    user_account_balance = db.Column(db.Integer)
    first_name = db.Column(db.String(20), nullable=False)
    last_name = db.Column(db.String(20))
    address = db.Column(db.String)
    phone = db.Column(db.Integer, unique=True, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String)
    con_password = db.Column(db.String)
    user_lat = db.Column(db.Float)
    user_lat = db.Column(db.Float)
    date_edited = db.Column(db.DateTime)
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
    f_name = StringField('Your Name', validators=[DataRequired()])
    l_name = StringField('Your Name', validators=[DataRequired()])
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
    delivery_mode = RadioField("car", choices=[('value','description')])
    submit = SubmitField("Request Dispatch")


class TrackTestForm(FlaskForm):
    title = StringField("Title")
    submit = SubmitField("Register")
    

class CreditForm(FlaskForm):
    amount = StringField("Amount")
    submit = SubmitField("Credit")



# <---- END FORM CLASS ---->


#
#
#
#
#
#
 
# <---- All test routes will go here ---->

@app.route("/rider/go-offline")
@login_required_partner
def go_offline():
    partner_id = current_user.id
    partner_stat = PartnerSignup.query.get(partner_id)
    last_order_count = Orders.query.filter_by(driver_id=partner_id, status='accepted').order_by(Orders.id.desc()).count()
    
    
    if last_order_count > 1:
        flash("Unable to go OFFLINE! Complete pending rides to go Offline...", category="error")
        return redirect(url_for("dashboard_rides"))
    else:
        partner_stat.driver_status = 'offline'
        
        try:
            db.session.commit()
        except:
            flash("oops, There was an error updating your status", category='error')
        
        return redirect(url_for("partner_dashboard"))


@app.route("/rider/go-online")
@login_required_partner
def go_online():
    
    partner_id = current_user.id
    partner_stat = PartnerSignup.query.get(partner_id)
    
    partner_stat.driver_status = 'available'
    
    try:
        db.session.commit()
    except:
        flash("oops, There was an error updating your status", category='error')
    
    return redirect(url_for("partner_dashboard"))



@app.route("/rider/order/complete/<int:id>")
@login_required_partner
def order_complete(id):
    orders = Orders.query.get(id)
    partner_id = current_user.id
    partner_stat = PartnerSignup.query.get(partner_id)
    
    total = format_number_with_commas(orders.delivery_cost)
    
    
    partner_stat.driver_status = 'available'
    orders.status = "completed"
    
    try:
        db.session.commit()
    except:
        flash("oops, There was an error updating your status", category='error')
    
    flash("Order Completed! N{} has been added to your balance".format(total), category='success')
    return redirect(url_for("partner_dashboard"))


@app.route("/rider/order/details/<int:id>")
@login_required_partner
def order_details(id):
    
    orders = Orders.query.get(id)
    access = orders.driver_id
    
    if current_user.id == access:
        timestamp = datetime.now()
        partner_id = current_user.id
        
        partner_loc = PartnerSignup.query.get(partner_id)
        
        new_coord = Orders.query.filter(Orders.order.has(id=partner_id))
        
        # get driver location and get the pickup location to get the ETA
        latitude = (float(partner_loc.driver_lat))
        longitude = (float(partner_loc.driver_lon))
        
        dst_latitude = (float(orders.pickup_lat))
        dst_longitude = (float(orders.pickup_lon))
        
        
        url = "https://api.tomtom.com/routing/matrix/2"

        querystring = {"key":"JoBjMY24siY0bENUY5g52SLXouAaf4FX"}

        payload = {
            "origins": [{"point": {
                        "latitude": latitude,
                        "longitude": longitude
                    }}],
            
            "destinations": [{"point": {
                        "latitude": dst_latitude,
                        "longitude": dst_longitude 
                    }}],
            
            "options": {
                "departAt": "now",
                "routeType": "fastest",
                "traffic": "live",
                "travelMode": "car",
                "vehicleMaxSpeed": 70,
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
        #testdistance_api = response2['data'][0]['routeSummary']['lengthInMeters']
        testtime_api = response2['data'][0]['routeSummary']['travelTimeInSeconds']
        
        #format the values and round to whole number
        #testdistance = (round(testdistance_api /1000))
        testtime = (round(testtime_api /60))
        
        
        return render_template("order-details.html",
                            orders=orders,
                            timestamp=timestamp,
                            testtime=testtime,
                            latitude=latitude,
                            dst_longitude=dst_longitude,
                            dst_latitude=dst_latitude,
                            longitude=longitude,
                            partner_loc=partner_loc)
    else:
        flash("Error...Not Allowed", category='error')
        return redirect(url_for("partner_dashboard"))



# Custom filter(var) to pass to jinja
def total_seconds_filter(td):
    return td.total_seconds()


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



# Register the custom filter
app.jinja_env.filters['total_seconds'] = total_seconds_filter
app.jinja_env.filters['format_number'] = format_number_with_commas

def calculate_time_difference(minutes_ago):
    current_time = datetime.now()
    time_difference = current_time - minutes_ago
    minutes = int(time_difference.total_seconds() / 60)
#     return minutes


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
            form_data = UserSignup(first_name=form.f_name.data,
                                   last_name=form.l_name.data,
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
            return redirect(url_for('user_dash'))
        else:
            flash("User email or password is incorrect! Try again...")
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
            flash("Partner email or password is incorrect! Try again...")
            form2.username.data = '' 
            form2.email.data = '' 
            form2.password.data = ''
        
           
    return render_template('login.html', form=form, form2=form2)




@app.route('/save_location', methods=['POST', 'GET'])
@login_required
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
        print(f"{new_coord.username} posted their location!")
    except:
        flash("oops, There was an error tracking your location", category='error')
    
    return 'Location saved successfully'


@app.route("/rider/view/<int:id>")
def view_driver(id):
    driver = PartnerSignup.query.get(id)
    orders_count = Orders.query.filter_by(driver_id=id, status='accepted').count()
    return render_template("view-driver.html",
                           driver=driver,
                           orders_count=orders_count)



@app.route("/company/my-rides", methods=["POST", "GET"], defaults={"page" : 1})
@app.route("/company/my-rides/<int:page>", methods=["POST", "GET"])
@login_required_partner
def dashboard_rides(page):
    partner_id = current_user.id
    ses = session['type']
    last_order = Orders.query.filter_by(driver_id=partner_id, status='accepted').order_by(Orders.id.desc()).first()
    order_qry = Orders.query.filter(Orders.partner.has(id=partner_id)).order_by(Orders.id.desc()).paginate(page=page, per_page=5)
    orders_sum = db.session.query(db.func.sum(Orders.delivery_cost)).filter_by(driver_id=current_user.id, status='completed').scalar()
    orders_count = Orders.query.filter_by(driver_id=partner_id, status='completed').count()
    orders_count_all = Orders.query.filter_by(driver_id=partner_id).count()
    timestamp = datetime.now()
              
    return render_template("driver-my-rides.html",
                           last_order=last_order,
                           order_qry=order_qry,
                           orders_sum=orders_sum,
                           orders_count=orders_count,
                           timestamp=timestamp,
                           ses=ses,
                           orders_count_all=orders_count_all)
    
    

@app.route("/company", methods=["POST", "GET"])
# @app.route("/company/<int:id>", methods=["POST", "GET"])
@login_required_partner
def partner_dashboard():
    # redirect to home page if the user current session is "user"
    partner_id = current_user.id
        
       
    # def a func to say, if rider current lat,lon == nearest_rider_index
    # automatically assign order to the particular rider
    ses = session['type']
    orders = Orders.query.filter_by(status='pending').order_by(Orders.id.desc())
    orders_count = Orders.query.filter_by(driver_id=partner_id, status='completed').count()
    orders_sum = db.session.query(db.func.sum(Orders.delivery_cost)).filter_by(driver_id=current_user.id, status='completed').scalar()
    order_qry = Orders.query.filter(Orders.partner.has(id=partner_id)).order_by(Orders.id.desc()).all()
    # last_order =  Orders.query.filter_by(driver_id=partner_id, status='pending').all()
    last_order = Orders.query.filter_by(driver_id=partner_id, status='accepted').order_by(Orders.id.desc()).first()
    
    last_order_count = Orders.query.filter_by(driver_id=partner_id, status='accepted').order_by(Orders.id.desc()).count()
    
    
    timestamp = datetime.now()
    
    # orders_sum = format_number_with_commas(orders_sum_req)

    # lat_lon = {}
    # records = PartnerSignup.query.all()
    # for lat_lons in records:
    #     lat_lon[lat_lons.id] = [ float(lat_lons.driver_lat), float(lat_lons.driver_lon)]
            
    # target_point = [9.052185, 7.485223]
    # nearest_point = None
    # min_distance = float('inf')

    # for point_name, coords in lat_lon.items():
    #     lat = coords[0]
    #     lon = coords[1]
    #     distance = ((lat - target_point[0]) ** 2 + (lon - target_point[1]) ** 2) ** 0.5
    #     if distance < min_distance:
    #         min_distance = distance
    #         nearest_point = point_name

    # nearest_coordinates = lat_lon[nearest_point]
    
    return render_template('company.html', 
                        orders=orders,
                        orders_count=orders_count,
                        ses=ses,
                        orders_sum=orders_sum, 
                        timestamp=timestamp,
                        order_qry=order_qry,
                        last_order=last_order,
                        last_order_count=last_order_count) 
    
    




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
@app.route("/rider/order/accept/<int:id>")
@login_required_partner
def order_accepted(id):
    accepted_by = current_user.id
    driver_stat = PartnerSignup.query.get(accepted_by)
    order_accept = Orders.query.get(id)
    access = order_accept.driver_id
    last_order_count = Orders.query.filter_by(driver_id=accepted_by, status='accepted').order_by(Orders.id.desc()).count()
        
    if driver_stat.driver_status == "offline":
        flash("Go online to accept new rides!", category="warning")
        return redirect(url_for("partner_dashboard"))
    elif order_accept.status == "accepted" and current_user.id != access:
        flash("Oopss! Order Accepted by another rider...", category="error")
        return redirect(url_for("partner_dashboard"))
    elif last_order_count > 2:
        flash("Oopss! Complete current rides to accept new ones!", category="error")
        return redirect(url_for("partner_dashboard"))
        # to ensure rides are not accepted by multiple drivers
    elif order_accept.status == "pending":
        order_accept.status = 'accepted'
        order_accept.driver_id = accepted_by
        order_accept.accepted_by = accepted_by
        driver_stat.driver_status = 'on-ride'
        try:
            db.session.commit()
            flash("Order Accepted!", category='success')
            return redirect(url_for("order_details", 
                                    id=id))
        except:
            flash("oops, There was an error accepting this order...", category='error')
    
    elif order_accept.status == "accepted" and current_user.id == access:
        flash("Order has already been accepted by you!")
        return redirect(url_for("order_details", 
                                    id=id))
   
    
    return redirect(url_for("order_details"))
    
   
@app.route("/cancel/request/<int:id>")
@login_required_user
def cancel_request(id):
    user_id = current_user.id
    cancel_request = Orders.query.get(id)
    
    
    if cancel_request.status == "accepted":
        flash("You cannot cancel this request, a rider has accepted it already...", category="error")
        return redirect(url_for("user_dash"))
    else:
        cancel_request.status = 'canceled'
        try:
            db.session.commit()
            flash(" Your Order has been canceled!", category='success')
            return redirect(url_for("user_dash"))
        except:
            flash("oops, There was an error canceling this order...", category='error')
        
    return redirect(url_for("user_dash"))




    
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
    


@app.route("/user-dash/credit-account/<int:id>/<int:amount>", methods=["POST", "GET"])
@login_required_user
def credit_account(id, amount):
    user_id = UserSignup.query.get(id)
    user_mail = str(user_id.email)
    
    if user_id:
        url_paystack = "https://api.paystack.co/transaction/initialize"

        payload_paystack = {
            "email": f"{user_mail}",
            "amount": f"{amount}00" 
        }
        headers_paystack = {
            "Authorization": " Bearer sk_test_528e1a3543582b47f670ae934becaff87fb12dca".strip(),
            "Content-Type": "application/json"
        }

        response_paystack = requests.request("POST", url_paystack, json=payload_paystack, headers=headers_paystack)
        print(response_paystack.text)
       
    return redirect(url_for("pay_credit_account"))


@app.route("/user-dash/credit-account/", methods=["POST", "GET"])
@login_required_user
def pay_credit_account():
    user_details = UserSignup.query.get(current_user.id)
   
    if request.method == "GET" and "trxref" in request.args:
        data_trxref = request.args.get("trxref")
        print(data_trxref)
        url_verify = f"https://api.paystack.co/transaction/verify/{data_trxref}"
        headers_paystack = {
            "Authorization": " Bearer sk_test_528e1a3543582b47f670ae934becaff87fb12dca".strip(),
            "Content-Type": "application/json"
        }

        response_pay_verify = requests.request("GET", url_verify, headers=headers_paystack)
        response_pay_verify_json = response_pay_verify.json()
        
        response_pay_verify_res = response_pay_verify_json["data"]["gateway_response"]
        print(response_pay_verify.text)
        print(response_pay_verify_res)
        if response_pay_verify_res == "Successful":
            response_pay_verify_amount = response_pay_verify_json["data"]["amount"]
        
            update_amount = int(str(response_pay_verify_amount)[:-2])
            
            user_details.user_account_balance = update_amount
            
            try:
                db.session.commit()
                flash(f"{update_amount} has been added to your balance!")
                return redirect(url_for("user-dash"))
            except:
                flash("oops, There was an error updating your account balance...", category='error')
            




@app.route("/user-dash", methods=["POST", "GET"])
@login_required_user
def user_dash():
    condition = True
    
    # query db to get particular user ride requests
    user_id = current_user.id
    order_qry = Orders.query.filter(Orders.order.has(id=user_id)).order_by(Orders.id.desc()).all()
    user_details = UserSignup.query.get(user_id)
   
    #values in naira
    basecharge = 300
    cost_per_min = 30
    cost_per_km = 70 
    
    #values in naira
    van_basecharge = 600
    
    #values in naira
    car_basecharge = 400
    
    timestamp = datetime.now()

    form = RequestOrderForm(request.form)
    credit_form = CreditForm(request.form)
    
    form.validate
    if request.method == "POST" and form.validate_on_submit():
        
        address = form.pickup.data
        address2 = form.dropoff.data
        
        delivery_mode = request.form.get("engine")

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
        
        #calculate the cost formula
        if delivery_mode == "bike":
            testcost = int(testdistance *cost_per_km) + int(testtime *cost_per_min) + int(basecharge)
        elif delivery_mode == "car":
            testcost = int(testdistance *cost_per_km) + int(testtime *cost_per_min) + int(car_basecharge)
        elif delivery_mode == "van":
            testcost = int(testdistance *cost_per_km) + int(testtime *cost_per_min) + int(van_basecharge)
        else:
            flash("selecect an option please", category="error")
        
        
        timestamp = datetime.now()
        
        
        lat_lon = {}
        riders_qry = PartnerSignup.query.filter_by(driver_status="available").all()
        for lat_lons in riders_qry:
            lat_lon[lat_lons.id] = [ float(lat_lons.driver_lat), float(lat_lons.driver_lon)]
                    
        pickup_coord = [float(lat), float(lon)]
        # nearest_rider = None
        # min_distance = float('inf')
        distances = {}
        for driver_id, coords in lat_lon.items():
            dri_lat = coords[0]
            dri_lon = coords[1]
            distance =  math.sqrt((pickup_coord[0] - dri_lat) ** 2 + (pickup_coord[1] - dri_lon) ** 2) 
            distances[driver_id] = distance
            
            sorted_riders = sorted(lat_lon.items(), key=lambda x: x[1])
            
            # Select the three nearest points
            nearest_riders = sorted_riders[:5]
            
            
            for riders, distance in nearest_riders:
                
                print(riders)
                
        
        print(nearest_riders)
    
        print(sorted_riders)
        try:
            # Add new order to db
            order = Orders(placed_by_id=user_id,
                        pickup=address,
                        dropoff=address2,
                        user_id=user_id,
                        delivery_time=testtime,
                        delivery_distance=testdistance,
                        delivery_cost=testcost,
                        pickup_lat=lat,
                        pickup_lon=lon,
                        dropoff_lat=lat2,
                        dropoff_lon=lon2,
                        available_riders=riders,
                        delivery_mode=delivery_mode)
            db.session.add(order)
            db.session.commit()
            flash("Order Request Created Successfully!", category='success')
        except:
            flash("Oops, there was an error placing that request...", category='error')
    
    if request.method == "POST" and credit_form.validate():
        return redirect(url_for("credit_account",
                                id=current_user.id,
                                amount=credit_form.amount.data))

        

    return render_template("user-dash.html",
                           order_qry=order_qry,
                           form=form,
                           timestamp=timestamp,
                           condition=condition,
                           credit_form=credit_form)


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


@app.errorhandler(500)
def svr_error(error):
    return render_template('500.html'), 500



# @socketio.on("message")
# def message(data):
#     room = session.get("room")
   
#     content = {
#         "name": session.get("name"),
#         "message": data["data"]
#     }
#     send(content, to=room)
#     #rooms[room]["messages"].append(content)
#     print(f"{session.get('name')} said: {data['data']}")


# @socketio.on("changed", namespace='/test')
# def changed(data):
#     orderqry = Orders.query.filter_by(status = "accepted").all()
#     message1 = "hello receiver"
#     for orders in orderqry:
#         if orders.status == 'accepted':
#             emit('status_changed', {'message': 'accept1.'})
#         elif orders.status == 'pending':
#             emit('status_changed', {'message': 'pending1.'})
#         else:
#             emit('status_changed', {'message': 'Declined1.'})

#     emit('changed', {'message1': message1}, broadcast=True)
#     print("sent msg")
    # for orderqrys in orderqry:
    #     if orderqrys.status == 'pending':
    #         emit('status_changed', {'message': 'Status changed to accept.'}, broadcast=True)
    #     else:
    #         emit('status_changed', {'message': 'Declined.'})
   
            


# @socketio.on("connect")
# def connect():
#     user_id = current_user.full_name
#     message1 = "hello receivr2"
#     print("connected frm" + user_id)
#     while True:
#         orderqry = Orders.query.filter(Orders.order.has(id=user_id)).filter_by(status='accepted').all()
#         for orders in orderqry:
#             if orders.status == 'accepted':
#                 emit('status_changed', {'message': 'accept.'})
#             elif orders.status == 'pending':
#                 emit('status_changed', {'message': 'pending.'})
#             else:
#                 emit('status_changed', {'message': 'Declined.'})

#         emit('changed', {'message1': message1}, broadcast=True)
        
#         socketio.sleep(12)
    


# @socketio.on("disconnect")
# def disconnect():
#     print("Disconnected frm")



if __name__ == '__main__':
    app.run(debug=True)
