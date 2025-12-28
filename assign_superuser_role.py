"""
Script to assign Super Admin role to superuser
Run this on PythonAnywhere after creating superuser:

python manage.py shell < assign_superuser_role.py
"""

from accounts.models import User, Role

# Get superuser
superusers = User.objects.filter(is_superuser=True)

if not superusers.exists():
    print("⚠ No superuser found!")
    print("Please create superuser first: python manage.py createsuperuser")
    exit()

# Get Super Admin role
try:
    super_admin_role = Role.objects.get(name='Super Admin')
except Role.DoesNotExist:
    print("⚠ Super Admin role not found!")
    print("Please run: python manage.py create_default_roles")
    exit()

# Assign role to all superusers
updated_count = 0
for superuser in superusers:
    if superuser.role != super_admin_role:
        superuser.role = super_admin_role
        superuser.save()
        print(f"✅ Assigned Super Admin role to: {superuser.email}")
        updated_count += 1
    else:
        print(f"ℹ {superuser.email} already has Super Admin role")

if updated_count > 0:
    print(f"\n✅ Successfully assigned roles to {updated_count} superuser(s)!")
else:
    print("\nℹ All superusers already have Super Admin role")

