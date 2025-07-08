# Task 2: Role-Based Access Control (RBAC) System

## Overview

This is a simple RBAC system built with Flask that demonstrates:
- User authentication with JWT tokens
- Organization and Department management  
- Role-based permissions (Admin, Manager, Contributor, Viewer)
- Resource management with CRUD operations
- Guest link sharing with time-based expiration

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Flask API     │    │   SQLite DB     │
│   (HTML/JS)     │◄──►│   (JWT Auth)    │◄──►│   (User Data)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### System Flow Diagram

```
┌─────────────┐
│ User Access │
└─────┬───────┘
      │
      ▼
┌─────────────┐    No     ┌──────────────┐
│ Authenticated│ ───────► │ Login/Register│
│    User?    │          │    Page      │
└─────┬───────┘          └──────────────┘
      │ Yes
      ▼
┌─────────────┐
│Check Role & │
│ Permissions │
└─────┬───────┘
      │
      ▼
┌─────────────┐    Denied  ┌──────────────┐
│  Permission │ ─────────► │ Access Denied │
│  Granted?   │            │   Message    │
└─────┬───────┘            └──────────────┘
      │ Granted
      ▼
┌─────────────┐
│   Execute   │
│  Operation  │
│(CRUD/Share) │
└─────────────┘
```

### Database Schema

```
Users ──┐
        ├─── Organizations ──── Departments
        │
        └─── Resources ──── GuestLinks
```

### Guest Link Flow

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│Create Guest │─────►│Generate Token│─────►│Share Link   │
│    Link     │      │& Expiration  │      │Publicly     │
└─────────────┘      └──────────────┘      └─────────────┘
                            │
                            ▼
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   Access    │◄─────│Validate Token│◄─────│Guest Clicks │
│  Resource   │      │& Expiration  │      │    Link     │
└─────────────┘      └──────────────┘      └─────────────┘
```

## Role Permissions

| Role        | Create | Read | Update | Delete | Share |
|-------------|--------|------|--------|--------|-------|
| Admin       | ✓      | ✓    | ✓      | ✓      | ✓     |
| Manager     | ✓      | ✓    | ✓      | ✗      | ✓     |
| Contributor | ✓      | ✓    | ✓      | ✗      | ✗     |
| Viewer      | ✗      | ✓    | ✗      | ✗      | ✗     |

## Setup Instructions

### 1. Create Project Structure
```bash
mkdir Task_2
cd Task_2
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Application
```bash
python app.py
```

### 4. Access the System
- Open browser: `http://localhost:5000`
- Use the web interface to test all functionality

## API Endpoints

### Authentication
- `POST /register` - Register new user
- `POST /login` - Login and get JWT token

### Organizations & Departments
- `POST /organizations` - Create organization (requires auth)
- `POST /departments` - Create department (requires auth)

### Resources
- `POST /resources` - Create resource (requires auth)
- `GET /resources/<id>` - Get resource (requires auth)

### Guest Links
- `POST /guest-links` - Create shareable guest link (requires auth)
- `GET /guest/<token>` - Access resource via guest link (no auth)

## Testing Flow

### Step 1: Register Users
1. Register an Admin user
2. Register a Viewer user
3. Register a Manager user

### Step 2: Create Organization Structure
1. Login as Admin
2. Create an organization
3. Create departments under the organization

### Step 3: Test Resource Management
1. Create resources as different users
2. Try to access resources with different roles
3. Verify permission restrictions

### Step 4: Test Guest Links
1. Create a guest link as Admin/Manager
2. Try to access the guest link without authentication
3. Verify expiration and permission levels

## What to Test

### ✅ Authentication
- [ ] User registration works
- [ ] Login returns JWT token
- [ ] Invalid credentials are rejected

### ✅ Role-Based Access
- [ ] Admin can create organizations
- [ ] Viewer cannot create resources
- [ ] Manager can share resources
- [ ] Contributor cannot share resources

### ✅ Guest Links
- [ ] Guest links work without authentication
- [ ] Expired links are rejected
- [ ] Permission levels are respected

### ✅ Data Integrity
- [ ] Organizations contain departments
- [ ] Resources are linked to owners
- [ ] Users are assigned to organizations

## How to Know It's Working

### Success Indicators:
1. **Web Interface Loads** - You see the form interface at `http://localhost:5000`
2. **Registration Success** - Users can register and receive confirmation
3. **Authentication Works** - Login returns a token and saves it
4. **Permission Enforcement** - Different roles have different access levels
5. **Guest Access** - Guest links work without authentication
6. **Data Persistence** - Data is saved and retrieved correctly

### Common Issues:
- **Port Already in Use** - Change port in `app.py` or kill existing process
- **Database Errors** - Delete `rbac.db` file and restart
- **JWT Errors** - Check if token is being sent in Authorization header

## Quick Test Commands

```bash
# Register admin user
curl -X POST http://localhost:5000/register \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","email":"admin@test.com","password":"password","role":"admin"}'

# Login
curl -X POST http://localhost:5000/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"password"}'

# Create organization (use token from login)
curl -X POST http://localhost:5000/organizations \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{"name":"Test Org"}'
```

## File Structure

```
Task_2/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── README.md          # This file
└── rbac.db            # SQLite database (created automatically)
```

## Demo Flow

1. **Setup** (30 seconds)
   - Show project structure
   - Run `python app.py`
   - Open browser to `http://localhost:5000`

2. **User Registration** (1 minute)
   - Register Admin user
   - Register Viewer user
   - Show different roles available

3. **Authentication** (30 seconds)
   - Login as Admin
   - Show JWT token is saved
   - Demonstrate login failure with wrong credentials

4. **Organization Setup** (1 minute)
   - Create organization as Admin
   - Create department under organization
   - Show hierarchy structure

5. **Resource Management** (1.5 minutes)
   - Create resource as Admin
   - Login as Viewer
   - Try to create resource (should fail)
   - Show permission enforcement

6. **Guest Link Demo** (1 minute)
   - Create guest link as Admin
   - Access resource via guest link
   - Show no authentication required
   - Test different permission levels

**Total Demo Time: ~5 minutes**