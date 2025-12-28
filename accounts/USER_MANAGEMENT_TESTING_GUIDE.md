# User Management Testing Guide

## 📋 Overview

This guide explains how to test the User Management & Permissions System using dummy data and test cases.

## 🚀 Quick Start

### 1. Create Dummy Data

Run the management command to create dummy data for frontend testing:

```bash
cd backend
python manage.py create_dummy_user_data --count 20
```

This will create:
- **20 Organizations** (Tech Studios, Creative Labs, etc.)
- **20 Teams** (Development Team, Design Team, etc.)
- **20 Custom Roles** (Senior Developer, Junior Developer, etc.)
- **20 Users** (with realistic names and emails)
- **20 Invitations** (with different statuses: pending, accepted, expired, cancelled)

### 2. Default Credentials

After running the command, you can use:

- **Admin User:**
  - Email: `admin@oneworld3d.com` (or `admin@example.com` if already exists)
  - Password: `admin123`

- **Regular Users:**
  - Email: `john.smith@example.com`, `jane.johnson@example.com`, etc.
  - Password: `test123` (for all users)

## 🧪 Running Test Cases

### Run All Tests

```bash
cd backend
python manage.py test accounts.tests
```

### Run Specific Test Class

```bash
# Test User CRUD operations
python manage.py test accounts.tests.UserManagementAPITestCase

# Test Organization operations
python manage.py test accounts.tests.OrganizationAPITestCase

# Test Team operations
python manage.py test accounts.tests.TeamAPITestCase

# Test Role operations
python manage.py test accounts.tests.RoleAPITestCase

# Test Invitation operations
python manage.py test accounts.tests.InvitationAPITestCase

# Test Story Access operations
python manage.py test accounts.tests.StoryAccessAPITestCase

# Test Permission checks
python manage.py test accounts.tests.PermissionTestCase
```

### Run with Verbose Output

```bash
python manage.py test accounts.tests --verbosity=2
```

## 📊 Test Coverage

### ✅ User Management Tests (7 tests)
- List users
- Get user details
- Update user
- Delete user
- Permission checks
- Own profile access

### ✅ Organization Tests (5 tests)
- List organizations
- Create organization
- Get organization details
- Update organization
- Delete organization

### ✅ Team Tests (6 tests)
- List teams
- Create team
- Get team details
- Get team members
- Add team member
- Remove team member

### ✅ Role Tests (7 tests)
- List roles
- Create role
- Get role details
- Update role
- Delete role
- System role protection (update/delete forbidden)

### ✅ Invitation Tests (6 tests)
- List invitations
- Create invitation
- Get invitation by token
- Accept invitation
- Cancel invitation
- Email mismatch validation

### ✅ Story Access Tests (6 tests)
- List story access controls
- Grant access to user
- Grant access to team
- Update access permissions
- Revoke access
- Validation (cannot assign both user and team)

### ✅ Permission Tests (3 tests)
- User permission check
- Superuser has all permissions
- Story access checking

**Total: 40 comprehensive test cases** ✅

## 🎯 Frontend Testing

### 1. Login
- Use admin credentials or any created user
- Test login with different roles

### 2. User Management Page
- View all users
- Create new user
- Edit user details
- Delete user
- Filter by organization/team

### 3. Organization Management
- View all organizations
- Create organization
- Edit organization
- Delete organization

### 4. Team Management
- View all teams
- Create team
- Add members to team
- Remove members from team
- View team members

### 5. Role Management
- View all roles (system + custom)
- Create custom role
- Edit role permissions
- Delete custom role (system roles cannot be deleted)

### 6. Invitation Management
- View all invitations
- Create invitation
- Send invitation
- Resend invitation
- Cancel invitation
- View invitation status (pending, accepted, expired, cancelled)

### 7. Story Access Control
- View story access controls
- Grant access to user
- Grant access to team
- Update access permissions
- Revoke access

## 📝 Test Data Structure

### Organizations
- Tech Studios
- Creative Labs
- Digital Arts
- Animation House
- ... (20 total)

### Teams
- Development Team
- Design Team
- Animation Team
- VFX Team
- ... (20 total)

### Custom Roles
- Senior Developer
- Junior Developer
- Lead Designer
- UI/UX Designer
- 3D Artist
- ... (20 total)

### Users
- john.smith@example.com
- jane.johnson@example.com
- michael.williams@example.com
- ... (20 total)

Each user is assigned:
- An organization
- A team
- A role
- Profile information (bio, phone)

### Invitations
- Various statuses (pending, accepted, expired, cancelled)
- Different organizations and teams
- Different roles

## 🔧 Customization

### Change Count

To create more or fewer items:

```bash
python manage.py create_dummy_user_data --count 50
```

### Reset Data

To start fresh, you can:
1. Delete existing data from Django admin
2. Or run migrations to reset database

## 📚 API Endpoints

All endpoints are tested:

- `GET /api/auth/users/` - List users
- `GET /api/auth/users/{id}/` - Get user details
- `PUT /api/auth/users/{id}/update/` - Update user
- `DELETE /api/auth/users/{id}/delete/` - Delete user

- `GET /api/auth/organizations/` - List organizations
- `POST /api/auth/organizations/` - Create organization
- `GET /api/auth/organizations/{id}/` - Get organization
- `PUT /api/auth/organizations/{id}/` - Update organization
- `DELETE /api/auth/organizations/{id}/` - Delete organization

- `GET /api/auth/teams/` - List teams
- `POST /api/auth/teams/` - Create team
- `GET /api/auth/teams/{id}/` - Get team
- `GET /api/auth/teams/{id}/members/` - Get team members
- `POST /api/auth/teams/{id}/members/` - Add member
- `DELETE /api/auth/teams/{id}/members/{user_id}/` - Remove member

- `GET /api/auth/roles/` - List roles
- `POST /api/auth/roles/` - Create role
- `GET /api/auth/roles/{id}/` - Get role
- `PUT /api/auth/roles/{id}/` - Update role
- `DELETE /api/auth/roles/{id}/` - Delete role

- `GET /api/auth/invitations/` - List invitations
- `POST /api/auth/invitations/` - Create invitation
- `GET /api/auth/invitations/{token}/` - Get invitation by token
- `POST /api/auth/invitations/{id}/accept/` - Accept invitation
- `POST /api/auth/invitations/{id}/cancel/` - Cancel invitation

- `GET /api/auth/story-access/` - List story access
- `POST /api/auth/story-access/` - Create story access
- `GET /api/auth/story-access/{id}/` - Get story access
- `PUT /api/auth/story-access/{id}/` - Update story access
- `DELETE /api/auth/story-access/{id}/` - Delete story access

## ✅ All Tests Passing

All 40 test cases are passing and cover:
- ✅ CRUD operations for all models
- ✅ Permission checks
- ✅ Validation rules
- ✅ Edge cases
- ✅ Error handling

## 🎉 Ready for Frontend Testing!

You now have:
- ✅ Dummy data for frontend testing
- ✅ Comprehensive test suite (40 tests)
- ✅ All tests passing
- ✅ Easy-to-use management command

Happy testing! 🚀

