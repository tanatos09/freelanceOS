# 🔐 Security Policy

**Project:** freelanceOS  
**Last Updated:** 2026-03-08  
**Status:** ✅ Ready for public release

---

## Overview

freelanceOS is a Django REST Framework application with built-in security features for multi-workspace collaboration. This document outlines our security practices and how to securely deploy and use this application.

---

## Environment Setup

### Local Development

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/freelanceos.git
   cd freelanceos
   ```

2. **Create `.env` file from template:**
   ```bash
   cp .env.example .env
   ```

3. **Set environment variables:**
   - Edit `.env` with your local configuration
   - **IMPORTANT:** Never commit `.env` file
   - Generate a new `SECRET_KEY`:
     ```bash
     python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
     ```

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Run migrations:**
   ```bash
   python manage.py migrate
   ```

6. **Run development server:**
   ```bash
   python manage.py runserver
   ```

### Production Deployment

#### ⚠️ CRITICAL Security Requirements:

- [ ] **NEW SECRET_KEY** - Generate using `get_random_secret_key()`
- [ ] **NEW Database Password** - Change from default
- [ ] **HTTPS Only** - Use SECURE_SSL_REDIRECT=True
- [ ] **ALLOWED_HOSTS** - Set to your domain(s) only
- [ ] **CORS_ALLOWED_ORIGINS** - Whitelist specific frontend domains
- [ ] **DEBUG=False** - Never enable debugging in production
- [ ] **Secure Environment** - Use hosting provider's secret management

#### Environment Variables Template:

```ini
# .env (DO NOT COMMIT - SET VIA HOSTING PROVIDER)

# Django
SECRET_KEY=<generate-new-secure-key>
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database
DB_ENGINE=django.db.backends.postgresql
DB_NAME=freelanceos_prod
DB_USER=freelanceos_admin
DB_PASSWORD=<use-strong-password>
DB_HOST=your-db-host.com
DB_PORT=5432

# Frontend
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# SSL/Security
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

#### Deployment Methods:

**Heroku:**
```bash
heroku config:set SECRET_KEY=<your-new-secret-key>
heroku config:set DEBUG=False
heroku config:set ALLOWED_HOSTS=yourdomain.com
# ... set other env vars
```

**Docker:**
```bash
docker run -e SECRET_KEY=<key> -e DB_PASSWORD=<pass> ...
```

**Self-hosted (systemd):**
```ini
# /etc/systemd/system/freelanceos.service
[Service]
Environment="SECRET_KEY=<key>"
Environment="DEBUG=False"
Environment="DB_PASSWORD=<pass>"
```

---

## Security Features

### Authentication & Authorization

- **JWT Tokens** with 60-minute lifetime
- **Refresh Tokens** with 7-day lifetime
- **Token Rotation** - Automatic refresh token rotation
- **Token Blacklisting** - Revoked tokens cannot be used
- **User-specific Data** - Users can only access their own data

### Permission System

```python
# All API endpoints require authentication
@permission_classes([IsAuthenticated])
def view_function(request):
    # User can only access their own data
    user_data = UserService.get_user_data(request.user)
```

### Password Security

- **4 Password Validators** enabled:
  - User attribute similarity validator
  - Minimum length validator (8 characters)
  - Common password validator
  - Numeric password validator
- **PBKDF2 Password Hashing** with 260,000 iterations

### CSRF Protection

- **CSRF Middleware** enabled for all POST/PUT/DELETE requests
- **CSRF Token** required in request headers
- **Secure Cookies** in production (HTTPS-only)

### Data Access Control

```python
# Example: Services filter by user
class ClientService:
    @staticmethod
    def get_user_clients(user):
        return Client.objects.filter(user=user)

    @staticmethod
    def get_client_detail(user, client_id):
        return Client.objects.filter(user=user, id=client_id).first()
```

### Rate Limiting

- **Anonymous Users:** 100 requests/hour
- **Authenticated Users:** 1,000 requests/hour

### API Security Headers

```
Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
```

---

## Known Security Limitations

### Scope

This is a **freelance management MVP** - not intended for:
- Financial transactions (use Stripe, PayPal integrations)
- Storing sensitive payment information
- High-security industries (healthcare, banking, etc.)

### Recommendations for Production

1. **Add Rate Limiting**
   - Use django-ratelimit or DRF throttling (already included)

2. **Add IP Whitelisting** (if applicable)
   - For admin panel or sensitive endpoints

3. **Add 2FA/MFA** (recommended)
   - Consider django-otp or similar

4. **Add API Key Management**
   - For third-party integrations

5. **Implement Audit Logging**
   - Log sensitive operations (user deletions, permission changes)

6. **Use HTTPS Everywhere**
   - Enforce in production

7. **Regular Security Updates**
   - Keep Django and dependencies updated
   - Run `pip-audit` regularly

8. **Security Headers**
   - CSP, etc. (partially implemented)

---

## Reporting Security Vulnerabilities

⚠️ **DO NOT open public issues for security vulnerabilities**

**Email:** [your-security-email@example.com]  
**GPG Key:** [optional link to GPG key]

Include:
- Description of vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (optional)

We will:
1. Acknowledge receipt within 48 hours
2. Investigate and assess severity
3. Work on fix (timeline depends on severity)
4. Send patch to you for validation
5. Release security update
6. Credit your discovery (if desired)

---

## Security Checklist for Contributors

If you're contributing code, please ensure:

- [ ] **No hardcoded secrets** (API keys, passwords, tokens)
- [ ] **No print() debugging** left in production code
- [ ] **No test credentials** in fixtures
- [ ] **Environment variables** for all sensitive config
- [ ] **Authenticate sensitive endpoints** with @permission_classes
- [ ] **Filter data by user** in queries (don't expose others' data)
- [ ] **Validate input** on all API endpoints
- [ ] **Use HTTPS** for external API calls
- [ ] **No direct SQL queries** (use ORM)
- [ ] **Update dependencies** regularly
- [ ] **Run bandit** for security linting:
  ```bash
  pip install bandit
  bandit -r . -lll
  ```

---

## Dependency Security

### Vulnerable Dependencies

Check for vulnerabilities:
```bash
pip install pip-audit
pip-audit
```

### Regular Updates

```bash
# Check for outdated packages
pip list --outdated

# Update a package
pip install --upgrade django

# Update all
pip install -U -r requirements.txt
```

### Current Dependencies

- **Django 4.2** - LTS version, security patches until April 2026
- **djangorestframework 3.14** - Latest stable version
- **djangorestframework-simplejwt** - JWT authentication
- **python-decouple** - Environment variable management
- **psycopg2** - PostgreSQL driver
- **django-cors-headers** - CORS handling

---

## Testing Security

### Run Security Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=. tests/

# Run security-focused tests
pytest tests/ -k "security\|auth\|permission"
```

### Test Coverage Targets

- **Authentication:** 95%+ coverage
- **Permissions:** 95%+ coverage
- **Validators:** 90%+ coverage
- **Models:** 90%+ coverage

---

## Compliance

### Data Protection

This application does NOT:
- Collect personal data beyond user registration (email, name, password)
- Share data with third parties
- Use cookies for tracking
- Process payments

If you add payment processing:
- **PCI DSS** compliance required
- **GDPR** compliance required (if EU users)
- **CCPA** compliance required (if California users)

### HTTPS/TLS

- Enforced in production
- Recommended: TLS 1.2+
- Certificate: Let's Encrypt or similar

---

## Incident Response

### If You Discover a Vulnerability

1. **DO NOT** publicly disclose
2. **DO** email security team immediately
3. **Provide:** Description, reproduction steps, impact
4. **Wait:** For our response (max 48 hours)
5. **Work with us** on patch development

### If You Experience a Breach

1. **Immediately** rotate all secrets
2. **Notify** affected users
3. **Change** database passwords
4. **Review** access logs
5. **Update** security measures
6. **Document** lessons learned

---

## Securing Your Instance

### Basic Hardening

```bash
# 1. Keep system updated
apt-get update && apt-get upgrade  # Linux

# 2. Use strong database password
# (Change from default!)

# 3. Enable firewall
sudo ufw enable
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS

# 4. Use fail2ban for login attempts
sudo apt-get install fail2ban

# 5. Regular backups
# - Database backups (encrypted)
# - File backups
# - Off-server storage
```

### Monitoring

- Monitor error logs for suspicious patterns
- Alert on failed login attempts
- Monitor database for unusual queries
- Check for disk space issues
- Monitor memory usage

---

## Changes & Updates

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-03-08 | Initial security policy |

---

## References

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Django Security Documentation](https://docs.djangoproject.com/en/4.2/topics/security/)
- [DRF Security](https://www.django-rest-framework.org/api-guide/authentication/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)

---

## Questions?

For security-related questions:
- **Security Issues:** [security@example.com]
- **General Questions:** [support@example.com]
- **GitHub Discussions:** [Link to discussions]

---

**This security policy is reviewed and updated regularly. Last review: 2026-03-08**

---

⚠️ **Remember:** Security is everyone's responsibility. Thank you for helping keep freelanceOS secure! 🔒
