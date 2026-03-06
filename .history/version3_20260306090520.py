from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/sum")
def sum_numbers():
    a = int(request.args.get("a"))
    b = int(request.args.get("b"))
    return jsonify({"result": a + b})

if __name__ == "__main__":
    app.run(debug=True)