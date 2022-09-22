from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

# to-do: add two pages, one for inputting the types, one for searching by pokemon name
# in either case, send to a calculation route that grabs the columns from a sqlite
# and then runs the calculation and sends back to home page with the table rendered 
@app.route("/type")
def type_input():
    return "You came to the type input page!"

@app.route("/name")
def name_input():
    return "You came to the name input page!"


if __name__ == "__main__":
    app.run(debug=True)