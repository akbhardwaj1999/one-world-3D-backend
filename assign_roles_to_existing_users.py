"""
Script to assign default roles to existing users
Run this on PythonAnywhere after deployment:

python manage.py shell < assign_roles_to_existing_users.py
"""

from accounts.models import User, Role

# Get roles
try:
    admin_role = Role.objects.get(name='Admin')
    viewer_role = Role.objects.get(name='Viewer')
except Role.DoesNotExist:
    print("Error: Default roles not found!")
    print("Please run: python manage.py create_default_roles")
    exit()

# Assign roles to users
updated_count = 0
for user in User.objects.all():
    if user.role is None:
        if user.is_superuser or user.is_staff:
            user.role = admin_role
            print(f"✓ Assigned Admin role to: {user.email}")
        else:
            user.role = viewer_role
            print(f"✓ Assigned Viewer role to: {user.email}")
        user.save()
        updated_count += 1
    else:
        print(f"- Skipped {user.email} (already has role: {user.role.name})")

print(f"\n✅ Successfully assigned roles to {updated_count} users!")

