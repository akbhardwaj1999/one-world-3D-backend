#!/bin/bash
# Quick Deployment Script for User Management System on PythonAnywhere
# Run this script on PythonAnywhere Bash Console

echo "🚀 Starting User Management System Deployment..."
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Get project directory (adjust if needed)
PROJECT_DIR="$HOME/oneworld3d_backend"
cd "$PROJECT_DIR" || exit

echo -e "${YELLOW}Step 1: Activating virtual environment...${NC}"
source venv/bin/activate || {
    echo -e "${RED}Error: Virtual environment not found!${NC}"
    exit 1
}
echo -e "${GREEN}✓ Virtual environment activated${NC}"
echo ""

echo -e "${YELLOW}Step 2: Installing/Updating dependencies...${NC}"
pip install -q python-dotenv django-rest-framework-simplejwt
echo -e "${GREEN}✓ Dependencies installed${NC}"
echo ""

echo -e "${YELLOW}Step 3: Creating migrations...${NC}"
python manage.py makemigrations accounts || {
    echo -e "${RED}Error: Failed to create migrations!${NC}"
    exit 1
}
echo -e "${GREEN}✓ Migrations created${NC}"
echo ""

echo -e "${YELLOW}Step 4: Applying migrations...${NC}"
python manage.py migrate accounts || {
    echo -e "${RED}Error: Failed to apply migrations!${NC}"
    exit 1
}
python manage.py migrate || {
    echo -e "${RED}Error: Failed to apply general migrations!${NC}"
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

echo -e "${YELLOW}Step 7: Verifying deployment...${NC}"
python manage.py shell << EOF
from accounts.models import Organization, Team, Role, User, StoryAccess, Invitation
roles_count = Role.objects.count()
users_count = User.objects.count()
print(f"Roles in database: {roles_count}")
print(f"Users in database: {users_count}")
if roles_count >= 6:
    print("✓ Default roles verified")
else:
    print("⚠ Warning: Expected 6 roles, found {roles_count}")
EOF

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ Deployment Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}⚠ IMPORTANT: Don't forget to:${NC}"
echo "1. Restart your web app (Reload button in PythonAnywhere dashboard)"
echo "2. Check error logs if anything doesn't work"
echo "3. Test API endpoints"
echo ""
echo "Next steps:"
echo "- Assign roles to existing users"
echo "- Create first organization and team"
echo "- Test frontend integration"
echo ""

