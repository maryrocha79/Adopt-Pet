from flask import Flask, url_for, render_template, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from flask_debugtoolbar import DebugToolbarExtension
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, RadioField, TextAreaField, BooleanField
from wtforms.validators import InputRequired, Length, NumberRange, URL, Optional

defaultimg = "https://media.gettyimages.com/photos/portrait-of-otter-on-grassy-field-picture-id590287239?s=612x612"
app = Flask(__name__)

app.config['SECRET_KEY'] = "abcdef"

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://localhost/pets_db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)
toolbar = DebugToolbarExtension(app)


class Pet(db.Model):
    __tablename__ = "pets"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    species = db.Column(db.Text, nullable=False)
    photo_url = db.Column(db.Text)
    age = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.Text)
    available = db.Column(db.Boolean, nullable=False, default=True)


db.create_all()


class AddPetForm(FlaskForm):
    name = StringField("Pet Name", validators=[InputRequired()])
    species = RadioField(
        "Species",
        validators=[InputRequired()],
        choices=[('cat', 'Cat'), ('dog', 'Dog'), ('porcupine', 'Porcupine')])
    photo_url = StringField("Photo Url", validators=[Optional(), URL()])
    age = IntegerField(
        "Pet Age", validators=[InputRequired(),
                               NumberRange(min=0, max=30)])
    notes = TextAreaField("Comments", validators=[Length(max=50)])


class EditForm(FlaskForm):
    photo_url = StringField("Photo Url", validators=[Optional(), URL()])
    notes = TextAreaField("Comments", validators=[Length(max=50)])
    available = BooleanField("Available?")


@app.route('/pets')
def pet_index():
    pets = Pet.query.all()
    return render_template('pet_index.html', pets=pets)


@app.route('/pets/add', methods=['GET', 'POST'])
def add_pet():
    """Show pet add form and handle adding"""
    form = AddPetForm()

    if form.validate_on_submit():
        name = form.data['name']
        species = form.data['species']
        photo_url = form.data['photo_url']
        age = form.data['age']
        notes = form.data['notes']

        new_pet = Pet(
            name=name,
            species=species,
            photo_url=photo_url,
            age=age,
            notes=notes)
        db.session.add(new_pet)
        db.session.commit()
        return redirect(url_for('pet_index'))

    else:
        return render_template("pet_add_form.html", form=form)

    @app.route('/pets/<int:pet_id>', methods=['GET', 'POST'])
    def display_edit(pet_id):
        pet = Pet.query.get(pet_id)
        form = EditForm(obj=pet)

        if form.validate_on_submit():
            pet.photo_url = form.data['photo_url']
            pet.notes = form.data['notes']
            pet.available = form.data['available']
            db.session.commit()
            return redirect(url_for('pet_index'))

        else:
            return render_template("pet_edit_form.html", form=form, pet=pet)
