from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
import random


app = Flask(__name__)

# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
db = SQLAlchemy()
db.init_app(app)


# Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)


with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/random_cafe")
def get_random_cafe():
    all_cafe = db.session.execute(db.select(Cafe)).scalars().all()
    chosen_cafe = random.choice(all_cafe)

    cafe_data = {
        "name": chosen_cafe.name,
        "map_url": chosen_cafe.map_url,
        "img_url": chosen_cafe.img_url,
        "location": chosen_cafe.location,
        "seats": chosen_cafe.seats,
        "has_toilet": chosen_cafe.has_toilet,
        "has_wifi": chosen_cafe.has_wifi,
        "has_sockets": chosen_cafe.has_sockets,
        "can_take_calls": chosen_cafe.can_take_calls,
        "coffee_price": chosen_cafe.coffee_price
    }
    return jsonify(cafe_data)


@app.route("/all")
def get_all():
    all_cafe = db.session.execute(db.select(Cafe)).scalars().all()
    cafe_data = []
    for cafe in all_cafe:
        cafe_data.append({
            "id": cafe.id,
            "name": cafe.name,
            "map_url": cafe.map_url,
            "img_url": cafe.img_url,
            "location": cafe.location,
            "seats": cafe.seats,
            "has_toilet": cafe.has_toilet,
            "has_wifi": cafe.has_wifi,
            "has_sockets": cafe.has_sockets,
            "can_take_calls": cafe.can_take_calls,
            "coffee_price": cafe.coffee_price
        })
    return jsonify(cafe_data)


@app.route("/search")
def search():
    query = request.args.get("loc")
    all_cafes = db.session.execute(db.select(Cafe).where(Cafe.location == query)).scalars().all()

    cafe_data=[]
    if all_cafes:
        for cafe in all_cafes:
            cafe_data.append({
                "id": cafe.id,
                "name": cafe.name,
                "map_url": cafe.map_url,
                "img_url": cafe.img_url,
                "location": cafe.location,
                "seats": cafe.seats,
                "has_toilet": cafe.has_toilet,
                "has_wifi": cafe.has_wifi,
                "has_sockets": cafe.has_sockets,
                "can_take_calls": cafe.can_take_calls,
                "coffee_price": cafe.coffee_price
            })
        return jsonify(cafe_data)

    else:
        return jsonify(erorr={"Not found": "Sorry we don't have any data for the cafe in this location"}), 404


@app.route("/add", methods=['GET', 'POST'])
def add_cafe():
    try:
        if request.method == "POST":
            new_cafe = Cafe(name=request.form['name'], map_url=request.form['map_url'], img_url=request.form['img_url'], location=request.form['location'], seats=request.form['seats'], has_toilet=bool(request.form['has_toilet']), has_wifi=bool(request.form['has_wifi']), has_sockets=bool(request.form['has_sockets']), can_take_calls=bool(request.form['can_take_calls']), coffee_price=request.form['coffee_price'])
            db.session.add(new_cafe)
            db.session.commit()
            return jsonify(message={"message": "User added Successfully"})
    except Exception as e:
        db.session.rollback()
        return jsonify(Error={"Message": f"Error adding cafe: {str(e)}"}), 500

    return jsonify(Error={"Message": "This Method is not allowed here"})


@app.route("/update-price/<cafe_id>", methods=['PATCH'])
def update_prize(cafe_id):
    if request.method == "PATCH":
        new_price = request.form['price']
        cafe = db.session.execute(db.select(Cafe).where(Cafe.id == cafe_id)).scalar()
        if cafe:
            cafe.coffee_price = new_price
            db.session.commit()
            return jsonify(Message={"Success": "Price updated successfully"}), 200
        return jsonify(Error={"Message": "Cafe with this id doesn't exist"}), 404

    return jsonify(Error={"Message": "This Method is not allowed here"}), 405


@app.route("/report-closed/<cafe_id>", methods=['DELETE'])
def close_cafe(cafe_id):
    api_key = "TOPSECRETKEYOFMOHIT"
    if request.method == 'DELETE':
        query = request.args.get("api-key")
        cafe = db.session.execute(db.select(Cafe).where(Cafe.id == cafe_id)).scalar()
        if cafe:
            if query == api_key:
                db.session.delete(cafe)
                db.session.commit()
                return jsonify(Message={"Success": "This Cafe is now removed"}), 200
            return jsonify(Error={"Message": "You are not Authorized to do this"}), 403
        return jsonify(Error={"Message": "Cafe with this id doesn't exist"}), 404
    return jsonify(Error={"Message": "This Method is not allowed here"}), 405


if __name__ == '__main__':
    app.run(debug=True)
