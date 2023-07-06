import datetime
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from itsdangerous import URLSafeTimedSerializer as Serializer
from models.Models import db, User, Team, Role, Permission, RolePermissions
from sqlalchemy.exc import IntegrityError


app = Flask(__name__)

CORS(app)  # aktiviert CORS für die gesamte App

app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{os.environ.get('DB_USERNAME')}:{os.environ.get('DB_PASSWORD')}@localhost/kapa_website"
# Sie sollten hier einen sicheren, geheimen Schlüssel setzen
app.config['SECRET_KEY'] = 'your-secret-key'

db.init_app(app)

with app.app_context():
    db.create_all()


@app.route('/')
def home():
    return "Hallo, das ist die Hauptseite meiner Flask-App!"


@app.route('/user', methods=['POST'])
def create_user():
    if not request.is_json:
        return {'message': 'No JSON data provided.'}, 400

    data = request.get_json()
    username = data.get('Username')
    email = data.get('Email')
    password = data.get('Password')

    # Validate username and email
    existing_user = User.query.filter_by(Username=username).first()
    if existing_user:
        return {'message': 'Username already in use'}, 400

    existing_email = User.query.filter_by(Email=email).first()
    if existing_email:
        return {'message': 'Email already in use'}, 400

    # Validate password
    if password is None:
        return {'message': 'No password provided.'}, 400

    if len(password) < 8 or not any(char.isdigit() for char in password):
        return {'message': 'Password must be at least 8 characters and contain a number'}, 400

    # If validations pass, create the user
    new_user = User(
        Username=username,
        Email=email
    )
    new_user.set_password(password)
    new_user.CreatedAt = datetime.datetime.utcnow()
    try:
        db.session.add(new_user)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({'message': 'Username already exists.'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'An error occurred while creating the User.'}), 500
    return jsonify(new_user.serialize()), 201


@app.route('/user/<int:user_id>', methods=['GET'])
def read_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404
    return jsonify(user.serialize()), 200


@app.route('/user/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    if not request.is_json:
        return jsonify({'message': 'No input data provided'}), 400

    data = request.get_json()
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    username = data.get('Username')
    email = data.get('Email')
    password = data.get('Password')

    # Check for existing username
    if username:
        existing_user = User.query.filter_by(Username=username).first()
        if existing_user and existing_user.User_ID != user_id:
            return jsonify({'message': 'Username already in use'}), 400
        user.Username = username

    # Check for existing email
    if email:
        existing_email = User.query.filter_by(Email=email).first()
        if existing_email and existing_email.User_ID != user_id:
            return jsonify({'message': 'Email already in use'}), 400
        user.Email = email

    # Check for password
    if password:
        if len(password) < 8 or not any(char.isdigit() for char in password):
            return jsonify({'message': 'Password must be at least 8 characters and contain a number'}), 400
        user.set_password(password)

    db.session.commit()
    return jsonify(user.serialize()), 200


@app.route('/user/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return {'message': 'User not found.'}, 404
    db.session.delete(user)
    db.session.commit()
    return {'message': 'User successfully deleted.'}


@app.route('/team', methods=['POST'])
def create_team():
    data = request.get_json()
    team_name = data.get('TeamName')
    if Team.query.filter_by(TeamName=team_name).first():
        return jsonify({'message': 'Team name already exists.'}), 400
    if not isinstance(team_name, str) or len(team_name) < 1:
        return jsonify({'message': 'Invalid team name.'}), 400
    new_team = Team(TeamName=team_name)
    try:
        db.session.add(new_team)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({'message': 'Team name already exists.'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'An error occurred while creating the team.'}), 500

    return jsonify(new_team.serialize()), 201


@app.route('/team/<int:team_id>', methods=['GET'])
def read_team(team_id):
    team = Team.query.get(team_id)
    if not team:
        return jsonify({'message': 'Team not found'}), 404
    return jsonify(team.serialize()), 200


@app.route('/team/<int:team_id>', methods=['PUT'])
def update_team(team_id):
    data = request.get_json()
    team = Team.query.get(team_id)
    team_name = data.get('TeamName')
    if not team:
        return jsonify({'message': 'Team not found'}), 404
    if not isinstance(team_name, str) or len(team_name) < 1:
        return jsonify({'message': 'Invalid team name.'}), 400
    team.TeamName = data.get('TeamName', team.TeamName)
    db.session.commit()
    return jsonify(team.serialize()), 200


@app.route('/team/<int:team_id>', methods=['DELETE'])
def delete_team(team_id):
    team = Team.query.get(team_id)
    if not team:
        return jsonify({'message': 'Team not found'}), 404
    db.session.delete(team)
    db.session.commit()
    return jsonify({'message': 'Team successfully deleted.'}), 200


if __name__ == '__main__':
    app.run(debug=True)
