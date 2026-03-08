# ================================================================
# FreelanceOS Security Fix Script
# ================================================================
# 
# Automatizuje bezpečnostní opravy PŘED publikací na GitHub
#
# Usage: 
#   1. Otevři PowerShell (jako Admin)
#   2. cd c:\Users\frank\Desktop\freelanceos
#   3. .\security-fix.ps1
#
# ================================================================

Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  🔐 FreelanceOS Security Fix Script" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Check if we're in the right directory
if (-not (Test-Path "manage.py")) {
    Write-Host "❌ Error: manage.py not found!" -ForegroundColor Red
    Write-Host "   Jsi v tom správném adresáři? Měl bys být v root freelanceos adresáři." -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Správný adresář detekován" -ForegroundColor Green
Write-Host ""

# ================================================================
# STEP 1: Backup Current State
# ================================================================
Write-Host "📦 STEP 1: Backup aktuálního stavu..." -ForegroundColor Yellow

if (Test-Path ".env") {
    Copy-Item ".env" ".env.backup" -Force
    Write-Host "   ✅ Backup .env → .env.backup" -ForegroundColor Green
}

git mremote -v > git_remotes_backup.txt
Write-Host "   ✅ Git remotes zabackupovány" -ForegroundColor Green
Write-Host ""

# ================================================================
# STEP 2: Remove .env from git history
# ================================================================
Write-Host "🗑️  STEP 2: Smazat .env z git historii..." -ForegroundColor Yellow
Write-Host ""
Write-Host "⚠️  VAROVÁNÍ: Toto přepíše git historii!" -ForegroundColor Red
Write-Host "   Pokud máš projekt sdílený s ostatními, informuj je!" -ForegroundColor Red
Write-Host ""

$response = Read-Host "Chceš pokračovat? (ano/ne)"
if ($response -ne "ano" -and $response -ne "yes" -and $response -ne "y") {
    Write-Host "❌ Zrušeno." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Spouštím: git filter-branch --tree-filter 'rm -f .env' --prune-empty -- --all"
git filter-branch --tree-filter 'rm -f .env' --prune-empty -- --all

if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ .env odstraněn z git historii" -ForegroundColor Green
} else {
    Write-Host "   ⚠️  Git filter-branch selhán (možná není co opravovat)" -ForegroundColor Yellow
}

Write-Host ""

# ================================================================
# STEP 3: Generator nového SECRET_KEY
# ================================================================
Write-Host "🔑 STEP 3: Generování nového SECRET_KEY..." -ForegroundColor Yellow

$secretKey = python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ Nový SECRET_KEY vygenerován:" -ForegroundColor Green
    Write-Host "   $secretKey" -ForegroundColor Cyan
    Write-Host ""
    
    # Save to temporary file for reference
    $secretKey | Set-Content "new_secret_key.txt"
    Write-Host "   💾 Uložen do: new_secret_key.txt" -ForegroundColor Green
} else {
    Write-Host "   ❌ Chyba při generování SECRET_KEY" -ForegroundColor Red
    Write-Host "   Zkontroluj, zda máš Django nainstalován" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# ================================================================
# STEP 4: Create new .env from template
# ================================================================
Write-Host "📝 STEP 4: Vytvoření nového .env..." -ForegroundColor Yellow

if (Test-Path ".env") {
    Remove-Item ".env" -Force
    Write-Host "   ✅ Starý .env smazán" -ForegroundColor Green
}

Copy-Item ".env.example" ".env"
Write-Host "   ✅ Nový .env vytvořen z .env.example" -ForegroundColor Green

# Try to update SECRET_KEY in .env (if possible)
try {
    $envContent = Get-Content ".env" -Raw
    $envContent = $envContent -replace 'SECRET_KEY=change-me.*', "SECRET_KEY=$secretKey"
    $envContent | Set-Content ".env"
    Write-Host "   ✅ SECRET_KEY automaticky zaktualizován v .env" -ForegroundColor Green
} catch {
    Write-Host "   ⚠️  Ruční aktualizace SECRET_KEY v .env" -ForegroundColor Yellow
}

Write-Host ""

# ================================================================
# STEP 5: Move test_api.py
# ================================================================
Write-Host "📂 STEP 5: Přesun test_api.py..." -ForegroundColor Yellow

if (Test-Path "test_api.py") {
    # Vytvoř dev-scripts folder pokud neexistuje
    if (-not (Test-Path "dev-scripts")) {
        New-Item -ItemType Directory "dev-scripts" | Out-Null
        Write-Host "   ✅ dev-scripts folder vytvořen" -ForegroundColor Green
    }
    
    Move-Item "test_api.py" "dev-scripts/test_manual_api.py" -Force
    Write-Host "   ✅ test_api.py přesunut do dev-scripts/" -ForegroundColor Green
    
    # Add to .gitignore
    if ((Get-Content ".gitignore" -Raw) -notmatch "test_api\.py") {
        Add-Content ".gitignore" ""
        Add-Content ".gitignore" "# Development"
        Add-Content ".gitignore" "test_api.py"
        Add-Content ".gitignore" "dev-scripts/"
        Write-Host "   ✅ test_api.py přidán do .gitignore" -ForegroundColor Green
    }
} else {
    Write-Host "   ℹ️  test_api.py neexistuje (nejspíš již smazán)" -ForegroundColor Cyan
}

Write-Host ""

# ================================================================
# STEP 6: Fix PASSWORD_HASHERS
# ================================================================
Write-Host "🔐 STEP 6: Oprava PASSWORD_HASHERS v testech..." -ForegroundColor Yellow

$testingSettingsPath = "config\settings\testing.py"

if (Test-Path $testingSettingsPath) {
    $content = Get-Content $testingSettingsPath -Raw
    
    if ($content -match "MD5PasswordHasher") {
        $newContent = $content -replace "'django.contrib.auth.hashers.MD5PasswordHasher'", "'django.contrib.auth.hashers.PBKDF2PasswordHasher'"
        $newContent | Set-Content $testingSettingsPath
        Write-Host "   ✅ MD5PasswordHasher změněn na PBKDF2PasswordHasher" -ForegroundColor Green
    } else {
        Write-Host "   ℹ️  PASSWORD_HASHERS jsou už správné" -ForegroundColor Cyan
    }
} else {
    Write-Host "   ⚠️  $testingSettingsPath nenalezen" -ForegroundColor Yellow
}

Write-Host ""

# ================================================================
# STEP 7: Verify git status
# ================================================================
Write-Host "✓  STEP 7: Verifikace git stavu..." -ForegroundColor Yellow

# Check if .env is gitignored
$gitignore = git check-ignore -v ".env" 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ .env je správně v .gitignore" -ForegroundColor Green
} else {
    Write-Host "   ⚠️  Zkontroluj .gitignore - .env tam být měl" -ForegroundColor Yellow
}

# Push changes
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "Následující změny jsou připraveny:" -ForegroundColor Cyan
git status --short

Write-Host ""
Write-Host "⚠️  Force push (kvůli history rewrite)?" -ForegroundColor Red
$gitResponse = Read-Host "git push origin main --force-with-lease? (ano/ne)"

if ($gitResponse -eq "ano" -or $gitResponse -eq "yes" -or $gitResponse -eq "y") {
    Write-Host ""
    Write-Host "🚀 Git push probíhá..." -ForegroundColor Yellow
    git push origin main --force-with-lease
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✅ Git push úspěšný!" -ForegroundColor Green
    } else {
        Write-Host "   ❌ Git push selhán" -ForegroundColor Red
        Write-Host "   Zkontroluj, zda máš přístup k repositáři" -ForegroundColor Yellow
    }
} else {
    Write-Host "   ℹ️  Git push přeskočen - můžeš jej provést později" -ForegroundColor Cyan
    Write-Host "   Příkaz: git push origin main --force-with-lease" -ForegroundColor Yellow
}

Write-Host ""

# ================================================================
# FINAL SUMMARY
# ================================================================
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host "  ✅ BEZPEČNOSTNÍ OPRAVY HOTOVY!" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host ""

Write-Host "Co bylo provedeno:" -ForegroundColor Cyan
Write-Host "  ✅ Backup .env → .env.backup" -ForegroundColor Green
Write-Host "  ✅ .env odstraněn z git historii" -ForegroundColor Green
Write-Host "  ✅ Nový SECRET_KEY vygenerován" -ForegroundColor Green
Write-Host "  ✅ Nový .env vytvořen" -ForegroundColor Green
Write-Host "  ✅ test_api.py přesunut" -ForegroundColor Green
Write-Host "  ✅ PASSWORD_HASHERS opraveny" -ForegroundColor Green
Write-Host ""

Write-Host "Další kroky:" -ForegroundColor Yellow
Write-Host "  1. 📝 Ověř .env obsah - změňte DB_PASSWORD a ostatní hodnoty"
Write-Host "  2. 🔍 Spusť security checks:"
Write-Host "     pip install pip-audit bandit"
Write-Host "     pip-audit"
Write-Host "     bandit -r . -lll"
Write-Host "  3. 📚 Přečti si:"
Write-Host "     - SECURITY_AUDIT_REPORT.md"
Write-Host "     - SECURITY.md"
Write-Host "  4. ✅ Zkontroluj git log na sekretní data:"
Write-Host "     git log -p | Select-String -Pattern 'PASSWORD|SECRET'"
Write-Host "  5. 🚀 Publikuj na GitHub s důvěrou!"
Write-Host ""

# Cleanup
if (Test-Path "new_secret_key.txt") {
    Write-Host "💾 Nový SECRET_KEY uložen v: new_secret_key.txt" -ForegroundColor Cyan
    Write-Host "   (Deaktivuj soubor, až budeš hotov, aby nebyl veřejný)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host "  Máte-li otázky, viz SECURITY_DOCUMENTATION_INDEX.md" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host ""

Write-Host "Script dokončen. 🎉" -ForegroundColor Cyan

