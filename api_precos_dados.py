from flask import Flask, jsonify
import json

app = Flask(__name__)

@app.route('/dados')
def dados():

    with open('resultados_fiis.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    return jsonify(data)

if __name__ == '__main__':
    app.run(
        host='0.0.0.0', 
        port=5001,  
)

 