from flask import Flask, jsonify, make_response

app = Flask(__name__)

@app.route("/data")
def get_data():
    data = {"message": "This data can be cached"}

    response = make_response(jsonify(data))
    response.headers["Cache-Control"] = "public, max-age=60"

    return response

if __name__ == "__main__":
    app.run(debug=True)