/**
 * Clients Page Logic
 */

class ClientsManager {
  constructor() {
    this.clients = [];
    this.editingId = null;
    this.searchQuery = '';
    this.init();
  }

  init() {
    this.attachEventListeners();
    this.loadClients();
  }

  attachEventListeners() {
    document.getElementById('addClientBtn')?.addEventListener('click', () => {
      this.openAddModal();
    });
    document.getElementById('addClientEmptyBtn')?.addEventListener('click', () => {
      this.openAddModal();
    });

    document.getElementById('clientForm').addEventListener('submit', (e) => {
      e.preventDefault();
      this.handleFormSubmit();
    });

    document.getElementById('searchInput')?.addEventListener(
      'input',
      UIManager.debounce((e) => {
        this.searchQuery = e.target.value;
        this.renderTable();
      }, 300)
    );
  }

  async loadClients() {
    this.showSkeleton();
    try {
      this.clients = await window.api.clients.list(this.searchQuery);
      this.renderTable();
    } catch (err) {
      console.error('Failed to load clients:', err);
      UIManager.error(err.message || 'Chyba při načítání klientů');
      document.getElementById('clientsTbody').innerHTML =
        `<tr><td colspan="6" style="text-align:center;color:var(--danger);padding:2rem">
          Chyba při načítání dat.
         </td></tr>`;
    }
  }

  showSkeleton() {
    const tbody = document.getElementById('clientsTbody');
    if (!tbody) return;
    const tableWrap = tbody.closest('.table-wrap');
    const emptyState = document.getElementById('emptyState');

    const rows = Array.from({ length: 3 }, () => `
      <tr class="skeleton-row">
        <td><span class="row-skeleton" style="width:140px"></span><span class="row-skeleton" style="width:90px;margin-top:4px"></span></td>
        <td><span class="row-skeleton" style="width:160px"></span></td>
        <td><span class="row-skeleton" style="width:30px"></span></td>
        <td><span class="row-skeleton" style="width:70px"></span></td>
        <td><span class="row-skeleton" style="width:80px"></span></td>
        <td></td>
      </tr>
    `).join('');

    tbody.innerHTML = rows;
    if (tableWrap) tableWrap.style.display = 'block';
    if (emptyState) emptyState.style.display = 'none';
  }

  renderTable() {
    const tbody = document.getElementById('clientsTbody');
    const emptyState = document.getElementById('emptyState');
    const tableWrap = tbody ? tbody.closest('.table-wrap') : null;

    // Filter locally on search
    const q = this.searchQuery.toLowerCase();
    const filtered = q
      ? this.clients.filter(c =>
          c.name.toLowerCase().includes(q) ||
          (c.email || '').toLowerCase().includes(q) ||
          (c.company || '').toLowerCase().includes(q)
        )
      : this.clients;

    if (filtered.length === 0) {
      tableWrap.style.display = 'none';
      emptyState.style.display = 'block';
      return;
    }

    tableWrap.style.display = 'block';
    emptyState.style.display = 'none';

    tbody.innerHTML = filtered.map(client => `
      <tr class="tr-clickable" onclick="window.location.href='/accounts/clients/${client.id}/'">
        <td>
          <div class="client-name">${this.escapeHtml(client.name)}</div>
          ${client.company
            ? `<div class="client-company">${this.escapeHtml(client.company)}</div>`
            : ''}
        </td>
        <td class="td-muted">${this.escapeHtml(client.email)}</td>
        <td>
          <span class="badge badge-muted">${client.project_count || 0}</span>
        </td>
        <td class="td-muted">${UIManager.formatCurrency(client.total_earnings || 0)}</td>
        <td class="td-muted td-date">${UIManager.formatDate(client.created_at)}</td>
        <td>
          <div class="td-actions" onclick="event.stopPropagation()">
            <button class="btn btn-outline btn-sm"
              onclick="clientsManager.openEditModal(${client.id})">
              Upravit
            </button>
            <button class="btn btn-danger-soft btn-sm"
              onclick="clientsManager.confirmDelete(${client.id})">
              Smazat
            </button>
          </div>
        </td>
      </tr>
    `).join('');
  }

  openAddModal() {
    this.editingId = null;
    document.getElementById('modalTitle').textContent = 'Přidat klienta';
    FormHelper.clear(document.getElementById('clientForm'));
    UIManager.modal.open('clientModal');
    setTimeout(() => document.getElementById('clientName').focus(), 80);
  }

  openEditModal(clientId) {
    const client = this.clients.find(c => c.id === clientId);
    if (!client) return;
    this.editingId = clientId;
    document.getElementById('modalTitle').textContent = 'Upravit klienta';
    FormHelper.clear(document.getElementById('clientForm'));
    FormHelper.populate(document.getElementById('clientForm'), {
      name:         client.name,
      email:        client.email,
      company:      client.company    || '',
      phone:        client.phone      || '',
      notes:        client.notes      || '',
      hourly_rate:  client.hourly_rate || 0,
    });
    UIManager.modal.open('clientModal');
    setTimeout(() => document.getElementById('clientName').focus(), 80);
  }

  async handleFormSubmit() {
    const form = document.getElementById('clientForm');
    const data = FormHelper.getData(form);
    try {
      FormHelper.setLoading(form, true);
      if (this.editingId) {
        await window.api.clients.update(this.editingId, data);
        UIManager.success('Klient upraven');
      } else {
        await window.api.clients.create(data);
        UIManager.success('Klient přidán');
      }
      UIManager.modal.close('clientModal');
      await this.loadClients();
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

  async confirmDelete(clientId) {
    const client = this.clients.find(c => c.id === clientId);
    if (!client) return;
    if (!confirm(`Opravdu chcete smazat klienta „${client.name}“?\nVšechny jeho projekty budou také smazány.`)) return;
    try {
      await window.api.clients.delete(clientId);
      UIManager.success('Klient smazán');
      await this.loadClients();
    } catch (err) {
      console.error('Delete error:', err);
      UIManager.error(err.message || 'Chyba při mazání');
    }
  }

  escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }
}

let clientsManager;
document.addEventListener('DOMContentLoaded', () => {
  if (document.getElementById('clientsTbody')) {
    clientsManager = new ClientsManager();
  }
});

