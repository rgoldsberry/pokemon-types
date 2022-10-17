import pandas as pd
from flask import Flask, render_template, request, redirect, url_for
from sqlalchemy import create_engine

app = Flask(__name__)



#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///web_app/pkmn.sqlite")

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
        type1 = request.form.get("type_1_input")
        type2 = request.form.get("type_2_input")
        def_mult_table = attack_with(type1, type2).to_html(index = False, classes=['table table-striped'])
        return redirect(url_for("calc", def_mult_table=def_mult_table))
    else:
        return render_template("type.html", type_list=type_list)



@app.route("/name", methods=["POST", "GET"])
def name_input():
    if request.method == "POST":
        pkmn=request.form.get("poke_name")

        if name_df.loc[pkmn][1]:
            type1=name_df.loc[pkmn][0]
            type2=name_df.loc[pkmn][1]
            def_mult_table = attack_with(type1, type2).to_html(index = False, classes=['table table-striped'])
            return redirect(url_for("calc", def_mult_table=def_mult_table))
        else:
            type1=name_df.loc[pkmn][0]
            def_mult_table = attack_with(type1).to_html(index = False, classes=['table table-striped'])
            return redirect(url_for("calc", def_mult_table=def_mult_table))
    else:
        name_list = list(name_df.index)
        return render_template("name.html", name_list = name_list)


@app.route("/calc")
def calc():
    def_mult_table = request.args.get("def_mult_table")
    return render_template("calc.html", def_mult_table=def_mult_table)

#################################################
# Running App
#################################################

if __name__ == "__main__":
    app.run(debug=True)