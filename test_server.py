from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({"message": "Hello, World!"})

if __name__ == '__main__':
    print("Starting on port 7777")
    app.run(host='0.0.0.0', port=7777, debug=True)