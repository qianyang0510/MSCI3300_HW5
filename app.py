from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from wtforms import StringField, IntegerField
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm

app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://qianyang:@localhost/pokemon'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:tap4fun@172.20.90.11/test'
app.config['SECRET_KEY'] = 'secret'
app.config['DEBUG'] = True
db = SQLAlchemy(app)

@app.before_first_request
def create_db():
    # Recreate database each time for demo
    db.create_all()

def serialize_list(model_list):
    return [m.as_dict() for m in model_list]

class Pokemon(db.Model):
    __tablename__ = 'pokemon'
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    name = db.Column(db.String(100), unique=True)
    type = db.Column(db.String(100))
    attack = db.Column(db.Integer)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class NewPokemonForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    type = StringField("Type", validators=[DataRequired()])
    attack = IntegerField("Attack", validators=[DataRequired()])


class DeletePokemonForm(FlaskForm):
    id = IntegerField()

@app.route("/search", methods=['GET', 'POST'])
def master():
    if request.method == 'GET':
        return render_template('master.html')
    if request.method == 'POST':
        name = request.form.get('name')
        results = Pokemon.query.filter(Pokemon.name.like('%{}%'.format(name))).all()
        return render_template('master.html',results=results)
        

@app.route("/")
def index(form=None):
    if form is None:
        form = NewPokemonForm()
    pokemons = list(Pokemon.query.order_by(Pokemon.id))
    return render_template("index.html", pokemons=pokemons, form=form)


@app.route("/add/", methods=("POST",))
def add_comment():
    form = NewPokemonForm()
    if form.validate_on_submit():
        db.session.add(Pokemon(name=form.name.data, type=form.type.data, attack=form.attack.data))
        db.session.commit()
        return redirect(url_for("index"))
    return index(form)


@app.route("/delete", methods=("POST",))
def delete_pokemon():
    form = DeletePokemonForm()
    if form.validate_on_submit():
        pokemon = db.session.query(Pokemon).filter_by(id=form.id.data).one()
        db.session.delete(pokemon)
        db.session.commit()
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run()
