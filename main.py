from flask import Flask, jsonify, render_template, request, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
import random


class NewCafe(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    map_url = StringField("Map_url", validators=[DataRequired()])
    img_url = StringField("Img_url", validators=[DataRequired()])
    location = StringField("Location", validators=[DataRequired()])
    seats = StringField("Seats", validators=[DataRequired()])
    toilet = StringField("Toilet", validators=[DataRequired()])
    wifi = StringField("wifi", validators=[DataRequired()])
    sockets = StringField("sockets", validators=[DataRequired()])
    calls = StringField("Calls", validators=[DataRequired()])
    coffee_price = StringField("Coffee_price", validators=[DataRequired()])
    submit = SubmitField("Add Cafe")


app = Flask(__name__)
# add it as a environment varible
app.secret_key = 'your_secret_key_here'
bootstrap = Bootstrap(app)

# Connect to Database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///cafes.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


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

    def to_dict(self):
        return {
            column.name: getattr(self, column.name) for column in self.__table__.columns
        }


@app.route("/")
def home():
    cafes = db.session.query(Cafe).all()
    return render_template("index.html", all_cafes=cafes)


@app.route("/random")
def get_random_caffe():
    cafes = db.session.query(Cafe).all()
    random_cafe = random.choice(cafes)
    return jsonify(
        cafe={
            "id": random_cafe.id,
            "name": random_cafe.name,
            "map_url": random_cafe.map_url,
            "img_url": random_cafe.img_url,
            "location": random_cafe.location,
            "seats": random_cafe.seats,
            "has_toilet": random_cafe.has_toilet,
            "has_wifi": random_cafe.has_wifi,
            "has_sockets": random_cafe.has_sockets,
            "can_take_calls": random_cafe.can_take_calls,
            "coffee_price": random_cafe.coffee_price,
        }
    )


@app.route("/all")
def get_all_cafes():
    cafes = db.session.query(Cafe).all()
    return jsonify(cafes=[cafe.to_dict() for cafe in cafes])


@app.route("/search")
def get_cafe_at_location():
    query_location = request.args.get("loc")
    cafes = Cafe.query.filter_by(location=query_location).all()
    if len(cafes) == 0:
        return jsonify(
            error={"Not Found": "Sorry, we don't have a cafe at that location."}
        )
    else:
        return jsonify(cafe=[cafe.to_dict() for cafe in cafes])


@app.route("/add", methods=["POST", "GET"])
def post_new_cafe():
    api_key = "TopSecretApiKey"
    if request.method == "GET":
        new_cafe = NewCafe()
        return render_template("new_cafe.html", form=new_cafe)
    if api_key == request.args.get("api_key"):
        new_cafe = Cafe(
            name=request.form.get("name"),
            map_url=request.form.get("map_url"),
            img_url=request.form.get("img_url"),
            location=request.form.get("location"),
            has_sockets=bool(request.form.get("sockets")),
            has_toilet=bool(request.form.get("toilet")),
            has_wifi=bool(request.form.get("wifi")),
            can_take_calls=bool(request.form.get("calls")),
            seats=request.form.get("seats"),
            coffee_price=request.form.get("coffee_price"),
        )
        db.session.add(new_cafe)
        db.session.commit()
        return jsonify(response={"Success": "Successfully added the new cafe."}), 200
    else:
        return (
            jsonify(
                response={
                    "Not Found": "Sorry, that's not allowed. Make sure you have the corretct api_key."
                }
            ),
            404,
        )


@app.route("/update-price/<int:cafe_id>", methods=["PATCH"])
def patch_new_price(cafe_id):
    new_price = request.args.get("new_price")
    cafe = db.session.query(Cafe).get(cafe_id)
    if cafe:
        cafe.coffee_price = new_price
        db.session.commit()
        return jsonify(response={"success": "Successfully updated the price."}), 200
    else:
        return (
            jsonify(
                error={
                    "Not Found": "Sorry a cafe with that id was not found in the database."
                }
            ),
            404,
        )


@app.route("/report-closed/<int:cafe_id>", methods=["DELETE"])
def delete_caffe(cafe_id):
    cafe = db.session.query(Cafe).get(cafe_id)
    api_key = "TopSecretAPIKey"

    if api_key == request.args.get("api_key"):
        if cafe:
            db.session.delete(cafe)
            db.session.commit()
            return (
                jsonify(
                    response={"Success": "Successfully deleted cafe from database."}
                ),
                200,
            )
        else:
            return (
                jsonify(
                    error={
                        "Not Found": "Sorry a cafe with that id was not found in the database"
                    }
                ),
                404,
            )

    else:
        return (
            jsonify(
                error={
                    "Not Found": "Sorry, that's not allowed. Make sure you have the correct api_key."
                }
            ),
            404,
        )


@app.route("/selected_coffee/<int:cafe_id>", methods=["POST", "GET"])
def selected_coffee(cafe_id):
    cafe = db.session.query(Cafe).get(cafe_id)
    return render_template("cafe.html", cafe=cafe)


@app.route("/new_cafe", methods=["POST", "GET"])
def new_cafe():
    form = NewCafe(meta={"csrf": False})
    if form.validate_on_submit():
        new_cafe_add = Cafe(
            name=request.form.get("name"),
            map_url=request.form.get("map_url"),
            img_url=request.form.get("img_url"),
            location=request.form.get("location"),
            has_sockets=bool(request.form.get("sockets")),
            has_toilet=bool(request.form.get("toilet")),
            has_wifi=bool(request.form.get("wifi")),
            can_take_calls=bool(request.form.get("calls")),
            seats=request.form.get("seats"),
            coffee_price=request.form.get("coffee_price"),
        )
        db.session.add(new_cafe_add)
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("new_cafe.html", form=form)


if __name__ == "__main__":
    app.run(debug=True)
