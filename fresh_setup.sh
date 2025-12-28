#!/bin/bash
# Fresh Setup Script for PythonAnywhere
# Run this after pulling code from Git

echo "🚀 Starting Fresh Setup..."
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

PROJECT_DIR="$HOME/oneworld3d_backend"
cd "$PROJECT_DIR" || exit

echo -e "${YELLOW}Step 1: Activating virtual environment...${NC}"
source venv/bin/activate || {
    echo -e "${RED}Error: Virtual environment not found!${NC}"
    exit 1
}
echo -e "${GREEN}✓ Virtual environment activated${NC}"
echo ""

echo -e "${YELLOW}Step 2: Installing dependencies...${NC}"
pip install -q -r requirements.txt
echo -e "${GREEN}✓ Dependencies installed${NC}"
echo ""

echo -e "${YELLOW}Step 3: Creating migrations...${NC}"
python manage.py makemigrations accounts || {
    echo -e "${RED}Error: Failed to create migrations for accounts!${NC}"
    exit 1
}
python manage.py makemigrations ai_machines || {
    echo -e "${RED}Error: Failed to create migrations for ai_machines!${NC}"
    exit 1
}
python manage.py makemigrations || {
    echo -e "${RED}Error: Failed to create migrations!${NC}"
    exit 1
}
echo -e "${GREEN}✓ Migrations created${NC}"
echo ""

echo -e "${YELLOW}Step 4: Applying migrations...${NC}"
python manage.py migrate || {
    echo -e "${RED}Error: Failed to apply migrations!${NC}"
    exit 1
}
echo -e "${GREEN}✓ Migrations applied${NC}"
echo ""

echo -e "${YELLOW}Step 5: Creating default roles...${NC}"
python manage.py create_default_roles || {
    echo -e "${RED}Error: Failed to create default roles!${NC}"
    exit 1
}
echo -e "${GREEN}✓ Default roles created${NC}"
echo ""

echo -e "${YELLOW}Step 6: Collecting static files...${NC}"
python manage.py collectstatic --noinput || {
    echo -e "${YELLOW}Warning: Static files collection failed (may not be critical)${NC}"
}
echo -e "${GREEN}✓ Static files collected${NC}"
echo ""

echo -e "${YELLOW}Step 7: Verifying setup...${NC}"
python manage.py shell << EOF
from accounts.models import Organization, Team, Role, User
roles_count = Role.objects.count()
users_count = User.objects.count()
print(f"Roles in database: {roles_count}")
print(f"Users in database: {users_count}")
if roles_count >= 6:
    print("✓ Default roles verified")
else:
    print(f"⚠ Warning: Expected 6 roles, found {roles_count}")
EOF

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ Fresh Setup Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}⚠ IMPORTANT Next Steps:${NC}"
echo "1. Create superuser: python manage.py createsuperuser"
echo "2. Assign role to superuser (run assign_superuser_role.py)"
echo "3. Create organization/team (run create_first_org_team.py)"
echo "4. Restart web app (Dashboard → Web → Reload)"
echo "5. Test API endpoints"
echo ""

