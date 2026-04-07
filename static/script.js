 // Configuration
        const API_URL = 'http://localhost:5000';
        const API_KEY = 'senai-cybersystems-2026-secure-key'; 
        
        const authHeaders = {
            'Content-Type': 'application/json',
            'X-API-Key': API_KEY
        };

        // ── Initialization ─────────────────────────────────────────────
        window.onload = async function() {
            await checkStatus();
            await loadOrders();
        };

        // ── API Health Check ───────────────────────────────────────────
        async function checkStatus() {
            const badge = document.getElementById('status-badge');
            try {
                const res = await fetch(`${API_URL}/status`);
                const data = await res.json();
                badge.textContent = `API Online | ${data.total_orders} orders`;
                badge.className = 'online';
            } catch (error) {
                badge.textContent = 'API Offline';
                badge.className = 'offline';
            }
        }

        // ── Badge Renderer ─────────────────────────────────────────────
        function renderBadge(status) {
            const classes = {
                'Pending': 'badge-pending',
                'In Progress': 'badge-progress',
                'Completed': 'badge-completed'
            };
            const cls = classes[status] || '';
            return `<span class="badge ${cls}">${status}</span>`;
        }

        // ── Show Message Utility ───────────────────────────────────────
        function showMessage(text, type) {
            const div = document.getElementById('message-box');
            div.textContent = text;
            div.className = `message ${type}`;
            div.classList.remove('hidden');
            setTimeout(() => div.classList.add('hidden'), 4000);
        }

        // ── Read (GET) ─────────────────────────────────────────────────
        async function loadOrders() {
            const loading = document.getElementById('loading');
            const noData = document.getElementById('no-data');
            const table = document.getElementById('orders-table');
            const tbody = document.getElementById('table-body');

            loading.classList.remove('hidden');
            table.classList.add('hidden');
            noData.classList.add('hidden');

            try {
                const res = await fetch(`${API_URL}/orders`);
                const orders = await res.json();
                
                loading.classList.add('hidden');
                
                if (orders.length === 0) {
                    noData.classList.remove('hidden');
                    return;
                }
                
                tbody.innerHTML = orders.map(order => `
                    <tr id="row-${order.id}">
                        <td>${order.id}</td>
                        <td>${order.product}</td>
                        <td>${order.quantity}</td>
                        <td>
                            <select onchange="updateStatus(${order.id}, this.value)">
                                <option value="Pending" ${order.status === 'Pending' ? 'selected' : ''}>Pending</option>
                                <option value="In Progress" ${order.status === 'In Progress' ? 'selected' : ''}>In Progress</option>
                                <option value="Completed" ${order.status === 'Completed' ? 'selected' : ''}>Completed</option>
                            </select>
                            <br>
                            <div style="margin-top: 5px;" id="badge-${order.id}">
                                ${renderBadge(order.status)}
                            </div>
                        </td>
                        <td>${order.created_at}</td>
                        <td>
                            <button class="btn-delete" onclick="deleteOrder(${order.id})">Delete</button>
                        </td>
                    </tr>
                `).join('');
                
                table.classList.remove('hidden');
            } catch (error) {
                loading.classList.add('hidden');
                showMessage('Connection error. Is the server running?', 'error');
                console.error(error);
            }
        }

        // ── Create (POST) ──────────────────────────────────────────────
        async function createOrder() {
            const product = document.getElementById('product').value.trim();
            const quantity = document.getElementById('quantity').value;
            const status = document.getElementById('initial-status').value;

            if (!product) {
                showMessage('Please enter a product name.', 'error');
                return;
            }
            if (!quantity || Number(quantity) <= 0) {
                showMessage('Please enter a valid positive quantity.', 'error');
                return;
            }

            const btn = document.getElementById('btn-register');
            btn.disabled = true;
            btn.textContent = 'Registering...';

            try {
                const res = await fetch(`${API_URL}/orders`, {
                    method: 'POST',
                    headers: authHeaders,
                    body: JSON.stringify({ 
                        product: product, 
                        quantity: Number(quantity), 
                        status: status 
                    })
                });
                
                const data = await res.json();
                
                if (res.ok) {
                    showMessage(`Order #${data.id} registered successfully!`, 'success');
                    document.getElementById('product').value = '';
                    document.getElementById('quantity').value = '';
                    document.getElementById('initial-status').value = 'Pending';
                    await loadOrders();
                    await checkStatus();
                } else {
                    showMessage(data.error || 'Failed to register order.', 'error');
                }
            } catch (error) {
                showMessage('Connection error.', 'error');
            } finally {
                btn.disabled = false;
                btn.textContent = 'Register Order';
            }
        }

        // ── Update (PUT) ───────────────────────────────────────────────
        async function updateStatus(id, newStatus) {
            try {
                const res = await fetch(`${API_URL}/orders/${id}`, {
                    method: 'PUT',
                    headers: authHeaders,
                    body: JSON.stringify({ status: newStatus })
                });
                
                const data = await res.json();
                
                if (res.ok) {
                    showMessage(`Order #${id} status updated to '${newStatus}'.`, 'success');
                    const badgeDiv = document.getElementById(`badge-${id}`);
                    if (badgeDiv) {
                        badgeDiv.innerHTML = renderBadge(newStatus);
                    }
                } else {
                    showMessage(data.error || 'Failed to update status.', 'error');
                }
            } catch (error) {
                showMessage('Connection error.', 'error');
            }
        }

        // ── Delete (DELETE) ────────────────────────────────────────────
        async function deleteOrder(id) {
            const confirmed = window.confirm(`Are you sure you want to delete Order #${id}? This action is permanent.`);
            if (!confirmed) return;

            try {
                const res = await fetch(`${API_URL}/orders/${id}`, {
                    method: 'DELETE',
                    headers: { 'X-API-Key': API_KEY } // DELETE usually doesn't need content-type
                });
                
                const data = await res.json();
                
                if (res.ok) {
                    showMessage(data.message, 'success');
                    const row = document.getElementById(`row-${id}`);
                    if (row) row.remove();
                    
                    const tbody = document.getElementById('table-body');
                    if (tbody.children.length === 0) {
                        document.getElementById('orders-table').classList.add('hidden');
                        document.getElementById('no-data').classList.remove('hidden');
                    }
                    await checkStatus();
                } else {
                    showMessage(data.error || 'Failed to delete order.', 'error');
                }
            } catch (error) {
                showMessage('Connection error.', 'error');
            }
        }