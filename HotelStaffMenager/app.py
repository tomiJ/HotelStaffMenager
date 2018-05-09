from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask import request, redirect, url_for, render_template
from flask_security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin, login_required

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://ukpesblq:0-iHLK1g9r2_KB_jynCgCHOnQ7nepKcO@dumbo.db.elephantsql.com:5432/ukpesblq'
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
    description = db.Column(db.String(255))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    first_name = db.Column(db.String(255), unique=True)
    last_name = db.Column(db.String(255), unique=True)
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))


class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    color = db.Column(db.String(80), unique=True)
    max_people = db.Column(db.Integer)
    stays = db.relationship('Stay', backref=db.backref('room'))

    def __init__(self, color, max_people):
        self.color = color
        self.max_people = max_people

    def _repr_(self):
        return '<Room %r>' % self.color


class Guest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    stays = db.relationship('Stay', backref=db.backref('guest'))

    def __init__(self, email, first_name, last_name):
        self.email = email
        self.first_name = first_name
        self.last_name = last_name

    def _repr_(self):
        return '<Guest %r>' % self.email


class Stay(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start_at = db.Column(db.DateTime())
    end_at = db.Column(db.DateTime())
    guest_id = db.Column(db.Integer, db.ForeignKey('guest.id'))
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'))

    def __init__(self, id, start_at, end_at):
        self.id = id
        self.start_at = start_at
        self.end_at = end_at


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


@app.route('/new_room', methods=['POST'])
@login_required
def create_room():
    room = Room(request.form['color'], request.form['max_people'])
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
    guest = Guest(request.form['email'], request.form['first_name'], request.form['last_name'])
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
    if guest is None:
        return render_template('/404.html')
    else:
        return render_template('guests/guest_info.html', guest=guest)


@app.route('/guest/<id>/new_stay', methods=['GET'])
@login_required
def new_stay(id):
    return render_template('/stays/new.html')


@app.route('/guest/<id>/new_stay', methods=['POST'])
@login_required
def create_stay():

    guest = Guest.query.filter_by(id=request.form['id']).one_or_none()
    if guest is None:
        return render_template('/404.html')
    else:
        room = Room.query.filter_by(color=color).one_or_none()
        if room is None:
            return render_template('/rooms/sorry.html')
        stay = Stay()
        db.session.add(guest_stays)
        db.session.add(room_stays)
        db.session.add(stay)


if __name__ == "__main__":
    app.run()
