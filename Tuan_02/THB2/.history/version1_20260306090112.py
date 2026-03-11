from flask import Flask

app = Flask(__name__)

users = [
    {"id": 1, "name": "An"},
    {"id": 2, "name": "Binh"}
]

@app.route("/getUsers")
def get_users():
    return {"users": users}

@app.route("/addUser")
def add_user():
    users.append({"id": 3, "name": "Cuong"})
    return {"message": "User added"}

app.run()