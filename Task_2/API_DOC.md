# RBAC System API Documentation

## Base URL
```
http://localhost:5000
```

## Authentication
Most endpoints require JWT token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

## Response Format
All responses are in JSON format:
```json
{
  "message": "Success message",
  "data": { ... },
  "error": "Error message if applicable"
}
```

## Endpoints

### Authentication

#### Register User
```
POST /register
Content-Type: application/json

{
  "username": "johndoe",
  "email": "john@example.com", 
  "password": "password123",
  "role": "viewer"  // Optional: admin, manager, contributor, viewer
}
```

**Response (201):**
```json
{
  "message": "User registered successfully",
  "user_id": 1
}
```

**Errors:**
- 400: Username/email already exists

#### Login
```
POST /login
Content-Type: application/json

{
  "username": "johndoe",
  "password": "password123"
}
```

**Response (200):**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "role": "admin"
}
```

**Errors:**
- 401: Invalid credentials

### Organizations

#### Create Organization
```
POST /organizations
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Tech Corp"
}
```

**Required Permission:** create
**Response (201):**
```json
{
  "message": "Organization created",
  "org_id": 1
}
```

**Errors:**
- 403: Insufficient permissions

### Departments

#### Create Department
```
POST /departments
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Engineering",
  "org_id": 1
}
```

**Required Permission:** create
**Response (201):**
```json
{
  "message": "Department created", 
  "dept_id": 1
}
```

### Resources

#### Create Resource
```
POST /resources
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Project Document",
  "content": "This is the project content..."
}
```

**Required Permission:** create
**Response (201):**
```json
{
  "message": "Resource created",
  "resource_id": 1
}
```

#### Get Resource
```
GET /resources/<resource_id>
Authorization: Bearer <token>
```

**Required Permission:** read
**Response (200):**
```json
{
  "id": 1,
  "name": "Project Document",
  "content": "This is the project content...",
  "owner_id": 1
}
```

**Errors:**
- 404: Resource not found
- 403: Insufficient permissions

### Guest Links

#### Create Guest Link
```
POST /guest-links
Authorization: Bearer <token>
Content-Type: application/json

{
  "resource_id": 1,
  "permission": "view"  // view or edit
}
```

**Required Permission:** share
**Ownership Rule:** Must own resource or be admin
**Response (201):**
```json
{
  "message": "Guest link created",
  "token": "a1b2c3d4-e5f6-7890-abcd-1234567890ef",
  "url": "/guest/a1b2c3d4-e5f6-7890-abcd-1234567890ef"
}
```

#### Access Guest Resource
```
GET /guest/<token>
```

**No Authentication Required**
**Response (200):**
```json
{
  "resource_name": "Project Document",
  "content": "This is the project content...",
  "permission": "view",
  "expires_at": "2024-01-15T10:30:00"
}
```

**Errors:**
- 404: Invalid token
- 410: Link expired

## Permission Matrix

| Role        | Create | Read | Update | Delete | Share |
|-------------|--------|------|--------|--------|-------|
| Admin       | ✓      | ✓    | ✓      | ✓      | ✓     |
| Manager     | ✓      | ✓    | ✓      | ✗      | ✓     |
| Contributor | ✓      | ✓    | ✓      | ✗      | ✗     |
| Viewer      | ✗      | ✓    | ✗      | ✗      | ✗     |

## Error Codes

### 400 Bad Request
- Invalid JSON format
- Missing required fields
- Validation errors

### 401 Unauthorized  
- Missing JWT token
- Invalid JWT token
- Expired JWT token

### 403 Forbidden
- Insufficient role permissions
- Resource ownership violations

### 404 Not Found
- Resource doesn't exist
- Invalid guest token

### 410 Gone
- Expired guest link

## Rate Limiting
Currently not implemented. In production, recommend:
- 100 requests/minute per user for authenticated endpoints
- 10 requests/minute per IP for guest links

## Testing Examples

### Complete User Flow
```bash
# 1. Register admin user
curl -X POST http://localhost:5000/register \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","email":"admin@test.com","password":"password","role":"admin"}'

# 2. Login
curl -X POST http://localhost:5000/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"password"}'

# Save the token from response
export TOKEN="your_token_here"

# 3. Create organization
curl -X POST http://localhost:5000/organizations \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"name":"Test Corp"}'

# 4. Create department
curl -X POST http://localhost:5000/departments \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"name":"Engineering","org_id":1}'

# 5. Create resource
curl -X POST http://localhost:5000/resources \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"name":"Test Document","content":"This is test content"}'

# 6. Create guest link
curl -X POST http://localhost:5000/guest-links \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"resource_id":1,"permission":"view"}'

# 7. Access via guest link (no auth required)
curl -X GET http://localhost:5000/guest/GUEST_TOKEN_HERE
```

### Permission Testing
```bash
# Register viewer user
curl -X POST http://localhost:5000/register \
  -H "Content-Type: application/json" \
  -d '{"username":"viewer","email":"viewer@test.com","password":"password","role":"viewer"}'

# Login as viewer
curl -X POST http://localhost:5000/login \
  -H "Content-Type: application/json" \
  -d '{"username":"viewer","password":"password"}'

# Try to create resource (should fail with 403)
curl -X POST http://localhost:5000/resources \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $VIEWER_TOKEN" \
  -d '{"name":"Should Fail","content":"This should not work"}'
```

## Security Notes

### JWT Token Security
- Tokens expire (configure in app settings)
- Use HTTPS in production
- Store tokens securely on client side

### Guest Link Security  
- Links expire after 7 days
- Tokens are UUIDs (non-guessable)
- Limited permissions (view/edit only)
- Resource ownership validation

### Input Validation
- All inputs are validated
- SQLAlchemy prevents SQL injection
- Password hashing with Werkzeug

## Production Considerations

### Security
- Switch to PostgreSQL for production
- Add proper indexing
- Connection pooling
- Backup strategy

### Security
- HTTPS enforcement
- Rate limiting
- CORS configuration
- CSP headers
- Audit logging

### Monitoring
- Health check endpoints
- Metrics collection
- Error tracking
- Performance monitoring