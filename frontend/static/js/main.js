// Global Config
const getApiBaseUrl = () => {
    const host = window.location.hostname || 'localhost';
    if (window.location.port === '5000') {
        return `${window.location.origin}/api`;
    }
    return `http://${host}:5000/api`;
};
const API_BASE_URL = getApiBaseUrl();

// Utilities
function showNotification(msg, type = 'info') {
    const area = document.getElementById('notification-area');
    const notif = document.createElement('div');
    notif.className = `notification ${type}`;
    notif.innerHTML = `
        <i class="fa-solid ${type === 'success' ? 'fa-check-circle' : type === 'error' ? 'fa-exclamation-circle' : 'fa-info-circle'}"></i>
        <span>${msg}</span>
    `;
    area.appendChild(notif);
    setTimeout(() => {
        notif.style.animation = 'slideIn 0.3s ease-in reverse forwards';
        setTimeout(() => notif.remove(), 300);
    }, 4000);
}

function getToken() {
    return localStorage.getItem('token');
}

// Authentication Flow
document.addEventListener('DOMContentLoaded', () => {
    checkAuth();
    initMap();

    // Prevent default drag behaviors for the entire window, but ALLOW dropping anywhere on the page to work!
    window.addEventListener('dragover', (e) => { 
        e.preventDefault(); 
        const dropZone = document.getElementById('dropZone');
        if (dropZone) dropZone.classList.add('dragover');
    });
    window.addEventListener('dragleave', (e) => {
        const dropZone = document.getElementById('dropZone');
        if (dropZone && e.target === document.documentElement) dropZone.classList.remove('dragover');
    });
    window.addEventListener('drop', (e) => { 
        e.preventDefault(); 
        const dropZone = document.getElementById('dropZone');
        const imageInput = document.getElementById('imageInput');
        if (dropZone) dropZone.classList.remove('dragover');
        
        // If they dropped a file anywhere on the screen, upload it!
        if (e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files.length > 0) {
            if (imageInput) imageInput.files = e.dataTransfer.files;
            if (typeof handleImageUpload === 'function') handleImageUpload(e.dataTransfer.files[0]);
        }
    });

    // Event Listeners
    const loginForm = document.getElementById('loginForm');
    if (loginForm) loginForm.addEventListener('submit', handleLogin);

    const regForm = document.getElementById('registerForm');
    if (regForm) regForm.addEventListener('submit', handleRegister);

    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) logoutBtn.addEventListener('click', handleLogout);

    // Image Upload & AI Preview
    const dropZone = document.getElementById('dropZone');
    const imageInput = document.getElementById('imageInput');
    if (dropZone && imageInput) {
        dropZone.addEventListener('click', () => {
            imageInput.value = ''; // Reset input so same file can trigger 'change'
            imageInput.click();
        });
        dropZone.addEventListener('dragover', (e) => { e.preventDefault(); dropZone.classList.add('dragover'); });
        dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragover'));
        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.classList.remove('dragover');
            if(e.dataTransfer.files.length) {
                imageInput.files = e.dataTransfer.files;
                handleImageUpload(e.dataTransfer.files[0]);
            }
        });
        imageInput.addEventListener('change', (e) => {
            if(e.target.files.length) handleImageUpload(e.target.files[0]);
        });
    }

    const bookingForm = document.getElementById('bookingForm');
    if (bookingForm) bookingForm.addEventListener('submit', handleBookingSubmit);
});

function checkAuth() {
    const token = getToken();
    const userRole = localStorage.getItem('role');
    const isAuthPage = window.location.pathname.includes('register.html');
    const isAdminPage = window.location.pathname.includes('admin.html');

    if (token) {
        if (isAuthPage) {
            window.location.href = userRole === 'admin' ? 'admin.html' : 'index.html';
        } else {
            // Unhide auth-required elements
            document.querySelectorAll('.auth-required').forEach(el => el.style.display = '');
            const loginBtn = document.getElementById('navLoginBtn');
            if(loginBtn) loginBtn.style.display = 'none';
            
            const nameEl = document.getElementById('userName');
            if(nameEl) nameEl.textContent = localStorage.getItem('name');

            if (!isAdminPage && !isAuthPage) {
                loadDashboardData();
            }
        }
    } else {
        if (!isAuthPage) {
            window.location.href = 'register.html';
        }
    }
}

async function handleLogin(e) {
    e.preventDefault();
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;

    try {
        const res = await fetch(`${API_BASE_URL}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });
        const data = await res.json();
        
        if (res.ok) {
            localStorage.setItem('token', data.token);
            localStorage.setItem('role', data.user.role);
            localStorage.setItem('name', data.user.name);
            showNotification('Login successful!', 'success');
            setTimeout(() => {
                window.location.href = data.user.role === 'admin' ? 'admin.html' : 'index.html';
            }, 1000);
        } else {
            showNotification(data.error || 'Login failed', 'error');
        }
    } catch (err) {
        showNotification('Network error. Is backend running?', 'error');
    }
}

async function handleRegister(e) {
    e.preventDefault();
    const name = document.getElementById('regName').value;
    const email = document.getElementById('regEmail').value;
    const password = document.getElementById('regPassword').value;

    try {
        const res = await fetch(`${API_BASE_URL}/auth/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, email, password })
        });
        const data = await res.json();
        
        if (res.ok) {
            showNotification('Registration successful! Please login.', 'success');
            document.getElementById('showLogin').click();
        } else {
            showNotification(data.error || 'Registration failed', 'error');
        }
    } catch (err) {
        showNotification('Network error', 'error');
    }
}

function handleLogout() {
    localStorage.clear();
    window.location.href = 'register.html';
}

// Leaflet Map Initialization
let map, marker;
function initMap() {
    const mapEl = document.getElementById('map');
    if (!mapEl) return;

    // Default center (e.g., Delhi, India)
    const defaultCenter = [28.6139, 77.2090];
    map = L.map('map', {
        center: defaultCenter,
        zoom: 13,
        zoomControl: true
    });
    
    // High-resolution, full detail OpenStreetMap DE tiles (100% free, no API key, street zoom up to 19)
    L.tileLayer('https://{s}.tile.openstreetmap.de/{z}/{x}/{y}.png', {
        maxZoom: 19,
        subdomains: 'abc',
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    // Initial marker & set hidden input fields
    marker = L.marker(defaultCenter, { draggable: true }).addTo(map);
    document.getElementById('lat').value = defaultCenter[0];
    document.getElementById('lng').value = defaultCenter[1];

    // Marker drag handler
    marker.on('dragend', function () {
        const latlng = marker.getLatLng();
        document.getElementById('lat').value = latlng.lat;
        document.getElementById('lng').value = latlng.lng;
    });

    // Click on map to position marker
    map.on('click', (e) => {
        const lat = e.latlng.lat;
        const lng = e.latlng.lng;
        document.getElementById('lat').value = lat;
        document.getElementById('lng').value = lng;
        
        if (marker) map.removeLayer(marker);
        marker = L.marker([lat, lng], { draggable: true }).addTo(map);
        marker.on('dragend', function () {
            const pos = marker.getLatLng();
            document.getElementById('lat').value = pos.lat;
            document.getElementById('lng').value = pos.lng;
        });
    });

    // Force map size recalculation after layout unhides / fades in
    setTimeout(() => {
        if (map) map.invalidateSize();
    }, 400);

    // Try HTML5 Geolocation
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(position => {
            const pos = [position.coords.latitude, position.coords.longitude];
            map.setView(pos, 14);
            if (marker) map.removeLayer(marker);
            marker = L.marker(pos, { draggable: true }).addTo(map);
            document.getElementById('lat').value = pos[0];
            document.getElementById('lng').value = pos[1];
            marker.on('dragend', function () {
                const p = marker.getLatLng();
                document.getElementById('lat').value = p.lat;
                document.getElementById('lng').value = p.lng;
            });
            setTimeout(() => { if (map) map.invalidateSize(); }, 200);
        }, () => {
            // Geolocation fallback handled by defaultCenter
        });
    }

    window.addEventListener('resize', () => {
        if (map) map.invalidateSize();
    });
}

// AI Image Upload & Classification Flow
async function handleImageUpload(file) {
    if (!file) return;

    // Show Preview
    const preview = document.getElementById('imagePreview');
    preview.src = URL.createObjectURL(file);
    preview.style.display = 'block';

    // Show Spinner
    document.getElementById('aiSpinner').style.display = 'block';
    document.getElementById('aiResult').style.display = 'none';

    const formData = new FormData();
    formData.append('image', file);

    try {
        const res = await fetch(`${API_BASE_URL}/ml/predict`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${getToken()}` },
            body: formData
        });
        
        const data = await res.json();
        document.getElementById('aiSpinner').style.display = 'none';

        if (res.ok) {
            document.getElementById('aiResult').style.display = 'block';
            document.getElementById('aiCategory').textContent = data.category;
            document.getElementById('aiConfidence').textContent = (data.confidence * 100).toFixed(1);
            document.getElementById('aiReward').textContent = data.estimated_reward;
            
            // Store hidden values for form submission
            document.getElementById('hiddenCategory').value = data.category;
            document.getElementById('hiddenConfidence').value = data.confidence;
            document.getElementById('hiddenImageUrl').value = data.image_url;
            
            showNotification(`AI detected: ${data.category}`, 'success');
        } else {
            showNotification(data.error || 'Failed to classify image', 'error');
        }
    } catch (err) {
        document.getElementById('aiSpinner').style.display = 'none';
        showNotification('Failed to connect to AI server', 'error');
    }
}

// Submit Booking
async function handleBookingSubmit(e) {
    e.preventDefault();

    const imageUrl = document.getElementById('hiddenImageUrl').value;
    const category = document.getElementById('hiddenCategory').value;
    const confidenceScore = parseFloat(document.getElementById('hiddenConfidence').value);
    const rawDate = document.getElementById('pickupDate').value;
    const lat = parseFloat(document.getElementById('lat').value);
    const lng = parseFloat(document.getElementById('lng').value);
    const address = document.getElementById('address').value;

    if (!imageUrl || !category) {
        return showNotification('Please upload an e-waste image first for AI classification', 'error');
    }

    if (!lat || !lng || isNaN(lat) || isNaN(lng)) {
        return showNotification('Please select a pickup location on the map', 'error');
    }
    
    if (!address || address.trim() === '') {
        return showNotification('Please enter your full address', 'error');
    }
    
    if (!rawDate) {
        return showNotification('Please select a preferred pickup date', 'error');
    }

    // Sanitize datetime format for MySQL compatibility
    const formattedDate = rawDate.replace('T', ' ') + (rawDate.length === 16 ? ':00' : '');

    const payload = {
        image_url: imageUrl,
        category: category,
        confidence_score: isNaN(confidenceScore) ? 0.95 : confidenceScore,
        address: address.trim(),
        latitude: lat,
        longitude: lng,
        scheduled_date: formattedDate
    };

    try {
        const res = await fetch(`${API_BASE_URL}/bookings/create`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${getToken()}`
            },
            body: JSON.stringify(payload)
        });

        const data = await res.json();
        if (res.ok) {
            showNotification('Booking scheduled successfully!', 'success');
            document.getElementById('bookingForm').reset();
            document.getElementById('hiddenImageUrl').value = '';
            document.getElementById('hiddenCategory').value = '';
            document.getElementById('hiddenConfidence').value = '';
            document.getElementById('imagePreview').style.display = 'none';
            document.getElementById('aiResult').style.display = 'none';
            loadDashboardData(); // Refresh list and stats
        } else {
            showNotification(data.error || 'Failed to book pickup', 'error');
        }
    } catch (err) {
        showNotification('Error scheduling pickup', 'error');
    }
}

// Load Dashboard Info (Bookings, Points, etc.)
async function loadDashboardData() {
    try {
        const timestamp = new Date().getTime();
        const [bookingsRes, rewardsRes] = await Promise.all([
            fetch(`${API_BASE_URL}/bookings/history?t=${timestamp}`, { headers: { 'Authorization': `Bearer ${getToken()}` } }),
            fetch(`${API_BASE_URL}/rewards/balance?t=${timestamp}`, { headers: { 'Authorization': `Bearer ${getToken()}` } })
        ]);

        if (bookingsRes.ok) {
            const data = await bookingsRes.json();
            updateBookingsTable(data.bookings);
            
            const pending = data.bookings.filter(b => ['pending', 'scheduled'].includes(b.status)).length;
            document.getElementById('pendingPickups').textContent = pending;
            document.getElementById('totalRecycled').textContent = data.bookings.filter(b => b.status === 'collected').length;
        }

        if (rewardsRes.ok) {
            const data = await rewardsRes.json();
            document.getElementById('rewardPoints').textContent = data.balance;
            const pointsBadge = document.getElementById('userPoints');
            if(pointsBadge) {
                pointsBadge.innerHTML = `<i class="fa-solid fa-coins"></i> ${data.balance} Points`;
                pointsBadge.style.display = 'inline-block';
            }
        }
    } catch (err) {
        console.error("Failed to load dashboard stats", err);
    }
}

function getImageUrl(url) {
    if (!url) return 'https://via.placeholder.com/150';
    if (url.startsWith('http://') || url.startsWith('https://')) return url;
    const host = window.location.hostname || 'localhost';
    return `http://${host}:5000${url.startsWith('/') ? '' : '/'}${url}`;
}

function updateBookingsTable(bookings) {
    const tbody = document.getElementById('bookingsTableBody');
    if (!tbody) return;

    tbody.innerHTML = '';
    if (!bookings.length) {
        tbody.innerHTML = '<tr><td colspan="8" style="text-align:center;">No bookings found.</td></tr>';
        return;
    }

    bookings.forEach(b => {
        const displayImgUrl = getImageUrl(b.image_url);
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>#${b.id.substring(0,6)}</td>
            <td><img src="${displayImgUrl}" alt="E-waste preview" style="width: 50px; height: 50px; object-fit: cover; border-radius: 8px; border: 1px solid var(--glass-border);"></td>
            <td>${b.category}</td>
            <td>${(b.confidence_score * 100).toFixed(0)}%</td>
            <td><span class="badge ${b.status}">${b.status}</span></td>
            <td><span class="badge ${b.status === 'collected' ? 'collected' : 'pending'}">${b.status === 'collected' ? '+' + b.points : b.points + ' (Est.)'}</span></td>
            <td>${new Date(b.scheduled_date).toLocaleDateString()}</td>
            <td>
                <button class="btn btn-sm btn-outline" onclick="deleteBooking('${b.id}')" style="padding:0.2rem 0.5rem; font-size:0.8rem; border-color:var(--danger); color:var(--danger);"><i class="fa-solid fa-trash"></i> Delete</button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

async function deleteBooking(id) {
    if (!confirm('Are you sure you want to delete this booking?')) return;

    try {
        const res = await fetch(`${API_BASE_URL}/bookings/${id}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${getToken()}`
            }
        });

        const data = await res.json();
        if (res.ok) {
            showNotification('Booking deleted successfully!', 'success');
            loadDashboardData(); // Refresh the list and stats
        } else {
            showNotification(data.error || 'Failed to delete booking', 'error');
        }
    } catch (err) {
        showNotification('Error deleting booking', 'error');
    }
}

