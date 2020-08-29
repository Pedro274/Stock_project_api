"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Portfolio
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code


@app.route('/')
def sitemap():
    return generate_sitemap(app)



#This endpoint will create a new user and save it in the database (the user will need to send username, password and email in the body of the request)
@app.route('/register_user', methods=['POST'])
def handle_register_user():
    request_data= request.get_json()
    user = User.query.filter_by(username=request_data['username']).first()
    if user:
        return jsonify({'message': 'username already exists'}), 409
    new_user = User(
        username=request_data["username"],
        email = request_data["email"],
        password = request_data["password"],
        is_active = True)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({
        "msg": "User was created"
    }), 200


#This endpoint gets all the users from the data base
@app.route('/users', methods=['GET'])
def get_all_users():
    users_query = User.query.all()
    all_users = list(map(lambda x: x.serialize(), users_query))
    return jsonify({
        "message": "This are all the available user",
        "users": all_users
    }), 200


#This endpoint gets one user (the user will need to send username and password in the body of the request)
@app.route('/login', methods=['POST'])
def handle_login():
    request_data = request.get_json()
    email = request_data["email"]
    users_query = User.query.filter_by(email=email).first()
    if users_query:
        return jsonify(users_query.serialize()), 200 
    return jsonify({"Message":"User not found"}), 404



#This endpoint will create a new portfolio (user need to provide symbol, companyName, price, shares and totalReturn in the body of the request ), the user_id needs to be in the url
@app.route('/portfolio/<user_id>', methods=['POST'])
def post_portfolio(user_id):
    request_data= request.get_json()
    stock = Portfolio.query.filter_by(companyName=request_data["companyName"]).filter_by(user_id=user_id).first()
    if stock:
        return jsonify({"message": "user already bought this stock"})
    stock_added= Portfolio(
        symbol = request_data["symbol"],
        companyName = request_data["companyName"],
        price = request_data["price"],
        shares = request_data["shares"],
        totalReturn = request_data["totalReturn"],
        user_id = user_id 
    )
    db.session.add(stock_added)
    db.session.commit()
    return jsonify({
        "msg": "Stock Added "
    }), 201


#This endpoint will find one specific portfolio by id (include the portfolio id in the url)
@app.route('/portfolio/<id>', methods=['GET'])
def get_portfolio(id):
    user_portfolio= Portfolio.query.filter_by(id=id).first()
    if user_portfolio:
        return jsonify({"portfolio": user_portfolio.serialize()}), 200
    return jsonify({"message": "Add stocks to your portfolio"}), 404
        

#This endpoint will find one specific portfolio by id and delete it (include the portfolio id in the url)
@app.route('/portfolio/<id>', methods=['DELETE'])
def handle_portfolio(id):
    stock_sold = Portfolio.query.filter_by(id=id).first()
    if stock_sold:
        db.session.delete(stock_sold)
        db.session.commit()
        return jsonify({
            "msg": "Stock Sold "
        }), 200
    return jsonify({"message":"Stock not found" }), 404


if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
