from flask import Flask, request

app = Flask(__name__)

users = [
    {"id": 1, "name": "An"},
    {"id": 2, "name": "Binh"}
]

@app.route("/users", methods=["GET"])
def get_users():
    return {"users": users}

@app.route("/users/<int:id>", methods=["GET"])
def get_user(id):
    for user in users:
        if user["id"] == id:
            return user

@app.route("/users", methods=["POST"])
def create_user():
    data = request.json
    users.append(data)
    return {"message": "User created"}

@app.route("/users/<int:id>", methods=["DELETE"])
def delete_user(id):
    global users
    users = [u for u in users if u["id"] != id]
    return {"message": "User deleted"}

app.run()