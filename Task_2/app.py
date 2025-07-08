from flask import Flask, request, jsonify, render_template_string
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import uuid
import os

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'your-secret-key-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rbac.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
jwt = JWTManager(app)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), default='viewer')  # admin, manager, contributor, viewer
    org_id = db.Column(db.Integer, db.ForeignKey('organization.id'))
    dept_id = db.Column(db.Integer, db.ForeignKey('department.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Organization(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    users = db.relationship('User', backref='organization', lazy=True)
    departments = db.relationship('Department', backref='organization', lazy=True)

class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    org_id = db.Column(db.Integer, db.ForeignKey('organization.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    users = db.relationship('User', backref='department', lazy=True)

class Resource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    org_id = db.Column(db.Integer, db.ForeignKey('organization.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    owner = db.relationship('User', backref='resources')

class GuestLink(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(100), unique=True, nullable=False)
    resource_id = db.Column(db.Integer, db.ForeignKey('resource.id'), nullable=False)
    permission = db.Column(db.String(10), default='view')  # view, edit
    expires_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    resource = db.relationship('Resource', backref='guest_links')

# Helper functions
def check_permission(user_role, action):
    permissions = {
        'admin': ['create', 'read', 'update', 'delete', 'share'],
        'manager': ['create', 'read', 'update', 'share'],
        'contributor': ['create', 'read', 'update'],
        'viewer': ['read']
    }
    return action in permissions.get(user_role, [])

# Routes
@app.route('/')
def home():
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>RBAC System - Register</title>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                margin: 0; 
                padding: 0; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .container { 
                background: white;
                padding: 40px;
                border-radius: 10px;
                box-shadow: 0 15px 35px rgba(0,0,0,0.1);
                width: 100%;
                max-width: 400px;
            }
            h1 { 
                text-align: center; 
                color: #333; 
                margin-bottom: 30px;
            }
            .form-group { 
                margin-bottom: 20px; 
            }
            label {
                display: block;
                margin-bottom: 5px;
                color: #555;
                font-weight: bold;
            }
            input, select { 
                width: 100%; 
                padding: 12px; 
                border: 2px solid #ddd;
                border-radius: 5px;
                font-size: 16px;
                box-sizing: border-box;
            }
            input:focus, select:focus {
                border-color: #667eea;
                outline: none;
            }
            button { 
                width: 100%;
                background: #667eea; 
                color: white; 
                padding: 12px 20px; 
                border: none; 
                border-radius: 5px;
                font-size: 16px;
                cursor: pointer;
                margin-top: 10px;
            }
            button:hover { 
                background: #5a6fd8; 
            }
            .link-button {
                background: transparent;
                color: #667eea;
                text-decoration: underline;
                font-size: 14px;
                padding: 5px;
                margin-top: 15px;
            }
            .link-button:hover {
                background: transparent;
                color: #5a6fd8;
            }
            .message {
                padding: 10px;
                margin-top: 10px;
                border-radius: 5px;
                text-align: center;
            }
            .success {
                background: #d4edda;
                color: #155724;
                border: 1px solid #c3e6cb;
            }
            .error {
                background: #f8d7da;
                color: #721c24;
                border: 1px solid #f5c6cb;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Create Account</h1>
            <form id="registerForm">
                <div class="form-group">
                    <label>Username</label>
                    <input type="text" id="username" required>
                </div>
                <div class="form-group">
                    <label>Email</label>
                    <input type="email" id="email" required>
                </div>
                <div class="form-group">
                    <label>Password</label>
                    <input type="password" id="password" required>
                </div>
                <div class="form-group">
                    <label>Role</label>
                    <select id="role">
                        <option value="viewer">Viewer</option>
                        <option value="contributor">Contributor</option>
                        <option value="manager">Manager</option>
                        <option value="admin">Admin</option>
                    </select>
                </div>
                <button type="submit">Register</button>
                <button type="button" class="link-button" onclick="window.location.href='/login'">
                    Already have an account? Login
                </button>
            </form>
            <div id="message"></div>
        </div>

        <script>
            document.getElementById('registerForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                
                const messageDiv = document.getElementById('message');
                messageDiv.innerHTML = '';
                
                try {
                    const response = await fetch('/register', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({
                            username: document.getElementById('username').value,
                            email: document.getElementById('email').value,
                            password: document.getElementById('password').value,
                            role: document.getElementById('role').value
                        })
                    });
                    
                    const data = await response.json();
                    
                    if (response.ok) {
                        messageDiv.innerHTML = '<div class="message success">Registration successful! <a href="/login">Click here to login</a></div>';
                        document.getElementById('registerForm').reset();
                    } else {
                        messageDiv.innerHTML = '<div class="message error">' + data.message + '</div>';
                    }
                } catch (error) {
                    messageDiv.innerHTML = '<div class="message error">Registration failed. Please try again.</div>';
                }
            });
        </script>
    </body>
    </html>
    ''')

@app.route('/login')
def login_page():
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>RBAC System - Login</title>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                margin: 0; 
                padding: 0; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .container { 
                background: white;
                padding: 40px;
                border-radius: 10px;
                box-shadow: 0 15px 35px rgba(0,0,0,0.1);
                width: 100%;
                max-width: 400px;
            }
            h1 { 
                text-align: center; 
                color: #333; 
                margin-bottom: 30px;
            }
            .form-group { 
                margin-bottom: 20px; 
            }
            label {
                display: block;
                margin-bottom: 5px;
                color: #555;
                font-weight: bold;
            }
            input { 
                width: 100%; 
                padding: 12px; 
                border: 2px solid #ddd;
                border-radius: 5px;
                font-size: 16px;
                box-sizing: border-box;
            }
            input:focus {
                border-color: #667eea;
                outline: none;
            }
            button { 
                width: 100%;
                background: #667eea; 
                color: white; 
                padding: 12px 20px; 
                border: none; 
                border-radius: 5px;
                font-size: 16px;
                cursor: pointer;
                margin-top: 10px;
            }
            button:hover { 
                background: #5a6fd8; 
            }
            .link-button {
                background: transparent;
                color: #667eea;
                text-decoration: underline;
                font-size: 14px;
                padding: 5px;
                margin-top: 15px;
            }
            .link-button:hover {
                background: transparent;
                color: #5a6fd8;
            }
            .message {
                padding: 10px;
                margin-top: 10px;
                border-radius: 5px;
                text-align: center;
            }
            .success {
                background: #d4edda;
                color: #155724;
                border: 1px solid #c3e6cb;
            }
            .error {
                background: #f8d7da;
                color: #721c24;
                border: 1px solid #f5c6cb;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Login</h1>
            <form id="loginForm">
                <div class="form-group">
                    <label>Username</label>
                    <input type="text" id="username" required>
                </div>
                <div class="form-group">
                    <label>Password</label>
                    <input type="password" id="password" required>
                </div>
                <button type="submit">Login</button>
                <button type="button" class="link-button" onclick="window.location.href='/'">
                    Don't have an account? Register
                </button>
            </form>
            <div id="message"></div>
        </div>

        <script>
            document.getElementById('loginForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                
                const messageDiv = document.getElementById('message');
                messageDiv.innerHTML = '';
                
                try {
                    const response = await fetch('/login', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({
                            username: document.getElementById('username').value,
                            password: document.getElementById('password').value
                        })
                    });
                    
                    const data = await response.json();
                    
                    if (response.ok) {
                        // Store token in localStorage
                        localStorage.setItem('authToken', data.access_token);
                        localStorage.setItem('userRole', data.role);
                        localStorage.setItem('username', document.getElementById('username').value);
                        
                        messageDiv.innerHTML = '<div class="message success">Login successful! Redirecting...</div>';
                        
                        // Redirect to dashboard
                        setTimeout(() => {
                            window.location.href = '/dashboard';
                        }, 1000);
                    } else {
                        messageDiv.innerHTML = '<div class="message error">' + data.message + '</div>';
                    }
                } catch (error) {
                    messageDiv.innerHTML = '<div class="message error">Login failed. Please try again.</div>';
                }
            });
        </script>
    </body>
    </html>
    ''')

@app.route('/dashboard')
def dashboard():
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>RBAC System - Dashboard</title>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                margin: 0; 
                padding: 0; 
                background: #f5f5f5;
            }
            .header {
                background: #667eea;
                color: white;
                padding: 15px 0;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }
            .header-content {
                max-width: 1200px;
                margin: 0 auto;
                padding: 0 20px;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            .user-info {
                display: flex;
                align-items: center;
                gap: 20px;
            }
            .container { 
                max-width: 1200px; 
                margin: 20px auto; 
                padding: 0 20px;
            }
            .form-group { 
                margin-bottom: 15px; 
            }
            input, select, textarea { 
                width: 100%; 
                padding: 10px; 
                border: 2px solid #ddd;
                border-radius: 5px;
                box-sizing: border-box;
            }
            input:focus, select:focus, textarea:focus {
                border-color: #667eea;
                outline: none;
            }
            button { 
                background: #667eea; 
                color: white; 
                padding: 10px 20px; 
                border: none; 
                border-radius: 5px;
                cursor: pointer;
                margin-right: 10px;
            }
            button:hover { 
                background: #5a6fd8; 
            }
            .logout-btn {
                background: #dc3545;
                padding: 8px 16px;
                font-size: 14px;
            }
            .logout-btn:hover {
                background: #c82333;
            }
            .section { 
                background: white;
                margin: 20px 0; 
                padding: 25px; 
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            .section h2 {
                margin-top: 0;
                color: #333;
                border-bottom: 2px solid #667eea;
                padding-bottom: 10px;
            }
            .results {
                background: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 5px;
                padding: 15px;
                margin-top: 10px;
                max-height: 300px;
                overflow-y: auto;
            }
            .result-item {
                background: white;
                margin: 5px 0;
                padding: 10px;
                border-radius: 3px;
                border-left: 4px solid #667eea;
            }
            .role-badge {
                background: #667eea;
                color: white;
                padding: 4px 8px;
                border-radius: 15px;
                font-size: 12px;
                text-transform: uppercase;
            }
        </style>
    </head>
    <body>
        <div class="header">
            <div class="header-content">
                <h1>RBAC Dashboard</h1>
                <div class="user-info">
                    <span>Welcome, <strong id="username"></strong></span>
                    <span class="role-badge" id="userRole"></span>
                    <button class="logout-btn" onclick="logout()">Logout</button>
                </div>
            </div>
        </div>

        <div class="container">
            <div class="section">
                <h2>Create Organization</h2>
                <form id="orgForm">
                    <div class="form-group">
                        <input type="text" id="orgName" placeholder="Organization Name" required>
                    </div>
                    <button type="submit">Create Organization</button>
                </form>
            </div>

            <div class="section">
                <h2>Create Department</h2>
                <form id="deptForm">
                    <div class="form-group">
                        <input type="text" id="deptName" placeholder="Department Name" required>
                        <input type="number" id="deptOrgId" placeholder="Organization ID" required>
                    </div>
                    <button type="submit">Create Department</button>
                </form>
            </div>

            <div class="section">
                <h2>Create Resource</h2>
                <form id="resourceForm">
                    <div class="form-group">
                        <input type="text" id="resourceName" placeholder="Resource Name" required>
                        <textarea id="resourceContent" placeholder="Resource Content" rows="3"></textarea>
                    </div>
                    <button type="submit">Create Resource</button>
                </form>
            </div>

            <div class="section">
                <h2>Create Guest Link</h2>
                <form id="guestForm">
                    <div class="form-group">
                        <input type="number" id="guestResourceId" placeholder="Resource ID" required>
                        <select id="guestPermission">
                            <option value="view">View Only</option>
                            <option value="edit">Edit</option>
                        </select>
                    </div>
                    <button type="submit">Create Guest Link</button>
                </form>
            </div>

            <div class="section">
                <h2>Activity Results</h2>
                <div class="results" id="results">
                    <p>Your activity results will appear here...</p>
                </div>
            </div>
        </div>

        <script>
            // Check if user is logged in
            const authToken = localStorage.getItem('authToken');
            const userRole = localStorage.getItem('userRole');
            const username = localStorage.getItem('username');
            
            if (!authToken) {
                window.location.href = '/login';
            }
            
            // Display user info
            document.getElementById('username').textContent = username || 'User';
            document.getElementById('userRole').textContent = userRole || 'viewer';
            
            function logout() {
                localStorage.removeItem('authToken');
                localStorage.removeItem('userRole');
                localStorage.removeItem('username');
                window.location.href = '/';
            }
            
            function showResult(message) {
                const results = document.getElementById('results');
                const resultDiv = document.createElement('div');
                resultDiv.className = 'result-item';
                resultDiv.innerHTML = '<strong>' + new Date().toLocaleTimeString() + ':</strong> ' + message;
                results.insertBefore(resultDiv, results.firstChild);
            }

            // Form handlers
            document.getElementById('orgForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                const response = await fetch('/organizations', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': 'Bearer ' + authToken
                    },
                    body: JSON.stringify({
                        name: document.getElementById('orgName').value
                    })
                });
                const data = await response.json();
                showResult('Organization: ' + JSON.stringify(data));
                if (response.ok) document.getElementById('orgForm').reset();
            });

            document.getElementById('deptForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                const response = await fetch('/departments', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': 'Bearer ' + authToken
                    },
                    body: JSON.stringify({
                        name: document.getElementById('deptName').value,
                        org_id: parseInt(document.getElementById('deptOrgId').value)
                    })
                });
                const data = await response.json();
                showResult('Department: ' + JSON.stringify(data));
                if (response.ok) document.getElementById('deptForm').reset();
            });

            document.getElementById('resourceForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                const response = await fetch('/resources', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': 'Bearer ' + authToken
                    },
                    body: JSON.stringify({
                        name: document.getElementById('resourceName').value,
                        content: document.getElementById('resourceContent').value
                    })
                });
                const data = await response.json();
                showResult('Resource: ' + JSON.stringify(data));
                if (response.ok) document.getElementById('resourceForm').reset();
            });

            document.getElementById('guestForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                const response = await fetch('/guest-links', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': 'Bearer ' + authToken
                    },
                    body: JSON.stringify({
                        resource_id: parseInt(document.getElementById('guestResourceId').value),
                        permission: document.getElementById('guestPermission').value
                    })
                });
                const data = await response.json();
                showResult('Guest Link: ' + JSON.stringify(data));
                if (response.ok) document.getElementById('guestForm').reset();
            });
        </script>
    </body>
    </html>
    ''')

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'message': 'Username already exists'}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'Email already exists'}), 400
    
    user = User(
        username=data['username'],
        email=data['email'],
        password_hash=generate_password_hash(data['password']),
        role=data.get('role', 'viewer')
    )
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({'message': 'User registered successfully', 'user_id': user.id}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    
    if user and check_password_hash(user.password_hash, data['password']):
        access_token = create_access_token(identity=user.id)
        return jsonify({'access_token': access_token, 'role': user.role}), 200
    
    return jsonify({'message': 'Invalid credentials'}), 401

@app.route('/organizations', methods=['POST'])
@jwt_required()
def create_organization():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not check_permission(user.role, 'create'):
        return jsonify({'message': 'Insufficient permissions'}), 403
    
    data = request.get_json()
    org = Organization(name=data['name'])
    db.session.add(org)
    db.session.commit()
    
    # Assign user to organization
    user.org_id = org.id
    db.session.commit()
    
    return jsonify({'message': 'Organization created', 'org_id': org.id}), 201

@app.route('/departments', methods=['POST'])
@jwt_required()
def create_department():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not check_permission(user.role, 'create'):
        return jsonify({'message': 'Insufficient permissions'}), 403
    
    data = request.get_json()
    dept = Department(name=data['name'], org_id=data['org_id'])
    db.session.add(dept)
    db.session.commit()
    
    return jsonify({'message': 'Department created', 'dept_id': dept.id}), 201

@app.route('/resources', methods=['POST'])
@jwt_required()
def create_resource():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not check_permission(user.role, 'create'):
        return jsonify({'message': 'Insufficient permissions'}), 403
    
    data = request.get_json()
    resource = Resource(
        name=data['name'],
        content=data.get('content', ''),
        owner_id=current_user_id,
        org_id=user.org_id or 1  # Default org if none
    )
    db.session.add(resource)
    db.session.commit()
    
    return jsonify({'message': 'Resource created', 'resource_id': resource.id}), 201

@app.route('/resources/<int:resource_id>', methods=['GET'])
@jwt_required()
def get_resource(resource_id):
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not check_permission(user.role, 'read'):
        return jsonify({'message': 'Insufficient permissions'}), 403
    
    resource = Resource.query.get_or_404(resource_id)
    return jsonify({
        'id': resource.id,
        'name': resource.name,
        'content': resource.content,
        'owner_id': resource.owner_id
    })

@app.route('/guest-links', methods=['POST'])
@jwt_required()
def create_guest_link():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not check_permission(user.role, 'share'):
        return jsonify({'message': 'Insufficient permissions'}), 403
    
    data = request.get_json()
    resource = Resource.query.get_or_404(data['resource_id'])
    
    # Check if user owns the resource or has admin rights
    if resource.owner_id != current_user_id and user.role != 'admin':
        return jsonify({'message': 'Can only share your own resources'}), 403
    
    guest_link = GuestLink(
        token=str(uuid.uuid4()),
        resource_id=data['resource_id'],
        permission=data.get('permission', 'view'),
        expires_at=datetime.utcnow() + timedelta(days=7)
    )
    db.session.add(guest_link)
    db.session.commit()
    
    return jsonify({
        'message': 'Guest link created',
        'token': guest_link.token,
        'url': f'/guest/{guest_link.token}'
    }), 201

@app.route('/guest/<token>', methods=['GET'])
def guest_access(token):
    guest_link = GuestLink.query.filter_by(token=token).first_or_404()
    
    if guest_link.expires_at and guest_link.expires_at < datetime.utcnow():
        return jsonify({'message': 'Guest link expired'}), 410
    
    resource = guest_link.resource
    return jsonify({
        'resource_name': resource.name,
        'content': resource.content,
        'permission': guest_link.permission,
        'expires_at': guest_link.expires_at.isoformat() if guest_link.expires_at else None
    })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)