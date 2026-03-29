/**
 * Application Utilities
 * Modal management, alerts, navigation, and common UI helpers
 */

class UIManager {
  // ── Toast notification system ────────────────────────────────────────────

  static _getToastContainer() {
    let container = document.getElementById('toastContainer');
    if (!container) {
      container = document.createElement('div');
      container.id = 'toastContainer';
      container.className = 'toast-container';
      document.body.appendChild(container);
    }
    return container;
  }

  /**
   * Show a toast notification.
   * @param {string} message
   * @param {'error'|'success'|'info'|'warning'} type
   * @param {number} [duration] ms before auto-dismiss (0 = no auto-dismiss)
   */
  static alert(message, type = 'error', duration) {
    const ms = duration ?? (type === 'error' ? 5000 : 3500);

    const icons = {
      error:   '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" aria-hidden="true"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>',
      success: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" aria-hidden="true"><polyline points="20 6 9 17 4 12"/></svg>',
      info:    '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" aria-hidden="true"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>',
      warning: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" aria-hidden="true"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>',
    };

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.setAttribute('role', type === 'error' ? 'alert' : 'status');
    toast.innerHTML = `
      <span class="toast-icon">${icons[type] || icons.info}</span>
      <span class="toast-message">${this._escapeHtml(message)}</span>
      <button class="toast-close" aria-label="Zavřít">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" aria-hidden="true"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
      </button>
      ${ms > 0 ? '<div class="toast-progress"><div class="toast-progress-bar"></div></div>' : ''}
    `;

    const dismiss = () => {
      toast.classList.add('toast-hiding');
      toast.addEventListener('animationend', () => toast.remove(), { once: true });
    };

    toast.querySelector('.toast-close').addEventListener('click', dismiss);

    this._getToastContainer().appendChild(toast);

    // Trigger enter animation on next frame
    requestAnimationFrame(() => toast.classList.add('toast-visible'));

    if (ms > 0) {
      const bar = toast.querySelector('.toast-progress-bar');
      if (bar) bar.style.animationDuration = `${ms}ms`;
      setTimeout(dismiss, ms);
    }
  }

  static error(message)   { this.alert(message, 'error'); }
  static success(message) { this.alert(message, 'success'); }
  static info(message)    { this.alert(message, 'info'); }
  static warning(message) { this.alert(message, 'warning'); }

  static _escapeHtml(text) {
    const d = document.createElement('div');
    d.textContent = text;
    return d.innerHTML;
  }

  /**
   * Modal management
   */
  static modal = {
    open(id) {
      const modal = document.getElementById(id);
      if (modal) {
        modal.classList.add('show');
        document.body.style.overflow = 'hidden';
      }
    },
    close(id) {
      const modal = document.getElementById(id);
      if (modal) {
        modal.classList.remove('show');
        document.body.style.overflow = '';
      }
    },
    closeAll() {
      document.querySelectorAll('.modal.show').forEach(m => {
        m.classList.remove('show');
      });
      document.body.style.overflow = '';
    },
  };

  /**
   * Format date to local string
   */
  static formatDate(dateString) {
    if (!dateString) return '—';
    const date = new Date(dateString);
    return date.toLocaleDateString('cs-CZ', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  }

  /**
   * Format currency
   */
  static formatCurrency(value) {
    if (!value) return '0 Kč';
    return new Intl.NumberFormat('cs-CZ', {
      style: 'currency',
      currency: 'CZK',
    }).format(value);
  }

  /**
   * Get status badge HTML
   */
  static statusBadge(status) {
    const labels = {
      draft: 'Návrh',
      active: 'Aktivní',
      paused: 'Pozastaveno',
      pending_payment: 'Čeká na platbu',
      completed: 'Hotovo',
      archived: 'Archivováno',
      cancelled: 'Zrušeno',
    };
    return `<span class="badge badge-${status}">${labels[status] || status}</span>`;
  }

  /**
   * Check if authenticated
   */
  static isAuthenticated() {
    return !!localStorage.getItem('access_token');
  }

  /**
   * Setup page authentication check
   */
  static requireAuth() {
    if (!this.isAuthenticated()) {
      window.location.href = '/accounts/login/';
    }
  }

  /**
   * Load current user
   */
  static async loadUser() {
    try {
      const user = await window.api.get('/auth/me/');
      localStorage.setItem('user', JSON.stringify(user));
      return user;
    } catch (err) {
      console.error('Failed to load user:', err);
      // Only logout if we're not on a public page
      const publicPages = ['/accounts/login/', '/accounts/register/'];
      const isPublicPage = publicPages.some(page => window.location.pathname === page);
      if (!isPublicPage) {
        window.api.logout();
      }
    }
  }

  /**
   * Setup navigation active state
   */
  static setActiveNav(pageName) {
    document.querySelectorAll('.navbar-nav a').forEach(link => {
      link.classList.remove('active');
      if (link.dataset.page === pageName) {
        link.classList.add('active');
      }
    });
  }

  /**
   * Format file input to data URL
   */
  static fileToDataURL(file) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(reader.result);
      reader.onerror = reject;
      reader.readAsDataURL(file);
    });
  }

  /**
   * Debounce function
   */
  static debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  }
}

/**
 * Form helper
 */
class FormHelper {
  /**
   * Get form data as object
   */
  static getData(formEl) {
    const formData = new FormData(formEl);
    const data = {};
    formData.forEach((value, key) => {
      data[key] = value;
    });
    return data;
  }

  /**
   * Populate form with data
   */
  static populate(formEl, data) {
    if (!data) return;
    Object.entries(data).forEach(([key, value]) => {
      const field = formEl.elements[key];
      if (field) {
        if (field.type === 'checkbox') {
          field.checked = !!value;
        } else {
          field.value = value || '';
        }
      }
    });
  }

  /**
   * Clear form
   */
  static clear(formEl) {
    formEl.reset();
    formEl.querySelectorAll('.form-error').forEach(el => {
      el.textContent = '';
    });
    formEl.querySelectorAll('.form-group.error').forEach(el => {
      el.classList.remove('error');
    });
  }

  /**
   * Show field errors from API response.
   * Marks .form-group with .error class so red border + message are visible.
   */
  static showErrors(formEl, errors) {
    // Clear existing errors and error states
    formEl.querySelectorAll('.form-error').forEach(el => { el.textContent = ''; });
    formEl.querySelectorAll('.form-group.error').forEach(el => el.classList.remove('error'));

    // Show new errors
    Object.entries(errors).forEach(([field, messages]) => {
      const msg = Array.isArray(messages) ? messages[0] : messages;
      // Non-field errors and detail shown as toast
      if (field === 'non_field_errors' || field === 'detail') {
        UIManager.error(String(msg));
        return;
      }
      const input = formEl.elements[field];
      if (input) {
        const group = input.closest('.form-group');
        let errorEl = group ? group.querySelector('.form-error') : null;
        if (!errorEl) {
          errorEl = document.createElement('div');
          errorEl.className = 'form-error';
          input.parentNode.appendChild(errorEl);
        }
        errorEl.textContent = msg;
        if (group) group.classList.add('error');
      } else {
        // Field not in form – show as toast fallback
        UIManager.error(`${field}: ${msg}`);
      }
    });
  }

  /**
   * Validate required fields and email format, show inline errors.
   * Returns true if all required fields pass, false otherwise.
   */
  static validate(formEl) {
    formEl.querySelectorAll('.form-error').forEach(el => { el.textContent = ''; });
    formEl.querySelectorAll('.form-group.error').forEach(el => el.classList.remove('error'));

    let valid = true;
    formEl.querySelectorAll('input[required], select[required], textarea[required]').forEach(input => {
      const group = input.closest('.form-group');
      let errorEl = group ? group.querySelector('.form-error') : null;
      if (!errorEl && group) {
        errorEl = document.createElement('div');
        errorEl.className = 'form-error';
        group.appendChild(errorEl);
      }
      const value = input.value.trim();
      let msg = '';
      if (!value) {
        msg = 'Toto pole je povinné.';
      } else if (input.type === 'email' && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
        msg = 'Zadejte platný e-mail.';
      }
      if (msg) {
        if (group) group.classList.add('error');
        if (errorEl) errorEl.textContent = msg;
        valid = false;
      }
    });
    return valid;
  }

  /**
   * Attach per-field blur validation to all inputs in a form.
   * Validates required and email fields on blur; selects also on change.
   */
  static attachBlurValidation(formEl) {
    const validateField = (input) => {
      const group = input.closest('.form-group');
      let errorEl = group ? group.querySelector('.form-error') : null;
      if (!errorEl && group) {
        errorEl = document.createElement('div');
        errorEl.className = 'form-error';
        group.appendChild(errorEl);
      }
      if (!input.required) {
        if (group) group.classList.remove('error');
        if (errorEl) errorEl.textContent = '';
        return;
      }
      const value = input.value.trim();
      let msg = '';
      if (!value) {
        msg = 'Toto pole je povinné.';
      } else if (input.type === 'email' && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
        msg = 'Zadejte platný e-mail.';
      }
      if (msg) {
        if (group) group.classList.add('error');
        if (errorEl) errorEl.textContent = msg;
      } else {
        if (group) group.classList.remove('error');
        if (errorEl) errorEl.textContent = '';
      }
    };

    formEl.querySelectorAll('input, select, textarea').forEach(input => {
      if (input._blurValidationAttached) return;
      input._blurValidationAttached = true;
      input.addEventListener('blur', () => validateField(input));
      if (input.tagName === 'SELECT') {
        input.addEventListener('change', () => validateField(input));
      }
    });
  }

  /**
   * Disable form while processing
   */
  static setLoading(formEl, loading = true) {
    const btn = formEl.querySelector('button[type="submit"]');
    if (btn) {
      btn.disabled = loading;
      if (loading) {
        btn._originalText = btn.innerHTML;
        btn.textContent = '…';
      } else if (btn._originalText) {
        btn.innerHTML = btn._originalText;
        btn._originalText = null;
      }
    }
    const inputs = formEl.querySelectorAll('input, textarea, select');
    inputs.forEach(input => {
      input.disabled = loading;
    });
  }
}

/**
 * Initialize page
 */
document.addEventListener('DOMContentLoaded', async () => {
  // Skip auth check on public pages
  const publicPages = ['/accounts/login/', '/accounts/register/'];
  const isPublicPage = publicPages.some(page => window.location.pathname === page);
  
  if (!isPublicPage) {
    UIManager.requireAuth();
    // Load and display user info
    const user = await UIManager.loadUser();
    if (user && document.getElementById('userEmail')) {
      document.getElementById('userEmail').textContent = user.email;
    }
  }

  // Setup navbar clicks
  document.querySelectorAll('.navbar-nav a').forEach(link => {
    link.addEventListener('click', (e) => {
      // If link has href, don't prevent default
      // This allows normal navigation
    });
  });

  // Setup logout button
  const logoutBtn = document.getElementById('logoutBtn');
  if (logoutBtn) {
    logoutBtn.addEventListener('click', (e) => {
      e.preventDefault();
      window.api.logout();
    });
  }

  // Setup modal close buttons
  document.querySelectorAll('[data-modal-close]').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      const modalId = btn.getAttribute('data-modal-close');
      UIManager.modal.close(modalId);
    });
  });

  // Close modal on background click
  document.querySelectorAll('.modal').forEach(modal => {
    modal.addEventListener('click', (e) => {
      if (e.target === modal) {
        UIManager.modal.close(modal.id);
      }
    });
  });
});
