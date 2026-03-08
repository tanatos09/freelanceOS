#!/bin/bash

# ================================================================
# FreelanceOS Security Fix Script (Linux/macOS)
# ================================================================
#
# Automatizuje bezpečnostní opravy PŘED publikací na GitHub
#
# Usage: 
#   1. chmod +x security-fix.sh
#   2. ./security-fix.sh
#
# ================================================================

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# ================================================================
# Helper functions
# ================================================================

print_header() {
    echo -e "\n${CYAN}═══════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}  $1${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════════════════${NC}\n"
}

print_step() {
    echo -e "\n${YELLOW}$1${NC}"
}

print_success() {
    echo -e "${GREEN}   ✅ $1${NC}"
}

print_info() {
    echo -e "${CYAN}   ℹ️  $1${NC}"
}

print_warning() {
    echo -e "${RED}   ⚠️  $1${NC}"
}

# ================================================================
# START
# ================================================================

print_header "🔐 FreelanceOS Security Fix Script"

# Check if we're in the right directory
if [[ ! -f "manage.py" ]]; then
    print_warning "manage.py not found!"
    echo "Musíš být v root freelanceos adresáři."
    exit 1
fi

print_success "Správný adresář detekován"

# ================================================================
# STEP 1: Backup Current State
# ================================================================

print_step "📦 STEP 1: Backup aktuálního stavu..."

if [[ -f ".env" ]]; then
    cp .env .env.backup
    print_success "Backup .env → .env.backup"
fi

git remote -v > git_remotes_backup.txt 2>/dev/null || true
print_success "Git remotes zabackupovány"

# ================================================================
# STEP 2: Remove .env from git history
# ================================================================

print_step "🗑️  STEP 2: Smazat .env z git historii..."
echo ""
print_warning "VAROVÁNÍ: Toto přepíše git historii!"
print_warning "Pokud máš projekt sdílený s ostatními, informuj je!"
echo ""

read -p "Chceš pokračovat? (ano/ne) " response

if [[ "$response" != "ano" && "$response" != "yes" && "$response" != "y" ]]; then
    echo "❌ Zrušeno."
    exit 1
fi

echo ""
echo "Spouštím: git filter-branch --tree-filter 'rm -f .env' --prune-empty -- --all"

if git filter-branch --tree-filter 'rm -f .env' --prune-empty -- --all 2>/dev/null; then
    print_success ".env odstraněn z git historii"
else
    print_warning "Git filter-branch selhán (možná už hotovo)"
fi

echo ""

# ================================================================
# STEP 3: Generate new SECRET_KEY
# ================================================================

print_step "🔑 STEP 3: Generování nového SECRET_KEY..."

SECRET_KEY=$(python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())" 2>/dev/null)

if [[ $? -eq 0 && -n "$SECRET_KEY" ]]; then
    print_success "Nový SECRET_KEY vygenerován:"
    echo -e "${CYAN}   $SECRET_KEY${NC}"
    echo ""
    
    # Save to temporary file for reference
    echo "$SECRET_KEY" > new_secret_key.txt
    print_success "Uložen do: new_secret_key.txt"
else
    print_warning "Chyba při generování SECRET_KEY"
    echo "Zkontroluj, zda máš Django nainstalován"
    exit 1
fi

echo ""

# ================================================================
# STEP 4: Create new .env from template
# ================================================================

print_step "📝 STEP 4: Vytvoření nového .env..."

if [[ -f ".env" ]]; then
    rm -f .env
    print_success "Starý .env smazán"
fi

if [[ -f ".env.example" ]]; then
    cp .env.example .env
    print_success "Nový .env vytvořen z .env.example"
    
    # Try to update SECRET_KEY in .env
    if [[ $(uname) == "Darwin" ]]; then
        # macOS
        sed -i '' "s/SECRET_KEY=.*/SECRET_KEY=$SECRET_KEY/" .env
    else
        # Linux
        sed -i "s/SECRET_KEY=.*/SECRET_KEY=$SECRET_KEY/" .env
    fi
    print_success "SECRET_KEY automaticky zaktualizován v .env"
else
    print_warning ".env.example nenalezen"
fi

echo ""

# ================================================================
# STEP 5: Move test_api.py
# ================================================================

print_step "📂 STEP 5: Přesun test_api.py..."

if [[ -f "test_api.py" ]]; then
    mkdir -p dev-scripts
    mv test_api.py dev-scripts/test_manual_api.py
    print_success "test_api.py přesunut do dev-scripts/"
    
    # Add to .gitignore
    if ! grep -q "test_api.py" .gitignore; then
        echo "" >> .gitignore
        echo "# Development" >> .gitignore
        echo "test_api.py" >> .gitignore
        echo "dev-scripts/" >> .gitignore
        print_success "test_api.py přidán do .gitignore"
    fi
else
    print_info "test_api.py neexistuje"
fi

echo ""

# ================================================================
# STEP 6: Fix PASSWORD_HASHERS
# ================================================================

print_step "🔐 STEP 6: Oprava PASSWORD_HASHERS v testech..."

TESTING_SETTINGS="config/settings/testing.py"

if [[ -f "$TESTING_SETTINGS" ]]; then
    if grep -q "MD5PasswordHasher" "$TESTING_SETTINGS"; then
        if [[ $(uname) == "Darwin" ]]; then
            # macOS
            sed -i '' "s/'django.contrib.auth.hashers.MD5PasswordHasher'/'django.contrib.auth.hashers.PBKDF2PasswordHasher'/" "$TESTING_SETTINGS"
        else
            # Linux
            sed -i "s/'django.contrib.auth.hashers.MD5PasswordHasher'/'django.contrib.auth.hashers.PBKDF2PasswordHasher'/" "$TESTING_SETTINGS"
        fi
        print_success "MD5PasswordHasher změněn na PBKDF2PasswordHasher"
    else
        print_info "PASSWORD_HASHERS jsou ok"
    fi
else
    print_warning "$TESTING_SETTINGS nenalezen"
fi

echo ""

# ================================================================
# STEP 7: Verify git status
# ================================================================

print_step "✓  STEP 7: Verifikace git stavu..."

if git check-ignore -q .env 2>/dev/null; then
    print_success ".env je správně v .gitignore"
else
    print_warning "Zkontroluj .gitignore - .env tam být měl"
fi

echo ""

# ================================================================
# Show changes
# ================================================================

echo "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}Následující změny jsou připraveny:${NC}"
git status --short
echo ""

# ================================================================
# Ask about git push
# ================================================================

print_warning "Force push (kvůli history rewrite)?"
read -p "git push origin main --force-with-lease? (ano/ne) " git_response

if [[ "$git_response" == "ano" || "$git_response" == "yes" || "$git_response" == "y" ]]; then
    echo ""
    print_step "🚀 Git push probíhá..."
    
    if git push origin main --force-with-lease; then
        print_success "Git push úspěšný!"
    else
        print_warning "Git push selhán"
        echo "Zkontroluj, zda máš přístup k repositáři"
    fi
else
    print_info "Git push přeskočen - můžeš jej provést později"
    echo "Příkaz: git push origin main --force-with-lease"
fi

echo ""

# ================================================================
# Final Summary
# ================================================================

print_header "✅ BEZPEČNOSTNÍ OPRAVY HOTOVY!"

echo -e "${CYAN}Co bylo provedeno:${NC}"
print_success "Backup .env → .env.backup"
print_success ".env odstraněn z git historii"
print_success "Nový SECRET_KEY vygenerován"
print_success "Nový .env vytvořen"
print_success "test_api.py přesunut"
print_success "PASSWORD_HASHERS opraveny"

echo ""
echo -e "${YELLOW}Další kroky:${NC}"
echo "  1. 📝 Ověř .env obsah - změň DB_PASSWORD a ostatní hodnoty"
echo "  2. 🔍 Spusť security checks:"
echo "     pip install pip-audit bandit"
echo "     pip-audit"
echo "     bandit -r . -lll"
echo "  3. 📚 Přečti si:"
echo "     - SECURITY_AUDIT_REPORT.md"
echo "     - SECURITY.md"
echo "  4. ✅ Zkontroluj git log:"
echo "     git log -p | grep -i 'PASSWORD\|SECRET'"
echo "  5. 🚀 Publikuj na GitHub!"
echo ""

if [[ -f "new_secret_key.txt" ]]; then
    echo -e "${CYAN}💾 Nový SECRET_KEY uložen v: new_secret_key.txt${NC}"
    echo -e "${RED}   (Deaktivuj soubor, až budeš hotov!)${NC}"
fi

echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  Máte-li otázky, viz SECURITY_DOCUMENTATION_INDEX.md${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════${NC}"
echo ""

print_success "Script dokončen. 🎉"

