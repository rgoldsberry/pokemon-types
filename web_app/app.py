import pandas as pd
from flask import Flask, render_template
from sqlalchemy import create_engine

app = Flask(__name__)



#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///pkmn.sqlite")

type_df = pd.read_sql("SELECT * FROM typemult", con = engine, index_col="type")

# core function for deciding what to attack with
def attack_with(type1, type2=None):

    #monotype    
    if type2 == None:
        damage = type_df[type1]
        damage = damage[damage != 1].sort_values(ascending=False)
        return pd.DataFrame(damage, columns = ["defmult"])
    #dual type
    else:
        damage = type_df[type1] * type_df[type2]
        damage = damage[damage != 1].sort_values(ascending=False)
        return pd.DataFrame(damage, columns = ["defmult"])


#################################################
# Flask Routes
#################################################

@app.route("/")
def index():
    table = attack_with('water', 'flying')
    return render_template("index.html", table = table.to_html())

# to-do: add two pages, one for inputting the types, one for searching by pokemon name
# in either case, send to a calculation route that grabs the columns from a sqlite
# and then runs the calculation and sends back to home page with the table rendered 
@app.route("/type")
def type_input():
    return "You came to the type input page!"

@app.route("/name")
def name_input():
    return "You came to the name input page!"

#################################################
# Running App
#################################################

if __name__ == "__main__":
    app.run(debug=True)