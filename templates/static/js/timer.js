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
    this.syncInterval = null;
    this._visibilityHandler = null;
    this._hiddenAt = null;
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
    // Pause / Resume
    document.getElementById('pauseBtn')?.addEventListener('click', () => this.pauseTimer());
    document.getElementById('resumeBtn')?.addEventListener('click', () => this.resumeTimer());
    // Commit modal form
    document.getElementById('commitForm')?.addEventListener('submit', (e) => {
      e.preventDefault();
      this.handleCommitSubmit();
    });

    // Edit modal form
    document.getElementById('editForm')?.addEventListener('submit', (e) => {
      e.preventDefault();
      this.handleEditSubmit();
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

  /**
   * Re-sync running state + today commits from backend.
   * Called on visibility change and periodically.
   */
  async _syncFromBackend() {
    try {
      const result = await window.api.workcommits.running();
      const wasRunning = !!(this.runningCommit && this.runningCommit.id);
      const wasPaused = !!(this.runningCommit && this.runningCommit.is_paused);
      const isRunning = !!(result && result.id);
      const isPaused = !!(result && result.is_paused);
      this.runningCommit = result || null;
      if (wasRunning !== isRunning || wasPaused !== isPaused) {
        this.renderTimerWidget();
      } else if (isRunning && !isPaused) {
        // Re-anchor tick to reduce drift
        this.stopTick();
        this.startTick();
      }
    } catch (err) {
      console.error('[TimerManager] sync running failed:', err);
    }
    // Always refresh today list so totals stay accurate
    try {
      const today = new Date().toISOString().split('T')[0];
      this.todayCommits = await window.api.workcommits.list({ date: today });
      this.renderTodayList();
    } catch (err) {
      console.error('[TimerManager] sync today list failed:', err);
    }
  }

  _startBackgroundSync() {
    // Visibility-change handler: re-sync immediately when tab becomes visible
    if (!this._visibilityHandler) {
      this._visibilityHandler = () => {
        if (document.visibilityState === 'visible') {
          // If hidden for > 3 s, force a backend re-sync
          const hiddenMs = this._hiddenAt ? Date.now() - this._hiddenAt : Infinity;
          if (hiddenMs > 3000) this._syncFromBackend();
          this._hiddenAt = null;
        } else {
          this._hiddenAt = Date.now();
        }
      };
      document.addEventListener('visibilitychange', this._visibilityHandler);
    }
    // Periodic sync every 30 s (keeps "odpracov\u00e1no dnes" accurate)
    if (!this.syncInterval) {
      this.syncInterval = setInterval(() => this._syncFromBackend(), 30_000);
    }
  }

  _stopBackgroundSync() {
    if (this._visibilityHandler) {
      document.removeEventListener('visibilitychange', this._visibilityHandler);
      this._visibilityHandler = null;
    }
    if (this.syncInterval) {
      clearInterval(this.syncInterval);
      this.syncInterval = null;
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

      this.stopTick();

      const isPaused = !!this.runningCommit.is_paused;
      const pauseBtn  = document.getElementById('pauseBtn');
      const resumeBtn = document.getElementById('resumeBtn');
      const statusLabel = document.getElementById('timerStatusLabel');
      const card = runningSection.querySelector('.timer-card');

      if (isPaused) {
        if (pauseBtn)  pauseBtn.style.display  = 'none';
        if (resumeBtn) resumeBtn.style.display = 'inline-flex';
        if (statusLabel) statusLabel.textContent = 'Pozastaveno';
        if (card) card.classList.add('timer-card--paused');
        // Freeze display at current elapsed work time
        this.updateTimerDisplay(this.runningCommit.elapsed_seconds || 0);
      } else {
        if (pauseBtn)  pauseBtn.style.display  = 'inline-flex';
        if (resumeBtn) resumeBtn.style.display = 'none';
        if (statusLabel) statusLabel.textContent = 'Pracuješ na';
        if (card) card.classList.remove('timer-card--paused');
        this.startTick();
      }

      this._startBackgroundSync();
    } else {
      runningSection.style.display = 'none';
      startSection.style.display = 'block';
      this.stopTick();
      this._stopBackgroundSync();
      document.getElementById('timerDisplay').textContent = '00:00:00';
    }
  }

  /**
   * Clock-based tick anchored to backend elapsed_seconds.
   * elapsed_seconds already excludes all paused time, so the display
   * stays accurate even after multiple pause/resume cycles.
   */
  startTick() {
    const elapsedMs = (this.runningCommit.elapsed_seconds || 0) * 1000;
    this._tickAdjustedStartMs = Date.now() - elapsedMs;
    const tick = () => {
      const elapsed = Math.floor((Date.now() - this._tickAdjustedStartMs) / 1000);
      this.updateTimerDisplay(elapsed);
      this._updateTodayTotal();
    };
    tick();
    this.tickInterval = setInterval(tick, 1000);
  }

  stopTick() {
    if (this.tickInterval) {
      clearInterval(this.tickInterval);
      this.tickInterval = null;
    }
    this._tickAdjustedStartMs = null;
  }

  updateTimerDisplay(totalSeconds) {
    const h = Math.floor(totalSeconds / 3600);
    const m = Math.floor((totalSeconds % 3600) / 60);
    const s = totalSeconds % 60;
    const fmt = (n) => String(n).padStart(2, '0');
    const el = document.getElementById('timerDisplay');
    if (el) el.textContent = `${fmt(h)}:${fmt(m)}:${fmt(s)}`;
  }

  /**
   * Compute and display today's total work time.
   * Includes all finished commits + the currently running session (live).
   * Called every second from startTick() and after every data refresh.
   */
  _updateTodayTotal() {
    const allFinished = this.todayCommits.filter(c => !c.is_running);
    let total = allFinished.reduce((sum, c) => sum + (c.duration_seconds || 0), 0);

    if (this.runningCommit && this.runningCommit.id) {
      if (this._tickAdjustedStartMs && !this.runningCommit.is_paused) {
        // Live elapsed — same anchor as the clock display
        total += Math.floor((Date.now() - this._tickAdjustedStartMs) / 1000);
      } else {
        // Paused or no tick yet — use the last known elapsed from backend
        total += this.runningCommit.elapsed_seconds || 0;
      }
    }

    const totalEl = document.getElementById('todayTotal');
    if (totalEl) totalEl.textContent = this.formatDuration(total);
  }

  async pauseTimer() {
    if (!this.runningCommit || this.runningCommit.is_paused) return;
    const btn = document.getElementById('pauseBtn');
    if (btn) { btn.disabled = true; btn.textContent = '…'; }
    try {
      const result = await window.api.workcommits.pause(this.runningCommit.id);
      this.runningCommit = result;
      this.renderTimerWidget();
    } catch (err) {
      UIManager.error(err.message || 'Chyba při pozastavení timeru.');
    } finally {
      if (btn) {
        btn.disabled = false;
        btn.innerHTML = '<svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><rect x="6" y="4" width="4" height="16"/><rect x="14" y="4" width="4" height="16"/></svg> Pauza';
      }
    }
  }

  async resumeTimer() {
    if (!this.runningCommit || !this.runningCommit.is_paused) return;
    const btn = document.getElementById('resumeBtn');
    if (btn) { btn.disabled = true; btn.textContent = '…'; }
    try {
      const result = await window.api.workcommits.resume(this.runningCommit.id);
      this.runningCommit = result;
      this.renderTimerWidget();
    } catch (err) {
      UIManager.error(err.message || 'Chyba při obnovení timeru.');
    } finally {
      if (btn) {
        btn.disabled = false;
        btn.innerHTML = '<svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><polygon points="5 3 19 12 5 21 5 3"/></svg> Pokračovat';
      }
    }
  }

  async startTimer() {
    const select = document.getElementById('projectSelect');
    const projectId = select?.value;
    if (!projectId) {
      UIManager.error('Vyberte projekt pro spuštění timeru.');
      const group = select?.closest('.form-group');
      if (group) {
        group.classList.add('error');
        let errorEl = group.querySelector('.form-error');
        if (!errorEl) {
          errorEl = document.createElement('div');
          errorEl.className = 'form-error';
          group.appendChild(errorEl);
        }
        errorEl.textContent = 'Vyberte projekt.';
      }
      return;
    }
    // Clear inline error on valid selection
    const group = select?.closest('.form-group');
    if (group) {
      group.classList.remove('error');
      const errorEl = group.querySelector('.form-error');
      if (errorEl) errorEl.textContent = '';
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
      this._updateTodayTotal();
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
        <td class="td-actions">
          <button class="btn btn-outline btn-sm" onclick="timerManager.openEditModal(${c.id})">Upravit</button>
          <button class="btn btn-danger-soft btn-sm" onclick="timerManager.deleteCommit(${c.id})">Smazat</button>
        </td>
      </tr>
    `).join('');

    // Update total (accounts for running commit + all finished)
    this._updateTodayTotal();

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

  _toDatetimeLocal(isoStr) {
    if (!isoStr) return '';
    const d = new Date(isoStr);
    const pad = n => String(n).padStart(2, '0');
    return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`;
  }

  openEditModal(id) {
    const commit = this.todayCommits.find(c => c.id === id);
    if (!commit) return;
    this._editingCommitId = id;
    document.getElementById('editDescription').value = commit.description || '';
    document.getElementById('editStartTime').value = this._toDatetimeLocal(commit.start_time);
    document.getElementById('editEndTime').value = commit.end_time ? this._toDatetimeLocal(commit.end_time) : '';
    UIManager.modal.open('editModal');
    setTimeout(() => document.getElementById('editDescription').focus(), 100);
  }

  async handleEditSubmit() {
    const id = this._editingCommitId;
    if (!id) return;

    const description = document.getElementById('editDescription').value.trim();
    const startVal = document.getElementById('editStartTime').value;
    const endVal = document.getElementById('editEndTime').value;

    const payload = { description };
    if (startVal) payload.start_time = new Date(startVal).toISOString();
    if (endVal) payload.end_time = new Date(endVal).toISOString();

    const form = document.getElementById('editForm');
    FormHelper.setLoading(form, true);
    try {
      await window.api.workcommits.patch(id, payload);
      UIManager.success('Záznam upraven.');
      UIManager.modal.close('editModal');
      await this.loadTodayCommits();
    } catch (err) {
      UIManager.error(err.message || 'Chyba při ukládání.');
    } finally {
      FormHelper.setLoading(form, false);
    }
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
