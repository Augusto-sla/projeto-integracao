"""
app.py - Flask Backend for the Production Order System.

REST API with full CRUD operations, API Key authentication,
input sanitization, and global error handling.
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from database import init_dataBase, get_connection
from functools import wraps
import datetime
import html

app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)

# Security Configuration
# In production, this should be an environment variable (e.g., os.environ.get('API_KEY'))
API_KEY = 'senai-cybersystems-2026-secure-key'


# ── Authentication Decorator ───────────────────────────────────────
def require_authentication(f):
    """
    Protects routes by requiring a valid X-API-Key header.
    
    Returns 401 if missing, or 403 if invalid.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        received_key = request.headers.get('X-API-Key')
        if not received_key:
            return jsonify({
                'error': 'Authentication required.',
                'instruction': 'Send the X-API-Key header with your request.'
            }), 401
        
        if received_key != API_KEY:
            return jsonify({
                'error': 'Invalid or expired API Key.'
            }), 403
            
        return f(*args, **kwargs)
    return decorated


# ── Global Error Handlers ──────────────────────────────────────────
@app.errorhandler(400)
def bad_request(e): 
    return jsonify({'error': 'Bad request.'}), 400

@app.errorhandler(401)
def unauthorized(e): 
    return jsonify({'error': 'Authentication required.'}), 401

@app.errorhandler(403)
def forbidden(e): 
    return jsonify({'error': 'Access denied.'}), 403

@app.errorhandler(404)
def not_found(e): 
    return jsonify({'error': 'Resource not found.'}), 404

@app.errorhandler(405)
def method_not_allowed(e): 
    return jsonify({'error': 'HTTP method not allowed on this route.'}), 405

@app.errorhandler(500)
def internal_error(e): 
    return jsonify({'error': 'Internal server error. Contact the administrator.'}), 500


# ── Frontend Route ─────────────────────────────────────────────────
@app.route('/')
def index():
    """Serves the index.html file from the static folder."""
    return app.send_static_file('index.html')


# ── API Health Check ───────────────────────────────────────────────
@app.route('/status', methods=['GET'])
def check_status():
    """Returns a JSON with the API status and total order count."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) as total FROM orders')
    result = cursor.fetchone()
    conn.close()
    
    return jsonify({
        'status': 'online',
        'system': 'Production Order System',
        'version': '2.0.0',
        'total_orders': result['total'],
        'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })


# ── GET /orders ────────────────────────────────────────────────────
@app.route('/orders', methods=['GET'])
def list_orders():
    """
    Lists all production orders. Accepts '?status=' as a query filter.
    
    Returns:
        JSON array of order objects.
    """
    status_filter = request.args.get('status')
    conn = get_connection()
    cursor = conn.cursor()
    
    if status_filter:
        cursor.execute('SELECT * FROM orders WHERE status = ? ORDER BY id DESC', (status_filter,))
    else:
        cursor.execute('SELECT * FROM orders ORDER BY id DESC')
        
    orders = cursor.fetchall()
    conn.close()
    
    return jsonify([dict(o) for o in orders]), 200


# ── GET /orders/<id> ───────────────────────────────────────────────
@app.route('/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    """Fetches a single order by ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM orders WHERE id = ?', (order_id,))
    order = cursor.fetchone()
    conn.close()
    
    if order is None:
        return jsonify({'error': f'Order {order_id} not found.'}), 404
        
    return jsonify(dict(order)), 200


# ── POST /orders ───────────────────────────────────────────────────
@app.route('/orders', methods=['POST'])
@require_authentication
def create_order():
    """
    Creates a new production order. Requires X-API-Key.
    Sanitizes string inputs to prevent XSS.
    """
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Missing or invalid JSON body.'}), 400
        
    # Sanitize and validate product name
    product = html.escape(data.get('product', '').strip())
    if not product:
        return jsonify({'error': 'Product field is required.'}), 400
    if len(product) > 200:
        return jsonify({'error': 'Product name too long (max 200 characters).'}), 400
        
    # Validate quantity
    quantity = data.get('quantity')
    if quantity is None:
        return jsonify({'error': 'Quantity field is required.'}), 400
    try:
        quantity = int(quantity)
        if quantity <= 0 or quantity > 999999:
            raise ValueError()
    except (ValueError, TypeError):
        return jsonify({'error': 'Quantity must be a positive integer between 1 and 999999.'}), 400
        
    # Validate status
    valid_statuses = ['Pending', 'In Progress', 'Completed']
    status = data.get('status', 'Pending')
    if status not in valid_statuses:
        return jsonify({'error': f'Invalid status. Allowed values: {valid_statuses}'}), 400
        
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO orders (product, quantity, status) VALUES (?, ?, ?)',
        (product, quantity, status)
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    
    # Fetch the newly created record to return
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM orders WHERE id = ?', (new_id,))
    new_order = cursor.fetchone()
    conn.close()
    
    return jsonify(dict(new_order)), 201


# ── PUT /orders/<id> ───────────────────────────────────────────────
@app.route('/orders/<int:order_id>', methods=['PUT'])
@require_authentication
def update_order(order_id):
    """
    Updates the status of an existing order. Requires X-API-Key.
    """
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Missing or invalid JSON body.'}), 400
        
    valid_statuses = ['Pending', 'In Progress', 'Completed']
    new_status = data.get('status', '').strip()
    
    if not new_status:
        return jsonify({'error': 'Status field is required.'}), 400
    if new_status not in valid_statuses:
        return jsonify({'error': f'Invalid status. Allowed values: {valid_statuses}'}), 400
        
    conn = get_connection()
    cursor = conn.cursor()
    
    # Check if exists
    cursor.execute('SELECT id FROM orders WHERE id = ?', (order_id,))
    if cursor.fetchone() is None:
        conn.close()
        return jsonify({'error': f'Order {order_id} not found.'}), 404
        
    cursor.execute('UPDATE orders SET status = ? WHERE id = ?', (new_status, order_id))
    conn.commit()
    conn.close()
    
    # Fetch updated record
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM orders WHERE id = ?', (order_id,))
    updated_order = cursor.fetchone()
    conn.close()
    
    return jsonify(dict(updated_order)), 200


# ── DELETE /orders/<id> ────────────────────────────────────────────
@app.route('/orders/<int:order_id>', methods=['DELETE'])
@require_authentication
def delete_order(order_id):
    """
    Permanently removes an order. Requires X-API-Key.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT id, product FROM orders WHERE id = ?', (order_id,))
    order = cursor.fetchone()
    
    if order is None:
        conn.close()
        return jsonify({'error': f'Order {order_id} not found.'}), 404
        
    product_name = order['product']
    cursor.execute('DELETE FROM orders WHERE id = ?', (order_id,))
    conn.commit()
    conn.close()
    
    return jsonify({
        'message': f'Order {order_id} ({product_name}) deleted successfully.',
        'deleted_id': order_id
    }), 200


if __name__ == '__main__':
    init_dataBase()
    app.run(debug=True, host='0.0.0.0', port=5000)