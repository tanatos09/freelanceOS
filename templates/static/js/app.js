/**
 * Application Utilities
 * Modal management, alerts, navigation, and common UI helpers
 */

class UIManager {
  /**
   * Show alert message
   */
  static alert(message, type = 'error') {
    const alertEl = document.createElement('div');
    alertEl.className = `alert alert-${type} show`;
    alertEl.textContent = message;
    alertEl.style.position = 'fixed';
    alertEl.style.top = '80px';
    alertEl.style.right = '20px';
    alertEl.style.maxWidth = '400px';
    alertEl.style.zIndex = '2000';
    document.body.appendChild(alertEl);

    setTimeout(() => {
      alertEl.remove();
    }, 4000);
  }

  /**
   * Show error toast
   */
  static error(message) {
    this.alert(message, 'error');
  }

  /**
   * Show success toast
   */
  static success(message) {
    this.alert(message, 'success');
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
      const user = await api.get('/auth/me/');
      localStorage.setItem('user', JSON.stringify(user));
      return user;
    } catch (err) {
      console.error('Failed to load user:', err);
      // Only logout if we're not on a public page
      const publicPages = ['/accounts/login/', '/accounts/register/'];
      const isPublicPage = publicPages.some(page => window.location.pathname === page);
      if (!isPublicPage) {
        api.logout();
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
      el.remove();
    });
  }

  /**
   * Show field errors
   */
  static showErrors(formEl, errors) {
    // Clear existing errors
    formEl.querySelectorAll('.form-error').forEach(el => {
      el.remove();
    });

    // Show new errors
    Object.entries(errors).forEach(([field, messages]) => {
      const input = formEl.elements[field];
      if (input) {
        const msg = Array.isArray(messages) ? messages[0] : messages;
        const error = document.createElement('div');
        error.className = 'form-error';
        error.textContent = msg;
        input.parentNode.appendChild(error);
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
        btn.textContent = '…';
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
      api.logout();
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
