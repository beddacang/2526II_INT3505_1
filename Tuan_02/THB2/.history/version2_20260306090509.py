from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/users", methods=["GET"])
def get_users():
    users = [
        {"id": 1, "name": "An"},
        {"id": 2, "name": "Binh"}
    ]
    return jsonify(users)

if __name__ == "__main__":
    app.run(debug=True)