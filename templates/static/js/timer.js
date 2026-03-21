/**
 * Timer Page Logic
 * Commit-based work tracking: Start → Commit (+ continue) → Stop
 */

class TimerManager {
  constructor() {
    this.runningCommit = null;
    this.projects = [];
    this.todayCommits = [];
    this.tickInterval = null;
    // Attach handlers synchronously so they're always ready before async init
    this.attachEventListeners();
    this.init();
  }

  async init() {
    // Wait for API client to be available with proper retry
    const maxRetries = 10;
    for (let i = 0; i < maxRetries; i++) {
      if (window.api && window.api.workcommits) break;
      await new Promise(resolve => setTimeout(resolve, 100));
    }
    if (!window.api || !window.api.workcommits) {
      console.error('API client not available after retries');
      UIManager.error('API klient se nepodařilo inicializovat. Obnovte stránku (Ctrl+Shift+R).');
      return;
    }
    await this.loadProjects();
    await this.loadRunning();
    await this.loadTodayCommits();
  }

  attachEventListeners() {
    // Start form
    document.getElementById('startForm')?.addEventListener('submit', (e) => {
      e.preventDefault();
      this.startTimer();
    });

    // Commit button (save + continue)
    document.getElementById('commitBtn')?.addEventListener('click', () => {
      this.openCommitModal(true);
    });

    // Stop button (save + stop)
    document.getElementById('stopBtn')?.addEventListener('click', () => {
      this.openCommitModal(false);
    });

    // Commit modal form
    document.getElementById('commitForm')?.addEventListener('submit', (e) => {
      e.preventDefault();
      this.handleCommitSubmit();
    });
  }

  async loadProjects() {
    try {
      const data = await window.api.projects.list();
      const all = Array.isArray(data) ? data : (data?.results || []);
      this.projects = all.filter(p => ['active', 'draft'].includes(p.status));
      const select = document.getElementById('projectSelect');
      if (!select) return;

      if (this.projects.length === 0) {
        select.innerHTML = '<option value="">-- Žádné projekty (vytvořte projekt) --</option>';
        select.disabled = true;
        document.getElementById('startBtn').disabled = true;
      } else {
        select.innerHTML =
          '<option value="">-- Vyberte projekt --</option>' +
          this.projects.map(p => `<option value="${p.id}">${this.escapeHtml(p.name)}${p.status === 'draft' ? ' (návrh)' : ''}</option>`).join('');
      }
    } catch (err) {
      console.error('Failed to load projects:', err);
      UIManager.error(err.message || 'Chyba při načítání projektů.');
    }
  }

  async loadRunning() {
    try {
      if (!window.api || !window.api.workcommits) {
        throw new Error('API klient nen\u00ed inicializov\u00e1n.');
      }
      const result = await window.api.workcommits.running();
      this.runningCommit = result || null;
    } catch (err) {
      console.error('Failed to load running commit:', err);
      this.runningCommit = null;
    } finally {
      this.renderTimerWidget();
    }
  }

  async loadTodayCommits() {
    try {
      const today = new Date().toISOString().split('T')[0];
      this.todayCommits = await window.api.workcommits.list({ date: today });
      this.renderTodayList();
    } catch (err) {
      console.error('Failed to load today commits:', err);
    }
  }

  renderTimerWidget() {
    const runningSection = document.getElementById('runningSection');
    const startSection = document.getElementById('startSection');

    if (!runningSection || !startSection) return;

    if (this.runningCommit && this.runningCommit.id) {
      runningSection.style.display = 'block';
      startSection.style.display = 'none';

      document.getElementById('runningProject').textContent =
        this.runningCommit.project_name || '—';

      // Start the tick
      this.stopTick();
      this.startTick(this.runningCommit.elapsed_seconds || 0);
    } else {
      runningSection.style.display = 'none';
      startSection.style.display = 'block';
      this.stopTick();
      document.getElementById('timerDisplay').textContent = '00:00:00';
    }
  }

  startTick(initialSeconds) {
    let elapsed = initialSeconds;
    this.updateTimerDisplay(elapsed);

    this.tickInterval = setInterval(() => {
      elapsed++;
      this.updateTimerDisplay(elapsed);
    }, 1000);
  }

  stopTick() {
    if (this.tickInterval) {
      clearInterval(this.tickInterval);
      this.tickInterval = null;
    }
  }

  updateTimerDisplay(totalSeconds) {
    const h = Math.floor(totalSeconds / 3600);
    const m = Math.floor((totalSeconds % 3600) / 60);
    const s = totalSeconds % 60;
    const fmt = (n) => String(n).padStart(2, '0');
    const el = document.getElementById('timerDisplay');
    if (el) el.textContent = `${fmt(h)}:${fmt(m)}:${fmt(s)}`;
  }

  async startTimer() {
    const projectId = document.getElementById('projectSelect')?.value;
    if (!projectId) {
      UIManager.error('Vyberte projekt pro spuštění timeru.');
      return;
    }

    if (!window.api || !window.api.workcommits || typeof window.api.workcommits.start !== 'function') {
      UIManager.error('API klient není dostupný. Obnovte stránku.');
      return;
    }

    const btn = document.getElementById('startBtn');
    btn.disabled = true;
    btn.textContent = '…';

    try {
      const result = await window.api.workcommits.start(parseInt(projectId));
      if (!result || !result.id) {
        throw new Error('Neplatná odpověď ze serveru.');
      }
      this.runningCommit = result;
      UIManager.success('Timer spuštěn!');
      this.renderTimerWidget();
      await this.loadTodayCommits();
    } catch (err) {
      UIManager.error(err.message || 'Chyba při spuštění timeru');
    } finally {
      btn.disabled = false;
      btn.innerHTML = '▶ Spustit';
    }
  }

  // ── Tag history helpers ──────────────────────
  _getTagHistory() {
    try { return JSON.parse(localStorage.getItem('tagHistory') || '[]'); } catch { return []; }
  }
  _saveTagToHistory(tag) {
    if (!tag) return;
    const history = [tag, ...this._getTagHistory().filter(t => t !== tag)].slice(0, 5);
    localStorage.setItem('tagHistory', JSON.stringify(history));
    localStorage.setItem('lastCommitTag', tag);
  }
  _renderTagSuggestions(currentTag) {
    const container = document.getElementById('tagSuggestions');
    if (!container) return;
    const tags = this._getTagHistory();
    if (tags.length === 0) { container.innerHTML = ''; return; }
    const top3 = tags.slice(0, 3);
    container.innerHTML = top3.map(t =>
      `<button type="button" class="tag-suggestion-btn${t === currentTag ? ' is-active' : ''}" data-tag="${this.escapeHtml(t)}">${this.escapeHtml(t)}</button>`
    ).join('');
    container.querySelectorAll('.tag-suggestion-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const input = document.getElementById('commitTag');
        if (input.value === btn.dataset.tag) {
          input.value = '';
          btn.classList.remove('is-active');
        } else {
          input.value = btn.dataset.tag;
          container.querySelectorAll('.tag-suggestion-btn').forEach(b => b.classList.remove('is-active'));
          btn.classList.add('is-active');
        }
      });
    });
  }

  openCommitModal(shouldContinue) {
    if (!this.runningCommit) return;
    this._pendingContinue = shouldContinue;
    document.getElementById('commitModalTitle').textContent = shouldContinue
      ? 'Commit + pokračovat'
      : 'Commit + zastavit';
    document.getElementById('commitDescription').value = '';
    const lastTag = localStorage.getItem('lastCommitTag') || '';
    document.getElementById('commitTag').value = lastTag;
    UIManager.modal.open('commitModal');
    this._renderTagSuggestions(lastTag);
    // keep active state in sync when user types
    document.getElementById('commitTag').oninput = (e) => {
      document.querySelectorAll('.tag-suggestion-btn').forEach(b =>
        b.classList.toggle('is-active', b.dataset.tag === e.target.value)
      );
    };
    setTimeout(() => document.getElementById('commitDescription').focus(), 100);
  }

  async handleCommitSubmit() {
    if (!this.runningCommit) return;

    if (!window.api || !window.api.workcommits) {
      UIManager.error('API klient není dostupný. Obnovte stránku.');
      return;
    }

    const description = document.getElementById('commitDescription').value.trim();
    const tag = document.getElementById('commitTag').value.trim() || null;
    const form = document.getElementById('commitForm');
    FormHelper.setLoading(form, true);

    try {
      if (this._pendingContinue) {
        // commit + continue
        const result = await window.api.workcommits.commit(
          this.runningCommit.id,
          description,
          true,
          tag
        );
        this.runningCommit = result?.next_commit || null;
        this._saveTagToHistory(tag);
        UIManager.success('Commit uložen, timer pokračuje.');
      } else {
        // stop
        await window.api.workcommits.stop(this.runningCommit.id, description, tag);
        this._saveTagToHistory(tag);
        this.runningCommit = null;
        UIManager.success('Timer zastaven a commit uložen.');
      }

      UIManager.modal.close('commitModal');
      this.renderTimerWidget();
      await this.loadTodayCommits();
    } catch (err) {
      UIManager.error(err.message || 'Chyba při ukládání commitu');
    } finally {
      FormHelper.setLoading(form, false);
    }
  }

  renderTodayList() {
    const tbody = document.getElementById('todayTbody');
    const emptyState = document.getElementById('todayEmpty');
    const tableWrap = tbody ? tbody.closest('.table-wrap') : null;

    if (!tbody) return;

    const allFinished = this.todayCommits.filter(c => !c.is_running);

    // ── Tag filter bar ───────────────────────
    const filterBar = document.getElementById('tagFilterBar');
    const tags = [...new Set(allFinished.map(c => c.tag).filter(Boolean))];
    if (filterBar) {
      if (tags.length > 1) {
        filterBar.style.display = 'flex';
        const active = this._activeTagFilter || null;
        filterBar.innerHTML =
          `<button class="tag-filter-btn${!active ? ' is-active' : ''}" data-tag="">Vše</button>` +
          tags.map(t => `<button class="tag-filter-btn${t === active ? ' is-active' : ''}" data-tag="${this.escapeHtml(t)}">${this.escapeHtml(t)}</button>`).join('');
        filterBar.querySelectorAll('.tag-filter-btn').forEach(btn => {
          btn.addEventListener('click', () => {
            this._activeTagFilter = btn.dataset.tag || null;
            this.renderTodayList();
          });
        });
      } else {
        filterBar.style.display = 'none';
        this._activeTagFilter = null;
      }
    }

    const finished = this._activeTagFilter
      ? allFinished.filter(c => c.tag === this._activeTagFilter)
      : allFinished;

    if (finished.length === 0) {
      if (tableWrap) tableWrap.style.display = 'none';
      if (emptyState) emptyState.style.display = 'block';
      return;
    }

    if (tableWrap) tableWrap.style.display = '';
    if (emptyState) emptyState.style.display = 'none';

    tbody.innerHTML = finished.map(c => `
      <tr>
        <td class="td-muted td-time">${this.formatTime(c.start_time)}</td>
        <td><strong>${this.escapeHtml(c.project_name || '')}</strong></td>
        <td class="td-muted">${this.escapeHtml(c.description || '—')}<span class="commit-tag-wrap" data-id="${c.id}">${c.tag ? ' <span class="badge badge-tag badge-tag--edit" title="Klikni pro úpravu">' + this.escapeHtml(c.tag) + '</span>' : ' <span class="commit-tag-add" title="Přidat tag">+ tag</span>'}</span></td>
        <td class="td-duration">${this.formatDuration(c.duration_seconds)}</td>
        <td>
          <button class="btn btn-danger-soft btn-sm" onclick="timerManager.deleteCommit(${c.id})">Smazat</button>
        </td>
      </tr>
    `).join('');

    // Update total
    const total = finished.reduce((sum, c) => sum + (c.duration_seconds || 0), 0);
    const totalEl = document.getElementById('todayTotal');
    if (totalEl) totalEl.textContent = this.formatDuration(total);

    // Inline tag edit
    tbody.querySelectorAll('.commit-tag-wrap').forEach(wrap => {
      const commitId = parseInt(wrap.dataset.id);
      const commit = finished.find(c => c.id === commitId);
      wrap.querySelector('.badge-tag--edit, .commit-tag-add')?.addEventListener('click', () => {
        const currentTag = commit?.tag || '';
        wrap.innerHTML = `<input class="commit-tag-input" type="text" value="${this.escapeHtml(currentTag)}" maxlength="50" placeholder="tag…" autocomplete="off">`;
        const input = wrap.querySelector('input');
        input.focus();
        input.select();
        const save = async () => {
          const newTag = input.value.trim() || null;
          if (newTag === (currentTag || null)) { await this.loadTodayCommits(); return; }
          try {
            await window.api.workcommits.patch(commitId, { tag: newTag });
            if (newTag) this._saveTagToHistory(newTag);
          } catch(e) { UIManager.error('Chyba při ukládání tagu'); }
          await this.loadTodayCommits();
        };
        input.addEventListener('blur', save);
        input.addEventListener('keydown', e => {
          if (e.key === 'Enter') { e.preventDefault(); input.blur(); }
          if (e.key === 'Escape') { input.removeEventListener('blur', save); this.loadTodayCommits(); }
        });
      });
    });
  }

  async deleteCommit(id) {
    if (!confirm('Opravdu chcete smazat tento commit?')) return;
    try {
      await window.api.workcommits.delete(id);
      UIManager.success('Commit smazán');
      await this.loadTodayCommits();
    } catch (err) {
      UIManager.error(err.message || 'Chyba při mazání');
    }
  }

  formatTime(isoString) {
    if (!isoString) return '—';
    const d = new Date(isoString);
    return d.toLocaleTimeString('cs-CZ', { hour: '2-digit', minute: '2-digit' });
  }

  formatDuration(seconds) {
    if (!seconds) return '0:00';
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    if (h > 0) return `${h}h ${String(m).padStart(2, '0')}m`;
    const s = seconds % 60;
    return `${m}:${String(s).padStart(2, '0')}`;
  }

  escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }
}

// Initialize timer manager
let timerManager;
document.addEventListener('DOMContentLoaded', () => {
  if (document.getElementById('timerDisplay')) {
    timerManager = new TimerManager();
  }
});
