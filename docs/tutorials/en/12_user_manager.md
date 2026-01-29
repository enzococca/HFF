# User Management

This tutorial explains how to manage users and permissions in HFF Survey for multi-user environments.

## Overview

HFF includes a user management system for PostgreSQL databases that allows:

- Multiple users to access the same database
- Role-based permissions
- Audit trails of who created/modified records
- Access control for sensitive data

> **Note**: User management is only available with PostgreSQL databases. SQLite databases do not support multi-user access.

---

## Opening User Management

1. Click **HFF Menu > Configuration > User Management**
2. Or click the **User Management** icon ![Users](icons/iconConn.png) in the toolbar

---

## User Roles

HFF supports three built-in roles:

| Role | Description | Permissions |
|------|-------------|-------------|
| **Admin** | Full system access | Create/delete users, all data operations, configuration |
| **Editor** | Data management | Create, read, update, delete records |
| **Viewer** | Read-only access | View records only, no modifications |

---

## Login

When user management is enabled:

1. A login dialog appears when opening HFF forms
2. Enter your **Username** and **Password**
3. Click **OK** to authenticate
4. Your role determines available actions

---

## Managing Users (Admin Only)

### Creating a New User

1. Open User Management dialog
2. Click **Add User** button
3. Fill in the user details:
   - **Username**: Unique login name
   - **Password**: Secure password
   - **Email**: Contact email (optional)
   - **Role**: Select Admin, Editor, or Viewer
4. Click **Save**

### Editing a User

1. Select the user from the list
2. Click **Edit** button
3. Modify the details as needed
4. Click **Save**

### Deleting a User

1. Select the user from the list
2. Click **Delete** button
3. Confirm the deletion

> **Warning**: Deleting a user does not delete their records. Records remain attributed to the deleted user.

---

## Changing Your Password

1. Open User Management dialog
2. Go to **Profile** tab
3. Enter your current password
4. Enter your new password
5. Confirm new password
6. Click **Change Password**

---

## Permission Details

### Admin Permissions

- Create, edit, delete users
- Access all forms and records
- Export all data
- Modify configuration
- Backup/restore database

### Editor Permissions

- Create new records
- Edit own records
- Edit records (if allowed by admin)
- Export data
- View all records

### Viewer Permissions

- View all records
- Export data (read-only)
- Cannot create or modify records

---

## Session Management

### Timeout Settings

Admins can configure:

- **Session Timeout**: Auto-logout after inactivity
- **Remember Me**: Option to stay logged in

### Active Sessions

View and manage active sessions:

1. Go to **Sessions** tab
2. See all currently logged-in users
3. Admins can force logout other users

---

## Audit Trail

When enabled, HFF tracks:

- Who created each record
- Who last modified each record
- Timestamp of changes

### Viewing Audit Information

Each record shows:

- **Created by**: Username of creator
- **Created date**: When record was created
- **Modified by**: Username of last modifier
- **Modified date**: When record was last changed

---

## Enabling User Management

### First-Time Setup

1. Connect to PostgreSQL database
2. Open User Management
3. Click **Initialize User System**
4. Create the first admin user
5. Enable user authentication

### Configuration Options

| Option | Description |
|--------|-------------|
| **Require Login** | Force authentication for all forms |
| **Allow Registration** | Let users self-register (admin approval) |
| **Password Policy** | Minimum length, complexity requirements |
| **Session Duration** | How long sessions remain active |

---

## Best Practices

### Security

- Use strong, unique passwords
- Don't share admin credentials
- Review user list regularly
- Remove inactive users

### Organization

- Create users for each team member
- Assign minimum required permissions
- Use descriptive usernames
- Document who has admin access

---

## Troubleshooting

### Cannot Login

- Verify username spelling
- Check Caps Lock
- Contact admin to reset password

### Permission Denied

- Verify your role has required permissions
- Contact admin to upgrade access

### User Management Not Available

- Ensure you're using PostgreSQL
- Check database connection
- Verify you have admin privileges

---

*Next: [Pottery Conservation Form](13_pottery_conservation_form.md)*
