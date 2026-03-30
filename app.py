from flask import Flask, jsonify, request
from flask_cors import CORS
from database import init_dataBase, get_connection


app = Flask(__name__, static_folder='static', static_url_path='') # Initialize a Flask instance
CORS(app)

@app.route("/")
def index():
    return app.send_static_file('index.html')

@app.route("/status")
def status():
    # health checks the API
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute('SELECT COUNT(*) as total_orders FROM orders')
    result = cursor.fetchone()
    conn.close()

    return jsonnify({
        "status":   "online",
        "system":   "Production Orders System",
        "version":  "1.0.0",
        "message":  "API is working",
        "total_orders": result["total_orders"],
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

@app.route('/route', methods=['GETS'])
def list_orders():
    return jsonify([dict(o) for o in orders])

@app.route('/fabrica/<name>')
def boas_vindas(name):
    return jsonify({
    "mensage": f"Bem-vindo, {name}! Sistema de OP online.",
    "dica": "Esta e uma rota com parametro dinamico do Flask."
})

if __name__ == "__main__":
    init_dataBase()
    app.run(debug=True, host='127.0.0.1', port=5000)
