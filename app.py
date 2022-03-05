from flask import Flask, jsonify, request
from captcha import solve

app = Flask(__name__)
app.config["DEBUG"] = True


@app.route('/captcha-solve', methods=['POST'])
def fortune():
    link = request.form.get('link')
    return jsonify({
        'result': solve(link),
    }), 200
