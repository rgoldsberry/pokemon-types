import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, session
from sqlalchemy import create_engine
import json
import os

app = Flask(__name__)

app.config['SECRET_KEY'] = os.urandom(12).hex()

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///pkmn.sqlite")

type_df = pd.read_sql("SELECT * FROM typemult", con = engine, index_col="type")

type_list = list(type_df.index)

name_df = pd.read_sql("SELECT name, type_1, type_2 FROM pkmn_name_type", con = engine, index_col="name")
name_df.drop("Drop", inplace=True)

# core function for deciding what to attack with
def attack_with(type1, type2=None):

    #monotype    
    if type2 == None:
        damage = type_df[type1]
        damage = damage[damage != 1].sort_values(ascending=False)
        damage = pd.DataFrame(damage).rename(columns={type1: "Defense Multiplier"})
        damage['Type'] = [hit_type.title() for hit_type in damage.index]
        damage = damage[['Type', 'Defense Multiplier']]
        return damage
    #dual type
    else:
        damage = type_df[type1] * type_df[type2]
        damage = damage[damage != 1].sort_values(ascending=False)
        damage = pd.DataFrame(damage, columns = ["Defense Multiplier"])
        damage['Type'] = [hit_type.title() for hit_type in damage.index]
        damage = damage[['Type', 'Defense Multiplier']]
        return damage


#################################################
# Flask Routes
#################################################

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/type", methods = ['POST', 'GET'])
def type_input():
    if request.method == "POST":
        
        # try clearing out previous variables in the session
        try:
            session.pop('send')
        except:
            pass

        # look for the monotype indicator, return a single type answer
        if request.form.get == "on":
            type1 = request.form.get("type_1_input")
            def_mult_table = attack_with(type1).to_html(index = False, classes=['table table-striped'])
            send = {
                "type1": type1,
                "def_mult": def_mult_table
                }
            session['send'] = json.dumps(send)
            return redirect(url_for("calc"))
        # dual type answer
        else:
            type1 = request.form.get("type_1_input")
            type2 = request.form.get("type_2_input")

            # catch the error of people inputting the same type twice
            if type1 == type2:
                send = {
                    "error": 'Same type input twice. Did you mean to check "Monotype"?',
                    "source": "/type"
                }
                session['send'] = json.dumps(send)
                return redirect(url_for("oops"))
            else:
                def_mult_table = attack_with(type1, type2).to_html(index = False, classes=['table table-striped'])
                send = {
                    "type1": type1,
                    "type2": type2,
                    "def_mult": def_mult_table
                    }
                session['send'] = json.dumps(send)
                return redirect(url_for("calc"))
    else:
        return render_template("type.html", type_list=type_list)



@app.route("/name", methods=["POST", "GET"])
def name_input():
    try:
        if request.method == "POST":
            # try clearing out previous variables in the session
            try:
                session.pop('send')
            except:
                pass

            pkmn=request.form.get("poke_name")
            
            # see if the pokemon is dual type
            if name_df.loc[pkmn][1]:
                type1=name_df.loc[pkmn][0]
                type2=name_df.loc[pkmn][1]
                def_mult_table = attack_with(type1, type2).to_html(index = False, classes=['table table-striped'])
                send = {
                    "pkmn": pkmn,
                    "type1": type1,
                    "type2": type2,
                    "def_mult": def_mult_table
                }
                session['send'] = json.dumps(send)
                return redirect(url_for("calc"))
            # monotype
            else:
                type1=name_df.loc[pkmn][0]
                def_mult_table = attack_with(type1).to_html(index = False, classes=['table table-striped'])
                send = {
                    "pkmn": pkmn,
                    "type1": type1,
                    "def_mult": def_mult_table
                }
                session['send'] = json.dumps(send)
                return redirect(url_for("calc"))
        # render base page with names as a list for autofill
        else:
            name_list = list(name_df.index)
            return render_template("name.html", name_list = name_list)
    # catch the error of inputting a pokemon not in the list
    except:
        send = {
           "error": "I don't know that Pokémon yet, sorry.",
           "source": "/name"
        }
        session['send'] = json.dumps(send)
        return redirect(url_for("oops"))

@app.route("/oops")
def oops():
    received = session['send']
    return render_template("oops.html", received = json.loads(received))


@app.route("/calc")
def calc():
    received = session['send']
    return render_template("calc.html", received=json.loads(received))

#################################################
# Running App
#################################################

if __name__ == "__main__":
    app.run()