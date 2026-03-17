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
    // Add client buttons
    document.getElementById('addClientBtn')?.addEventListener('click', () => {
      this.openAddModal();
    });
    document.getElementById('addClientEmptyBtn')?.addEventListener('click', () => {
      this.openAddModal();
    });

    // Form submission
    document.getElementById('clientForm').addEventListener('submit', (e) => {
      e.preventDefault();
      this.handleFormSubmit();
    });

    // Search
    document.getElementById('searchInput')?.addEventListener(
      'input',
      UIManager.debounce((e) => {
        this.searchQuery = e.target.value;
        this.renderTable();
      }, 300)
    );
  }

  async loadClients() {
    try {
      const tbody = document.getElementById('clientsTbody');
      tbody.innerHTML = '<tr><td colspan="5" style="text-align: center; color: var(--muted);">Načítám...</td></tr>';

      this.clients = await window.api.clients.list(this.searchQuery);
      this.renderTable();
    } catch (err) {
      console.error('Failed to load clients:', err);
      UIManager.error(err.message || 'Chyba při načítání klientů');
      document.getElementById('clientsTbody').innerHTML =
        '<tr><td colspan="5" style="text-align: center; color: var(--danger);">Chyba při načítání</td></tr>';
    }
  }

  renderTable() {
    const tbody = document.getElementById('clientsTbody');
    const emptyState = document.getElementById('emptyState');
    const table = document.getElementById('clientsTable');

    if (this.clients.length === 0) {
      table.style.display = 'none';
      emptyState.style.display = 'block';
      return;
    }

    table.style.display = 'table';
    emptyState.style.display = 'none';

    tbody.innerHTML = this.clients.map(client => `
      <tr>
        <td>
          <strong>${this.escapeHtml(client.name)}</strong>
          ${client.company ? `<div style="color: var(--muted); font-size: 0.85rem;">${this.escapeHtml(client.company)}</div>` : ''}
        </td>
        <td style="color: var(--muted);">${this.escapeHtml(client.email)}</td>
        <td>${client.project_count || 0}</td>
        <td style="color: var(--muted); font-size: 0.9rem;">${UIManager.formatDate(client.created_at)}</td>
        <td style="text-align: right;">
          <div class="td-actions">
            <button class="btn-sm" onclick="clientsManager.openEditModal(${client.id})">Upravit</button>
            <button class="btn-sm danger" onclick="clientsManager.delete(${client.id})">Smazat</button>
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
  }

  openEditModal(clientId) {
    const client = this.clients.find(c => c.id === clientId);
    if (!client) return;

    this.editingId = clientId;
    document.getElementById('modalTitle').textContent = 'Upravit klienta';
    FormHelper.populate(document.getElementById('clientForm'), {
      name: client.name,
      email: client.email,
      company: client.company,
      phone: client.phone,
      notes: client.notes,
    });
    UIManager.modal.open('clientModal');
  }

  async handleFormSubmit() {
    const form = document.getElementById('clientForm');
    const data = FormHelper.getData(form);

    try {
      FormHelper.setLoading(form, true);

      if (this.editingId) {
        // Update
        await window.api.clients.update(this.editingId, data);
        UIManager.success('Klient upraven');
      } else {
        // Create
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

  async delete(clientId) {
    const client = this.clients.find(c => c.id === clientId);
    if (!client) return;

    if (!confirm(`Opravdu chcete smazat klienta "${client.name}"?\nSoučasně budou smazáni všichni jeho projekty.`)) {
      return;
    }

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
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }
}

// Initialize clients manager when DOM is ready
let clientsManager;
document.addEventListener('DOMContentLoaded', () => {
  if (document.getElementById('addClientBtn') || document.getElementById('clientsTbody')) {
    clientsManager = new ClientsManager();
  }
});
