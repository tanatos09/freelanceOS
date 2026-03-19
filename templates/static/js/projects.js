/**
 * Projects Page Logic
 */

class ProjectsManager {
  constructor() {
    this.projects = [];
    this.clients = [];
    this.editingId = null;
    this.filters = {
      search: '',
      status: '',
      client_id: '',
    };
    this.statusLabels = {
      draft: 'Návrh',
      active: 'Aktivní',
      completed: 'Hotovo',
      archived: 'Archivováno',
      cancelled: 'Zrušeno',
    };
    this.init();
  }

  init() {
    this.attachEventListeners();
    this.loadClients();
    this.loadProjects();
  }

  attachEventListeners() {
    // Add project buttons
    document.getElementById('addProjectBtn')?.addEventListener('click', () => {
      this.openAddModal();
    });
    document.getElementById('addProjectEmptyBtn')?.addEventListener('click', () => {
      this.openAddModal();
    });

    // Form submission
    document.getElementById('projectForm').addEventListener('submit', (e) => {
      e.preventDefault();
      this.handleFormSubmit();
    });

    // Search and filters
    document.getElementById('searchInput')?.addEventListener(
      'input',
      UIManager.debounce((e) => {
        this.filters.search = e.target.value;
        this.applyFilters();
      }, 300)
    );

    document.getElementById('statusFilter')?.addEventListener('change', (e) => {
      this.filters.status = e.target.value;
      this.applyFilters();
    });

    document.getElementById('clientFilter')?.addEventListener('change', (e) => {
      this.filters.client_id = e.target.value;
      this.applyFilters();
    });
  }

  async loadClients() {
    try {
      this.clients = await window.api.clients.list();
      
      // Populate client dropdowns
      const clientSelect = document.getElementById('projectClient');
      clientSelect.innerHTML = '<option value="">-- Vyberte klienta --</option>' +
        this.clients.map(c => `<option value="${c.id}">${this.escapeHtml(c.name)}</option>`).join('');

      const clientFilter = document.getElementById('clientFilter');
      clientFilter.innerHTML = '<option value="">Všichni klienti</option>' +
        this.clients.map(c => `<option value="${c.id}">${this.escapeHtml(c.name)}</option>`).join('');
    } catch (err) {
      console.error('Failed to load clients:', err);
    }
  }

  showSkeleton() {
    const tbody = document.getElementById('projectsTbody');
    if (!tbody) return;
    const tableWrap = tbody.closest('.table-wrap');
    if (tableWrap) tableWrap.style.display = '';
    const emptyState = document.getElementById('emptyState');
    if (emptyState) emptyState.style.display = 'none';
    const rows = Array.from({ length: 3 }, () =>
      `<tr class="skeleton-row">
        <td><span class="row-skeleton" style="width:150px"></span></td>
        <td><span class="row-skeleton" style="width:110px"></span></td>
        <td><span class="row-skeleton" style="width:70px"></span></td>
        <td><span class="row-skeleton" style="width:90px"></span></td>
        <td><span class="row-skeleton" style="width:80px"></span></td>
        <td></td>
      </tr>`
    ).join('');
    tbody.innerHTML = rows;
  }

  async loadProjects() {
    this.showSkeleton();
    try {
      this.projects = await window.api.projects.list();
      this.renderTable();
    } catch (err) {
      console.error('Failed to load projects:', err);
      UIManager.error(err.message || 'Chyba při načítání projektů');
      const tbody = document.getElementById('projectsTbody');
      if (tbody) tbody.innerHTML =
        '<tr><td colspan="6" style="text-align: center; color: var(--danger);">Chyba při načítání</td></tr>';
    }
  }

  applyFilters() {
    this.renderTable();
  }

  getFilteredProjects() {
    return this.projects.filter(project => {
      // Search filter
      if (this.filters.search) {
        const search = this.filters.search.toLowerCase();
        if (!project.name.toLowerCase().includes(search)) {
          return false;
        }
      }

      // Status filter
      if (this.filters.status && project.status !== this.filters.status) {
        return false;
      }

      // Client filter
      if (this.filters.client_id && project.client !== parseInt(this.filters.client_id)) {
        return false;
      }

      return true;
    });
  }

  renderTable() {
    const tbody = document.getElementById('projectsTbody');
    const emptyState = document.getElementById('emptyState');
    const tableWrap = tbody ? tbody.closest('.table-wrap') : null;

    const filtered = this.getFilteredProjects();

    if (filtered.length === 0) {
      if (tableWrap) tableWrap.style.display = 'none';
      if (emptyState) emptyState.style.display = 'block';
      return;
    }

    if (tableWrap) tableWrap.style.display = '';
    if (emptyState) emptyState.style.display = 'none';

    tbody.innerHTML = filtered.map(project => {
      const client = this.clients.find(c => c.id === project.client);
      const deadline = new Date(project.end_date);
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      const isOverdue = project.end_date && deadline < today && project.status !== 'completed' && project.status !== 'cancelled' && project.status !== 'archived';

      return `
        <tr${isOverdue ? ' class="tr-overdue tr-clickable"' : ' class="tr-clickable"'} onclick="window.location.href='/accounts/projects/${project.id}/'">
          <td>
            <span class="project-name">${this.escapeHtml(project.name)}</span>
            ${isOverdue ? '<div class="project-overdue">Po termínu</div>' : ''}
          </td>
          <td class="td-muted">${client ? this.escapeHtml(client.name) : 'N/A'}</td>
          <td>${UIManager.statusBadge(project.status)}</td>
          <td class="td-muted">
            ${UIManager.formatDate(project.end_date)}
            ${project.days_until_deadline != null ? `<div class="td-days">${project.days_until_deadline} dní</div>` : ''}
          </td>
          <td>${UIManager.formatCurrency(project.budget)}</td>
          <td>
            ${project.estimated_hours > 0 ? `
              <span style="font-size:.8rem;color:var(--text-muted)">${Math.round(project.progress || 0)}&thinsp;%</span>
              <div class="progress-bar-wrap">
                <div class="progress-bar-fill${(project.progress || 0) >= 100 ? ' over' : (project.progress || 0) >= 80 ? ' warn' : ''}"
                     style="width:${Math.min(100, Math.round(project.progress || 0))}%"></div>
              </div>
            ` : '<span style="color:var(--text-muted)">—</span>'}
          </td>
          <td class="td-muted">${project.earnings != null && project.earnings > 0 ? UIManager.formatCurrency(project.earnings) : '<span style="color:var(--text-muted)">—</span>'}</td>
          <td>
            <div class="td-actions" onclick="event.stopPropagation()">
              <button class="btn btn-outline btn-sm" onclick="projectsManager.openEditModal(${project.id})">Upravit</button>
              <button class="btn btn-danger-soft btn-sm" onclick="projectsManager.confirmDelete(${project.id})">Smazat</button>
            </div>
          </td>
        </tr>
      `;
    }).join('');
  }

  openAddModal() {
    this.editingId = null;
    document.getElementById('modalTitle').textContent = 'Nový projekt';
    FormHelper.clear(document.getElementById('projectForm'));
    document.getElementById('projectStatus').value = 'active';
    UIManager.modal.open('projectModal');
  }

  async openEditModal(projectId) {
    this.editingId = projectId;
    document.getElementById('modalTitle').textContent = 'Upravit projekt';
    FormHelper.clear(document.getElementById('projectForm'));
    UIManager.modal.open('projectModal');

    try {
      const project = await window.api.projects.get(projectId);
      FormHelper.populate(document.getElementById('projectForm'), {
        name: project.name,
        client: project.client,
        description: project.description || '',
        status: project.status,
        budget: project.budget,
        estimated_hours: project.estimated_hours,
        hourly_rate: project.hourly_rate || 0,
        start_date: project.start_date || '',
        end_date: project.end_date || '',
      });
    } catch (err) {
      UIManager.error('Chyba při načítání projektu');
      UIManager.modal.close('projectModal');
    }
  }

  async handleFormSubmit() {
    const form = document.getElementById('projectForm');
    const data = FormHelper.getData(form);

    // Convert string values to proper types
    data.budget = data.budget ? parseFloat(data.budget) : 0;
    data.estimated_hours = data.estimated_hours ? parseFloat(data.estimated_hours) : 0;
    data.hourly_rate = data.hourly_rate ? parseFloat(data.hourly_rate) : 0;
    data.client = parseInt(data.client);

    // DRF DateField rejects empty strings – send null instead
    // Ensure dates are always in YYYY-MM-DD format for DRF
    data.start_date = data.start_date ? data.start_date.substring(0, 10) : null;
    data.end_date = data.end_date ? data.end_date.substring(0, 10) : null;

    // Frontend date validation
    if (data.start_date && data.end_date && data.start_date > data.end_date) {
      UIManager.error('Datum začátku musí být před deadline.');
      const endDateInput = form.elements['end_date'];
      if (endDateInput) {
        const errEl = document.createElement('div');
        errEl.className = 'form-error';
        errEl.textContent = 'Deadline musí být po datu začátku.';
        form.querySelectorAll('.form-error').forEach(e => e.remove());
        endDateInput.parentNode.appendChild(errEl);
      }
      return;
    }

    try {
      FormHelper.setLoading(form, true);

      if (this.editingId) {
        // Update
        await window.api.projects.update(this.editingId, data);
        UIManager.success('Projekt upraven');
      } else {
        // Create
        await window.api.projects.create(data);
        UIManager.success('Projekt vytvořen');
      }

      UIManager.modal.close('projectModal');
      await this.loadProjects();
    } catch (err) {
      console.error('Save error:', err);
      if (err.data && typeof err.data === 'object') {
        FormHelper.showErrors(form, err.data);
      } else {
        UIManager.error(err.message || 'Chyba při ukládání');
      }
    } finally {
      FormHelper.setLoading(form, false);
    }
  }

  async confirmDelete(projectId) {
    const project = this.projects.find(p => p.id === projectId);
    if (!project) return;

    if (!confirm(`Opravdu chcete smazat projekt "${project.name}"?`)) {
      return;
    }

    try {
      await window.api.projects.delete(projectId);
      UIManager.success('Projekt smazán');
      await this.loadProjects();
    } catch (err) {
      console.error('Delete error:', err);
      UIManager.error(err.message || 'Chyba při mazání');
    }
  }

  escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }
}

// Initialize projects manager when DOM is ready
let projectsManager;
document.addEventListener('DOMContentLoaded', () => {
  if (document.getElementById('addProjectBtn') || document.getElementById('projectsTbody')) {
    projectsManager = new ProjectsManager();
  }
});
