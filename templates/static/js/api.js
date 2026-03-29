/**
 * API Client with JWT Authentication
 * Handles all HTTP requests to the backend API
 */

class APIClient {
  constructor() {
    this.baseURL = '/api/v1';
    this.accessToken = localStorage.getItem('access_token');
    this.refreshToken = localStorage.getItem('refresh_token');
    // Singleton Promise: ensures concurrent 401s share one refresh call
    this._refreshPromise = null;

    // API sub-objects defined in constructor (not class fields) to guarantee
    // 'this' is fully bound before any arrow function references it.
    this.clients = {
      list: (search = '') => {
        const params = search ? `?search=${encodeURIComponent(search)}` : '';
        return this.get(`/clients/${params}`);
      },
      get: (id) => this.get(`/clients/${id}/`),
      create: (data) => this.post('/clients/', data),
      update: (id, data) => this.put(`/clients/${id}/`, data),
      delete: (id) => this.delete(`/clients/${id}/`),
      stats: (id) => this.get(`/clients/${id}/stats/`),
      projects: (id) => this.get(`/clients/${id}/projects/`),
    };

    this.projects = {
      list: (filters = {}) => {
        const params = new URLSearchParams(filters).toString();
        return this.get(`/projects/${params ? '?' + params : ''}`);
      },
      get: (id) => this.get(`/projects/${id}/`),
      create: (data) => this.post('/projects/', data),
      update: (id, data) => this.put(`/projects/${id}/`, data),
      delete: (id) => this.delete(`/projects/${id}/`),
    };

    this.workcommits = {
      list: (filters = {}) => {
        const params = new URLSearchParams(filters).toString();
        return this.get(`/workcommits/${params ? '?' + params : ''}`);
      },
      running: () => this.get('/workcommits/running/'),
      start: (projectId) => this.post('/workcommits/start/', { project: projectId }),
      commit: (id, description, continueTimer, tag = null) =>
        this.post(`/workcommits/${id}/commit/`, { description, continue: continueTimer, tag }),
      stop: (id, description = '', tag = null) =>
        this.post(`/workcommits/${id}/stop/`, { description, tag }),
      pause: (id) => this.post(`/workcommits/${id}/pause/`, {}),
      resume: (id) => this.post(`/workcommits/${id}/resume/`, {}),
      delete: (id) => this.delete(`/workcommits/${id}/`),
      patch: (id, data) => this.patch(`/workcommits/${id}/`, data),
    };

    this.dashboard = {
      stats: (range) => this.get('/dashboard/stats/' + (range ? '?range=' + range : '')),
    };
  }

  /**
   * Get authorization headers
   */
  getHeaders() {
    const headers = {
      'Content-Type': 'application/json',
    };
    if (this.accessToken) {
      headers['Authorization'] = `Bearer ${this.accessToken}`;
    }
    return headers;
  }

  /**
   * Refresh access token if needed.
   * Uses a singleton Promise so concurrent 401s always share one refresh call
   * instead of each racing to invalidate the refresh token.
   */
  async refreshAccessToken() {
    if (this._refreshPromise) return this._refreshPromise;

    this._refreshPromise = (async () => {
      if (!this.refreshToken) {
        this.logout();
        return false;
      }
      try {
        const res = await fetch(`${this.baseURL}/auth/token/refresh/`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ refresh: this.refreshToken }),
        });
        if (res.ok) {
          const data = await res.json();
          this.accessToken = data.access;
          this.refreshToken = data.refresh || this.refreshToken;
          localStorage.setItem('access_token', this.accessToken);
          localStorage.setItem('refresh_token', this.refreshToken);
          return true;
        }
        this.logout();
        return false;
      } catch (err) {
        console.error('Token refresh failed:', err);
        this.logout();
        return false;
      } finally {
        this._refreshPromise = null;
      }
    })();

    return this._refreshPromise;
  }

  /**
   * Make HTTP request
   */
  async request(endpoint, options = {}) {
    const method = options.method || 'GET';
    const url = `${this.baseURL}${endpoint}`;
    const headers = this.getHeaders();

    let response;
    try {
      response = await fetch(url, {
        method,
        headers,
        ...(options.body && { body: JSON.stringify(options.body) }),
      });
    } catch (err) {
      console.error('Network error:', err);
      throw new Error('Síťová chyba. Zkontrolujte připojení.');
    }

    // Handle 401 Unauthorized - try refresh token (at most once per call chain)
    if (response.status === 401 && !options._retried) {
      const refreshed = await this.refreshAccessToken();
      if (!refreshed) {
        throw new Error('Vaše relace vypršela. Prosím přihlašte se znovu.');
      }
      // Retry original request with new token; _retried prevents infinite loop
      return this.request(endpoint, { ...options, _retried: true });
    }

    if (response.status === 401) {
      throw new Error('Vaše relace vypršela. Prosím přihlašte se znovu.');
    }

    // Parse response
    let data;
    try {
      const contentType = response.headers.get('content-type');
      data = contentType && contentType.includes('application/json')
        ? await response.json()
        : null;
    } catch (err) {
      data = null;
    }

    if (!response.ok) {
      const errorMsg = data?.detail || data?.error || `Chyba: ${response.status}`;
      const error = new Error(errorMsg);
      error.status = response.status;
      error.data = data;
      throw error;
    }

    return data;
  }

  /**
   * GET request
   */
  get(endpoint) {
    return this.request(endpoint, { method: 'GET' });
  }

  /**
   * POST request
   */
  post(endpoint, body) {
    return this.request(endpoint, { method: 'POST', body });
  }

  /**
   * PUT request
   */
  put(endpoint, body) {
    return this.request(endpoint, { method: 'PUT', body });
  }

  patch(endpoint, body) {
    return this.request(endpoint, { method: 'PATCH', body });
  }

  /**
   * DELETE request
   */
  delete(endpoint) {
    return this.request(endpoint, { method: 'DELETE' });
  }

  /**
   * Logout user
   */
  logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
    window.location.href = '/accounts/login/';
  }

}

// Create global API client instance
try {
  window.api = new APIClient();
} catch (err) {
  console.error('Failed to create API client:', err);
  window.api = null;
}
