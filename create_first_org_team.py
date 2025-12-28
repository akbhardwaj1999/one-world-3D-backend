"""
Script to create first organization and team
Run this on PythonAnywhere after deployment:

python manage.py shell < create_first_org_team.py
"""

from accounts.models import Organization, Team

# Create organization
org_name = "My Organization"  # Change this to your organization name
org, created = Organization.objects.get_or_create(
    name=org_name,
    defaults={'slug': org_name.lower().replace(' ', '-')}
)

if created:
    print(f"✅ Created organization: {org.name}")
else:
    print(f"ℹ Organization already exists: {org.name}")

# Create team
team_name = "Main Team"  # Change this to your team name
team, created = Team.objects.get_or_create(
    organization=org,
    name=team_name,
    defaults={'description': 'Primary production team'}
)

if created:
    print(f"✅ Created team: {team.name} (in {org.name})")
else:
    print(f"ℹ Team already exists: {team.name}")

print(f"\nOrganization ID: {org.id}")
print(f"Team ID: {team.id}")
print("\nYou can now assign users to this organization and team via the admin panel or API.")

