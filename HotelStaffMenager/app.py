from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask import request, redirect, url_for, render_template
from flask_security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin, login_required

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://ieranesk:K7cR_v0fvj4wFJBSs1hF1f0DJmY9B_Zb@elmer.db.elephantsql.com:5432/ieranesk'
app.config['SECRET_KEY'] = 'super-secret'
app.config['SECURITY_REGISTERABLE'] = True
app.debug = True
app.config['SECURITY_PASSWORD_HASH'] = 'bcrypt'
app.config['SECURITY_PASSWORD_SALT'] = '$2a$16$PnnIgfMwkOjGX4SkHqSOPO'
db = SQLAlchemy(app)

roles_users = db.Table('roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))


class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(30))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    first_name = db.Column(db.String(30), unique=True)
    last_name = db.Column(db.String(30), unique=True)
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))


class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    color = db.Column(db.String(80), unique=True)
    number = db.Column(db.Integer, unique=True)
    max_people = db.Column(db.Integer)
    extra_places = db.Column(db.Integer)
    bath = db.Column(db.Boolean)
    shower = db.Column(db.Boolean)
    dog = db.Column(db.Boolean)
   # stays = db.relationship('Stay', backref=db.backref('room'))

    def __init__(self, color, number, max_people, extra_places, bath, shower, dog):
        self.color = color
        self.number = number
        self.max_people = max_people
        self.extra_places = extra_places
        self.bath = bath
        self.shower = shower
        self.dog = dog

    def _repr_(self):
        return '<Room %r>' % self.color


class Guest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(30), unique=True)
    phone = db.Column(db.String(12), unique=True)
    first_name = db.Column(db.String(30))
    last_name = db.Column(db.String(30))
  #  stays = db.relationship('Stay', backref=db.backref('guest'))

    def __init__(self, email, first_name, last_name, phone):
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.phone = phone

    def _repr_(self):
        return '<Guest %r>' % self.email


class Stay(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start_at = db.Column(db.DateTime())
    end_at = db.Column(db.DateTime())
    guest_id = db.Column(db.Integer, db.ForeignKey('guest.id'))
    guest = db.relationship('Guest')
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'))
    room = db.relationship('Room')
    num_of_people = db.Column(db.Integer)

    def __init__(self, start_at, end_at, guest_id, room_id, people):
        self.start_at = start_at
        self.end_at = end_at
        self.guest_id = guest_id
        self.room_id = room_id
        self.num_of_people = people


# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/profile/<email>')
@login_required
def profile(email):
    user = User.query.filter_by(email=email).one_or_none()
    return render_template('profile.html', user=user)


@app.route('/post_user', methods=['POST'])
@login_required
def post_user():
    user = User(request.form['email'], request.form['password'], request.form['first_name'], request.form['last_name'])
    db.session.add(user)
    db.session.commit()
    return redirect(url_for('/'))


@app.route('/rooms/<color>')
@login_required
def room_info(color):
    room = Room.query.filter_by(color=color).one_or_none()
    if room is None:
        return render_template('/404.html')
    else:
        return render_template('rooms/room_info.html', room=room)


@app.route('/rooms')
@login_required
def rooms():
    rooms_list = Room.query.all()
    if rooms_list == []:
        return render_template('rooms/sorry.html')
    else:
        return render_template('rooms/rooms.html', rooms=rooms_list)


@app.route('/new_room', methods=['GET'])
@login_required
def new_room():
    return render_template('/rooms/new.html')


def checkbox_value(f):

    if request.form.getlist(f) == ['on']:
        return True
    else:
        return False


@app.route('/new_room', methods=['POST'])
@login_required
def create_room():

    room = Room(request.form['color'],request.form['number'], request.form['max_people'], request.form['extra_people'],
                checkbox_value('bath'), checkbox_value('shower'), checkbox_value('dog'))
    db.session.add(room)
    db.session.commit()
    return redirect(url_for('rooms'))


@app.route('/new_guest', methods=['GET'])
@login_required
def new_guest():
    return render_template('/guests/new.html')


@app.route('/new_guest', methods=['POST'])
@login_required
def create_guest():
    guest = Guest(request.form['email'], request.form['first_name'], request.form['last_name'], request.form['phone'])
    db.session.add(guest)
    db.session.commit()
    return redirect(url_for('guests'))


@app.route('/guests')
@login_required
def guests():
    guests_list = Guest.query.all()
    if guests_list == []:
        return render_template('guests/sorry.html')
    else:
        return render_template('guests/guests.html', guests=guests_list)


@app.route('/guests/<id>')
@login_required
def guest_info(id):
    guest = Guest.query.filter_by(id=id).one_or_none()
    stays = Stay.query.filter_by(guest_id=id)
    if guest is None:
        return render_template('/404.html')
    else:
        return render_template('guests/guest_info.html', guest=guest, stays=stays)


@app.route('/new_stay/<guest_id>', methods=['GET'])
@login_required
def new_stay(guest_id):
    return render_template('stays/new.html', guest=Guest.query.filter_by(id=guest_id).one_or_none())


@app.route('/new_stay/<guest_id>', methods=['POST'])
def create_stay(guest_id):
    color = request.form['room']
    room = Room.query.filter_by(color=color).one_or_none()
    room_id = room.id
    stay = Stay(request.form['start'], request.form['end'], guest_id, room_id, request.form['people'])
    db.session.add(stay)
    db.session.commit()
    return redirect(url_for('stays'))


@app.route('/stays')
@login_required
def stays():
    stays_list = Stay.query.all()
    if stays_list == []:
        return render_template('stays/sorry.html')
    else:
        return render_template('stays/stays.html', stays=stays_list)


if __name__ == "__main__":
    app.run()
