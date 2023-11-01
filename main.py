from flask import Flask, jsonify, render_template, request, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
import random
import os



class NewCafe(FlaskForm):
    name = StringField("Name ", validators=[DataRequired()])
    map_url = StringField("Map link ", validators=[DataRequired()])
    img_url = StringField("Image link ", validators=[DataRequired()])
    location = StringField("Location ", validators=[DataRequired()])
    seats = StringField("Seats ", validators=[DataRequired()])
    toilet = StringField("Toilet", validators=[DataRequired()])
    wifi = StringField("Wifi ", validators=[DataRequired()])
    sockets = StringField("Sockets ", validators=[DataRequired()])
    calls = StringField("Calls ", validators=[DataRequired()])
    coffee_price = StringField("Coffee price ", validators=[DataRequired()])
    submit = SubmitField("Add Cafe")


class SearchForm(FlaskForm):
    location = StringField("Location", validators=[DataRequired()])
    submit = SubmitField("Submit")

app = Flask(__name__)
# add it as a environment varible
app.secret_key = "your_secret_key_here"
bootstrap = Bootstrap(app)


# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DB_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
app.app_context().push()

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

db.create_all()


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


@app.route("/search", methods=["POST", "GET"])
def search_page():
    form = SearchForm()
    if form.validate_on_submit():
        location = form.location.data.title()
        cafes = Cafe.query.filter_by(location=location).all()
        if len(cafes) == 0:
            return jsonify(
                error={"Not Found": "Sorry, we don't have a cafe at that location."}
            )
        else:
            return jsonify(cafe=[cafe.to_dict() for cafe in cafes])
    return render_template("search.html", form=form)

@app.route("/search/location", methods=["POST"])
def get_cafe_at_location(location):
    cafes = Cafe.query.filter_by(location=location.title()).all()
    if len(cafes) == 0:
        return jsonify(
            error={"Not Found": "Sorry, we don't have a cafe at that location."}
        )
    else:
        return jsonify(cafe=[cafe.to_dict() for cafe in cafes])


@app.route("/add", methods=["POST", "GET"])
def post_new_cafe():
    api_key = "TopSecretApiKey"
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