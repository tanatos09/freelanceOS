/**
 * Sidebar Mini Timer
 * Shows a compact timer widget in the sidebar on every page.
 * Uses the same window.api as TimerManager — never modifies TimerManager state directly,
 * but syncs it when both are present on the timer page.
 */
class SidebarTimer {
  constructor() {
    this.runningCommit  = null;
    this.tickInterval   = null;
    this.reminderInterval = null;
    this.commitMode     = null; // 'commit' | 'stop'
    this._init();
  }

  async _init() {
    // Wait for API client (same pattern as TimerManager)
    for (let i = 0; i < 20; i++) {
      if (window.api && window.api.workcommits) break;
      await new Promise(r => setTimeout(r, 100));
    }
    if (!window.api || !window.api.workcommits) return;

    this._attachListeners();
    await this._refresh();
  }

  _attachListeners() {
    document.getElementById('miniTimerCommitBtn')
      ?.addEventListener('click', () => this._openCommitForm('commit'));

    document.getElementById('miniTimerStopBtn')
      ?.addEventListener('click', () => this._openCommitForm('stop'));

    document.getElementById('miniTimerSaveBtn')
      ?.addEventListener('click', () => this._submitCommit());

    document.getElementById('miniTimerCancelBtn')
      ?.addEventListener('click', () => this._closeCommitForm());

    document.getElementById('miniTimerCommitInput')
      ?.addEventListener('keydown', (e) => {
        if (e.key === 'Enter')  this._submitCommit();
        if (e.key === 'Escape') this._closeCommitForm();
      });

    document.getElementById('timerReminderOk')
      ?.addEventListener('click', () => this._hideReminderDialog());

    document.getElementById('timerReminderStop')
      ?.addEventListener('click', () => this._stopFromReminder());
  }

  async _refresh() {
    try {
      const result = await window.api.workcommits.running();
      this.runningCommit = result || null;
    } catch {
      this.runningCommit = null;
    }
    this._render();
  }

  _render() {
    const idle    = document.getElementById('miniTimerIdle');
    const running = document.getElementById('miniTimerRunning');
    if (!idle || !running) return;

    if (this.runningCommit && this.runningCommit.id) {
      idle.style.display    = 'none';
      running.style.display = 'block';
      document.getElementById('miniTimerProject').textContent =
        this.runningCommit.project_name || '—';
      this._stopTick();
      this._startTick();
    } else {
      idle.style.display    = 'block';
      running.style.display = 'none';
      this._stopTick();
    }
    this._closeCommitForm();
  }

  static REMINDER_THRESHOLD_MS = 4 * 60 * 60 * 1000;

  _startTick() {
    const tick = () => {
      const elapsed = Date.now() - new Date(this.runningCommit.start_time).getTime();
      this._updateDisplay(Math.floor(elapsed / 1000));
    };
    tick();
    this.tickInterval = setInterval(tick, 1000);
    this._startReminderCheck();
  }

  _startReminderCheck() {
    const check = () => {
      const key = `timerReminderShown_${this.runningCommit.id}`;
      if (localStorage.getItem(key)) return;
      const elapsed = Date.now() - new Date(this.runningCommit.start_time).getTime();
      if (elapsed >= SidebarTimer.REMINDER_THRESHOLD_MS) {
        localStorage.setItem(key, '1');
        this._showReminderDialog();
      }
    };
    check();
    this.reminderInterval = setInterval(check, 60_000);
  }

  _showReminderDialog() {
    const dialog = document.getElementById('timerReminderDialog');
    if (dialog) dialog.style.display = 'flex';
  }

  _hideReminderDialog() {
    const dialog = document.getElementById('timerReminderDialog');
    if (dialog) dialog.style.display = 'none';
  }

  async _stopFromReminder() {
    this._hideReminderDialog();
    if (!this.runningCommit) return;
    try {
      await window.api.workcommits.stop(this.runningCommit.id, '');
      this.runningCommit = null;
      this._render();
      if (typeof timerManager !== 'undefined' && timerManager) {
        timerManager.runningCommit = null;
        timerManager.renderTimerWidget();
        timerManager.loadTodayCommits();
      }
    } catch (err) {
      console.error('[SidebarTimer] stop from reminder:', err);
      if (typeof UIManager !== 'undefined') UIManager.error(err.message || 'Chyba při zastavení timeru.');
    }
  }

  _stopTick() {
    if (this.reminderInterval) {
      clearInterval(this.reminderInterval);
      this.reminderInterval = null;
    }
    if (this.tickInterval) {
      clearInterval(this.tickInterval);
      this.tickInterval = null;
    }
  }

  _updateDisplay(totalSeconds) {
    const h   = Math.floor(totalSeconds / 3600);
    const m   = Math.floor((totalSeconds % 3600) / 60);
    const s   = totalSeconds % 60;
    const pad = n => String(n).padStart(2, '0');
    const el  = document.getElementById('miniTimerDisplay');
    if (el) el.textContent = `${pad(h)}:${pad(m)}:${pad(s)}`;
  }

  _openCommitForm(mode) {
    this.commitMode = mode;
    const form = document.getElementById('miniTimerCommitForm');
    if (form) form.style.display = 'block';
    document.getElementById('miniTimerCommitInput')?.focus();
  }

  _closeCommitForm() {
    const form  = document.getElementById('miniTimerCommitForm');
    const input = document.getElementById('miniTimerCommitInput');
    if (form)  form.style.display = 'none';
    if (input) input.value = '';
    this.commitMode = null;
  }

  async _submitCommit() {
    if (!this.runningCommit) return;

    const input       = document.getElementById('miniTimerCommitInput');
    const description = input ? input.value.trim() : '';
    const saveBtn     = document.getElementById('miniTimerSaveBtn');

    if (saveBtn) { saveBtn.disabled = true; saveBtn.textContent = '…'; }

    try {
      if (this.commitMode === 'commit') {
        // Commit + continue
        const result = await window.api.workcommits.commit(
          this.runningCommit.id, description, true
        );
        this.runningCommit = result?.next_commit || null;
      } else {
        // Commit + stop
        await window.api.workcommits.stop(this.runningCommit.id, description);
        this.runningCommit = null;
      }

      this._render();

      // Sync with TimerManager if on the timer page
      if (typeof timerManager !== 'undefined' && timerManager) {
        timerManager.runningCommit = this.runningCommit;
        timerManager.renderTimerWidget();
        timerManager.loadTodayCommits();
      }

      if (typeof UIManager !== 'undefined') {
        UIManager.success(this.runningCommit ? 'Commit uložen.' : 'Timer zastaven.');
      }

      window.dispatchEvent(new CustomEvent('workcommit:saved'));
    } catch (err) {
      console.error('[SidebarTimer]', err);
      if (typeof UIManager !== 'undefined') {
        UIManager.error(err.message || 'Chyba při ukládání commitu.');
      }
    } finally {
      if (saveBtn) { saveBtn.disabled = false; saveBtn.textContent = 'Uložit'; }
    }
  }
}

document.addEventListener('DOMContentLoaded', () => {
  window.sidebarTimer = new SidebarTimer();
});
