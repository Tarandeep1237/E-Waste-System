const API_BASE_URL = 'http://localhost:5000/api';

document.addEventListener('DOMContentLoaded', () => {
    // Check Admin Auth
    const token = localStorage.getItem('token');
    const role = localStorage.getItem('role');
    
    if (!token || role !== 'admin') {
        window.location.href = 'register.html';
        return;
    }

    document.getElementById('logoutBtn').addEventListener('click', () => {
        localStorage.clear();
        window.location.href = 'register.html';
    });

    initAdminDashboard();
});

let adminMap;
let heatLayer;

async function initAdminDashboard() {
    // 1. Fetch Admin Stats & Bookings
    await loadAdminData();
}

async function loadAdminData() {
    try {
        const timestamp = new Date().getTime();
        const res = await fetch(`${API_BASE_URL}/admin/dashboard?t=${timestamp}`, {
            headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
        });
        
        if (res.ok) {
            const data = await res.json();
            
            // Update Stats
            document.getElementById('totalPickups').textContent = data.stats.totalPickups;
            document.getElementById('pendingApprovals').textContent = data.stats.pendingApprovals;
            document.getElementById('pointsDistributed').textContent = data.stats.pointsDistributed;

            // Render Chart
            renderChart(data.categoryStats);

            // Render Table
            renderBookingsTable(data.bookings);
        }
    } catch (err) {
        console.error('Failed to load admin data', err);
    }
}

function renderChart(categoryStats) {
    const ctx = document.getElementById('categoryChart').getContext('2d');
    
    const labels = Object.keys(categoryStats);
    const data = Object.values(categoryStats);

    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: [
                    '#00d2ff',
                    '#3a7bd5',
                    '#22c55e',
                    '#f59e0b',
                    '#ef4444'
                ],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'right', labels: { color: '#f8fafc' } }
            }
        }
    });
}



function renderBookingsTable(bookings) {
    const tbody = document.getElementById('adminBookingsTable');
    tbody.innerHTML = '';

    bookings.forEach(b => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${b.user_name || 'User ' + b.user_id.substring(0,4)}</td>
            <td><img src="${b.image_url}" alt="E-waste" style="width: 50px; height: 50px; object-fit: cover; border-radius: 8px; border: 1px solid var(--glass-border);"></td>
            <td>${b.category} <small>(${(b.confidence_score*100).toFixed(0)}%)</small></td>
            <td>${new Date(b.scheduled_date).toLocaleDateString()}</td>
            <td><span class="badge ${b.status}">${b.status}</span></td>
            <td>
                ${b.status === 'pending' || b.status === 'scheduled' ? `
                    <button class="btn btn-sm btn-outline" onclick="updateBookingStatus('${b.id}', 'collected')" style="padding:0.2rem 0.5rem; font-size:0.8rem; margin-right:0.5rem;"><i class="fa-solid fa-check"></i> Collect</button>
                    <button class="btn btn-sm btn-outline" onclick="updateBookingStatus('${b.id}', 'rejected')" style="padding:0.2rem 0.5rem; font-size:0.8rem; border-color:var(--danger); color:var(--danger);"><i class="fa-solid fa-xmark"></i> Reject</button>
                ` : '-'}
            </td>
        `;
        tbody.appendChild(tr);
    });
}

async function updateBookingStatus(id, status) {
    if(!confirm(`Mark booking as ${status}?`)) return;

    try {
        const res = await fetch(`${API_BASE_URL}/admin/bookings/${id}/status`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            },
            body: JSON.stringify({ status })
        });
        
        if (res.ok) {
            loadAdminData(); // Refresh everything
        } else {
            alert('Failed to update status');
        }
    } catch (err) {
        console.error(err);
    }
}


