from    flask import Flask, jsonify, request
from    flask_cors import CORS
from    database import init_dataBase, get_connection
import  datetime
from    functools import wraps


app = Flask(__name__, static_folder='static', static_url_path='') # Initialize a Flask instance
CORS(app)

API_KEY = 'extremely-secure-api-key'

def autenticator(f):
    """
    Decorator that protects the routes demanding a valid API key

    The client must send the header:
        X-API-Key: <API key value>

    If the key in inexistent or incorrect returns 401 'unathourized'
    if correct, executes the function as intended

    """
    @wraps(f)
    def decorator(*args, **kwargs):
        # Lê o cabeçalho X-API-Key da requisição
        received_key = request.headers.get('X-API-Key')
        if not received_key:
            return jsonify({
            'error': 'Autentication needed.',
            'instrution': 'Send the header X-API-Key whith its key.'
            }), 401
        if received_key != API_KEY:
            return jsonify({
            'error': 'API key invalid or expired.'
            }), 403
            
        return f(*args, **kwargs)
    
    return decorator    
        
@app.route("/")
@autenticator
def index():
    return app.send_static_file('index.html')

@app.route("/status")
@autenticator
def status():
    # health checks the API
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute('SELECT COUNT(*) as total_orders FROM orders')
    result = cursor.fetchone()
    connection.close()

    return jsonify({
        "status":   "online",
        "system":   "Production Orders System",
        "version":  "1.0.0",
        "message":  "API is working",
        "total_orders": result["total_orders"],
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

@app.route('/orders', methods=['GET'])
@autenticator
def list_orders():
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM orders ORDER BY id DESC")
    orders = cursor.fetchall()
    connection.close()

    return jsonify([dict(o) for o in orders])

@app.route('/orders/<int:order_id>', methods=['GET'])
@autenticator
def search_order(order_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute('SELECT * FROM orders WHERE id=?', (order_id,))
    order = cursor.fetchone()   


    connection.close()
    if order is None:
        return jsonify ({'error': f'order {order_id} not found.'}), 404

    return jsonify(dict(order)), 200

@app.route('/orders', methods=['POST'])
@autenticator
def create_order():
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'requisition body non-existent or invalid.'}), 400

    product = data.get('product', '').strip()

    if not product:
        return jsonify({'error': 'field "product" is mandatory and can not be empty.'}), 400

    quantity = data.get('quantity')
    if quantity is None:
        return jsonify({'error': 'field "quantity" is mandatory and can not be empty.'}), 400
    
    try:
        quantity = int(quantity)
        if quantity <= 0:
            raise ValueError()
    except (ValueError, TypeError):
        return jsonify({'error': 'field "quantity" must be a positive integer.'}), 400

    valid_status = ['pending', 'in progress', 'done']
    status = data.get('status', 'pending')

    if status not in valid_status:
        return jsonify({'error': f'invalid status Use: {valid_status}'}), 400

    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute('INSERT INTO orders (product, quantity, status) VALUES (?, ?, ?)', (product, quantity, status))
    connection.commit()

    new_id= cursor.lastrowid
    connection.close()

    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM orders WHERE id = ?', (new_id,))
    new_order = cursor.fetchone()
    connection.close()

    return jsonify(dict(new_order)), 201

@app.route('/orders/<int:order_id>', methods=['PUT'])
@autenticator
def update_orders(order_id):
    data = request.get_json()
     
    if not data:
        return jsonify({'error': 'requisition body non-existent or invalid.'}), 400

    valid_status = ['pending', 'in progress', 'done']
    new_status = data.get('status', '').strip()
    
    if not new_status:
        return jsonify({'error': 'field status is mandatory.'}), 400

    if new_status not in valid_status:
        return jsonify({'error': f'invalid status. allowed valued: {valid_status}'}), 400

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute('UPDATE orders SET status = ? WHERE id = ?',(new_status, order_id))
    connection.commit()
    connection.close()


    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM orders WHERE id = ?', (order_id,))
    new_order = cursor.fetchone()
    connection.close()

    return jsonify(dict(new_order)), 200

@app.route('/orders/<int:order_id>', methods=['DELETE'])
@autenticator
def delete_order(order_id):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute('SELECT id, product FROM orders WHERE id = ?',(order_id,))
    order = cursor.fetchone()

    if order is None:
        connection.close()
        return jsonify({'error': f'Order {order_id} not found.'}), 404

    product_name = order['product']
    
    cursor.execute('DELETE FROM orders WHERE id = ?', (order_id,))
    connection.commit()
    connection.close()
    return jsonify({'mensage': f'Order {order_id} ({product_name}) removed with success.', 'id_removede': order_id}), 200

@app.route('/fabrica/<name>')
@autenticator
def welcome(name):
    return jsonify({
    "mensage": f"Welcome, {name}! OP system online.",
})

if __name__ == "__main__":
    init_dataBase()
    app.run(debug=True, host='0.0.0.0', port=5000)
