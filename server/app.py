#!/usr/bin/env python3

from flask import Flask, make_response, jsonify, request
from flask_migrate import Migrate
from flask_restful import Api, Resource

from models import db, Restaurant, RestaurantPizza, Pizza

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

class Restaurants(Resource):
    def get(self):
        restaurant_dicts = [restaurant.to_dict() for restaurant in Restaurant.query.all()]

        return make_response(
            restaurant_dicts,
            200
        )
    
api.add_resource(Restaurants, '/restaurants')


class RestaurantById(Resource):
    def get(self, id):
        restaurant = Restaurant.query.filter_by(id=id).first()

        if not restaurant:
            return make_response({ "error": "Restaurant not found"}, 404)
        
        return make_response(
            restaurant.to_dict(rules=('pizzas',)),
            200
        )
    
    def delete(self, id):
        restaurant = Restaurant.query.filter_by(id=id).first()

        if not restaurant:
            return make_response({ "error": "Restaurant not found"}, 404)
        
        restaurant_pizzas = RestaurantPizza.query.filter_by(restaurant_id=id).all()
        for restaurant_pizza in restaurant_pizzas:
            db.session.delete(restaurant_pizza)
        db.session.delete(restaurant)
        db.session.commit()

        return make_response({ "success": "" }, 200)
    
api.add_resource(RestaurantById, '/restaurants/<int:id>')

class Pizzas(Resource):
    def get(self):
        pizza_dicts = [pizza.to_dict() for pizza in Pizza.query.all()]

        return make_response(
            pizza_dicts,
            200
        )
    
api.add_resource(Pizzas, '/pizzas')

class RestaurantPizzas(Resource):
    def post(self):
        try:
            new_restaurantPizza = RestaurantPizza(
                price=request.get_json()['price'],
                pizza_id=request.get_json()['pizza_id'],
                restaurant_id=request.get_json()['restaurant_id']
            )

            db.session.add(new_restaurantPizza)
            db.session.commit()

            return make_response(
                new_restaurantPizza.pizza.to_dict(),
                201
            )
        
        except ValueError:
            return make_response({ "error": "Invalid input" }, 400)
        
api.add_resource(RestaurantPizzas, '/restaurant_pizzas')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
