import {
  loadBundleFromFile,
  getCharacterList,
  getPlayerView,
  createEmptyCompanionDelta,
  getEffectiveCharacter,
  recordCharacterPatch,
  addPlayerNote,
  removePlayerNote,
  countDeltaEntries,
  buildCompanionDeltaPayload,
  parseCompanionDeltaJson,
} from "./library.js";
import {
  t,
  translateDocument,
  getLocale,
  setLocale,
  detectLocale,
  formatTimestamp,
} from "./i18n.js";

const fileInput = document.querySelector("#bundle-file");
const dropzone = document.querySelector(".dropzone");
const clearButton = document.querySelector("#clear-button");
const statusNode = document.querySelector("#status");
const installHintsNode = document.querySelector("#install-hints");
const summaryNode = document.querySelector("#summary");
const worldsNode = document.querySelector("#worlds");
const sessionsNode = document.querySelector("#sessions");
const rulesetsNode = document.querySelector("#rulesets");
const mediaNode = document.querySelector("#media");

const playerOverlay = document.createElement("div");
playerOverlay.className = "player-overlay hidden";
playerOverlay.setAttribute("role", "dialog");
playerOverlay.setAttribute("aria-modal", "true");
playerOverlay.setAttribute("aria-labelledby", "player-dialog-title");
document.body.appendChild(playerOverlay);

const playerModeRow = document.createElement("div");
playerModeRow.className = "button-row hidden";
playerModeRow.innerHTML = `
  <button type="button" class="ghost" id="player-mode-btn"></button>
  <button type="button" class="accent-btn hidden" id="export-delta-btn"></button>
  <button type="button" class="ghost hidden" id="reset-delta-btn"></button>
`;
statusNode.after(playerModeRow);

const playerModeBtn = playerModeRow.querySelector("#player-mode-btn");
const exportDeltaBtn = playerModeRow.querySelector("#export-delta-btn");
const resetDeltaBtn = playerModeRow.querySelector("#reset-delta-btn");

const STORAGE_KEY = "rpx-companion:last-bundle:v1";
const DELTA_STORAGE_KEY = "rpx-companion:delta:v1";

let bundleState = null;
let deltaState = createEmptyCompanionDelta();
let activePlayerView = null;
let previousFocusElement = null;

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function createNode(tagName, className = "", text = null) {
  const node = document.createElement(tagName);
  if (className) {
    node.className = className;
  }
  if (text != null) {
    node.textContent = String(text);
  }
  return node;
}

function appendNode(parent, tagName, className = "", text = null) {
  const node = createNode(tagName, className, text);
  parent.appendChild(node);
  return node;
}

function renderEmptyMessage(target, className, message) {
  target.className = className;
  target.replaceChildren(createNode("p", "", message));
}

function createMetaList(rows) {
  const list = createNode("ul", "meta-list");
  rows.forEach(([label, value]) => {
    const item = createNode("li");
    appendNode(item, "span", "", label);
    appendNode(item, "strong", "", value);
    list.appendChild(item);
  });
  return list;
}

function createPillRow(values, emptyText) {
  const row = createNode("div", "pill-row");
  const safeValues = values ?? [];
  if (safeValues.length) {
    safeValues.forEach((value) => row.appendChild(createNode("span", "pill", value)));
  } else {
    row.appendChild(createNode("span", "pill", emptyText));
  }
  return row;
}

function setStatus(message, isError = false) {
  statusNode.textContent = message;
  statusNode.classList.toggle("is-error", isError);
}

function detectPlatform() {
  const userAgent = navigator.userAgent.toLowerCase();
  if (/iphone|ipad|ipod/.test(userAgent) || (navigator.platform === "MacIntel" && navigator.maxTouchPoints > 1)) {
    return "ios";
  }
  if (userAgent.includes("android")) {
    return "android";
  }
  return "desktop";
}

function isStandaloneMode() {
  return Boolean(window.matchMedia?.("(display-mode: standalone)")?.matches || navigator.standalone);
}

function saveBundleSnapshot(bundle) {
  try {
    localStorage.setItem(
      STORAGE_KEY,
      JSON.stringify({
        version: 1,
        savedAt: Date.now(),
        bundle,
      })
    );
    return true;
  } catch {
    return false;
  }
}

function clearBundleSnapshot() {
  try {
    localStorage.removeItem(STORAGE_KEY);
  } catch {
    // ignore
  }
}

function restoreBundleSnapshot() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) {
      return null;
    }
    const parsed = JSON.parse(raw);
    if (parsed?.version !== 1 || parsed?.bundle?.manifest?.format !== "rpx-campaign-bundle-v1") {
      clearBundleSnapshot();
      return null;
    }
    return parsed.bundle;
  } catch {
    clearBundleSnapshot();
    return null;
  }
}

function saveDeltaSnapshot(bundle, currentDelta) {
  try {
    const payload = buildCompanionDeltaPayload(bundle, currentDelta);
    localStorage.setItem(DELTA_STORAGE_KEY, JSON.stringify(payload));
    return true;
  } catch {
    return false;
  }
}

function clearDeltaSnapshot() {
  try {
    localStorage.removeItem(DELTA_STORAGE_KEY);
  } catch {
    // ignore
  }
}

function restoreDeltaSnapshot(bundle) {
  try {
    const raw = localStorage.getItem(DELTA_STORAGE_KEY);
    if (!raw) {
      return createEmptyCompanionDelta(bundle);
    }
    const restored = parseCompanionDeltaJson(raw);
    if (bundle?.sourceName && restored.sourceName && restored.sourceName !== bundle.sourceName) {
      return createEmptyCompanionDelta(bundle);
    }
    if (
      bundle?.manifest?.exported_at != null &&
      restored.bundleExportedAt != null &&
      restored.bundleExportedAt !== bundle.manifest.exported_at
    ) {
      return createEmptyCompanionDelta(bundle);
    }
    return restored;
  } catch {
    clearDeltaSnapshot();
    return createEmptyCompanionDelta(bundle);
  }
}

function syncToolbarButtons() {
  playerModeBtn.textContent = t("action_player_mode");
  const { totalCount } = countDeltaEntries(deltaState);
  exportDeltaBtn.textContent = t("action_export_delta", { count: totalCount });
  resetDeltaBtn.textContent = t("action_reset_delta");
  const showDeltaActions = Boolean(bundleState) && totalCount > 0;
  exportDeltaBtn.classList.toggle("hidden", !showDeltaActions);
  resetDeltaBtn.classList.toggle("hidden", !showDeltaActions);
}

function renderInstallHints() {
  const platform = detectPlatform();
  const hints = [];
  const standalone = isStandaloneMode();

  if (platform === "ios") {
    hints.push({
      title: standalone ? t("hint_ios_standalone_title") : t("hint_ios_browser_title"),
      body: standalone ? t("hint_ios_standalone_body") : t("hint_ios_browser_body"),
    });
  } else if (platform === "android") {
    hints.push({
      title: standalone ? t("hint_android_standalone_title") : t("hint_android_browser_title"),
      body: standalone ? t("hint_android_standalone_body") : t("hint_android_browser_body"),
    });
  } else {
    hints.push({
      title: t("hint_desktop_title"),
      body: t("hint_desktop_body"),
    });
  }

  hints.push({
    title: navigator.onLine ? t("hint_offline_ready_title") : t("hint_offline_active_title"),
    body: navigator.onLine ? t("hint_offline_ready_body") : t("hint_offline_active_body"),
  });

  if (!bundleState) {
    hints.push({
      title: t("hint_test_step_title"),
      body: t("hint_test_step_body"),
    });
  }

  installHintsNode.innerHTML = hints.map((hint) => `
    <article class="hint-card">
      <div class="hint-title">${escapeHtml(hint.title)}</div>
      <p>${escapeHtml(hint.body)}</p>
    </article>
  `).join("");
}

function renderEmpty() {
  summaryNode.className = "empty-state";
  summaryNode.innerHTML = `<p>${escapeHtml(t("summary_empty"))}</p>`;
  worldsNode.className = "card-grid empty-state";
  worldsNode.innerHTML = `<p>${escapeHtml(t("worlds_empty"))}</p>`;
  sessionsNode.className = "stack empty-state";
  sessionsNode.innerHTML = `<p>${escapeHtml(t("sessions_empty"))}</p>`;
  rulesetsNode.className = "stack empty-state";
  rulesetsNode.innerHTML = `<p>${escapeHtml(t("rulesets_empty"))}</p>`;
  mediaNode.className = "stack empty-state";
  mediaNode.innerHTML = `<p>${escapeHtml(t("media_empty"))}</p>`;
}

function renderSummary(bundle) {
  const { manifest, summary, sourceName } = bundle;
  summaryNode.className = "summary-grid";
  const rows = [
    [t("meta_source"), sourceName],
    [t("meta_worlds"), summary.worldCount],
    [t("meta_sessions"), summary.sessionCount],
    [t("meta_characters"), summary.characterCount],
    [t("player_overlay_missions"), summary.activeMissionCount],
    [t("meta_media_mode"), manifest.media_mode ?? "none"],
    [t("meta_exported"), formatTimestamp(manifest.exported_at, getLocale())],
    [t("meta_schema"), manifest.app?.schema_version ?? "–"],
  ];
  summaryNode.replaceChildren(...rows.map(([label, value]) => {
    const card = createNode("article", "stat-card");
    appendNode(card, "div", "label", label);
    appendNode(card, "div", "value", value);
    return card;
  }));
}

function renderWorlds(bundle) {
  if (!bundle.worlds.length) {
    renderEmptyMessage(worldsNode, "card-grid empty-state", t("worlds_empty"));
    return;
  }

  worldsNode.className = "card-grid";
  worldsNode.replaceChildren(...bundle.worlds.map((world) => {
    const card = createNode("article", "detail-card");
    appendNode(card, "h3", "", world.name);
    appendNode(card, "p", "", world.genre);
    card.appendChild(createMetaList([
      [t("panel_worlds_title"), world.mapCount],
      [t("meta_locations"), world.locationCount],
      [t("meta_main_map"), world.mapImage ?? t("meta_unknown")],
    ]));
    card.appendChild(createPillRow(world.featuredLocations, "–"));
    return card;
  }));
}

function renderCharacters(parent, sessionId, characters) {
  if (!characters.length) {
    parent.appendChild(createNode("p", "meta-note", "–"));
    return;
  }
  characters.forEach((rawCharacter) => {
    const character = bundleState
      ? getEffectiveCharacter(bundleState, deltaState, sessionId, rawCharacter.id)
      : rawCharacter;
    const line = createNode("div", "chat-line");
    const nameRow = createNode("div");
    appendNode(nameRow, "strong", "", character.name);
    if (character.hasDelta) {
      appendNode(nameRow, "span", "delta-badge", t("delta_badge_modified"));
    }
    line.appendChild(nameRow);
    appendNode(
      line,
      "div",
      "meta-note",
      `${t("player_overlay_hp")} ${character.health ?? "–"}/${character.maxHealth ?? "–"} · ${t("player_overlay_mana")} ${character.mana ?? "–"}/${character.maxMana ?? "–"} · ${t("meta_gold")} ${character.gold ?? "–"}`
    );
    parent.appendChild(line);
  });
}

function renderMissions(parent, session) {
  if (!session.activeMissions.length) {
    parent.appendChild(
      createNode("p", "meta-note", `${t("player_overlay_no_missions")} (${session.completedMissionCount})`)
    );
    return;
  }
  parent.appendChild(createPillRow(session.activeMissions.map((mission) => mission.name), t("player_overlay_no_missions")));
  parent.appendChild(
    createNode("p", "meta-note", t("missions_completed", { count: session.completedMissionCount }))
  );
}

function renderChat(parent, chat) {
  if (!chat.length) {
    parent.appendChild(createNode("p", "meta-note", t("player_overlay_no_chat")));
    return;
  }
  chat.forEach((message) => {
    const line = createNode("div", "chat-line");
    appendNode(line, "div", "chat-meta", `${message.role ?? "system"} · ${message.author ?? t("meta_unknown")}`);
    appendNode(line, "div", "chat-content", message.content ?? "");
    parent.appendChild(line);
  });
}

function renderSessions(bundle) {
  if (!bundle.sessions.length) {
    renderEmptyMessage(sessionsNode, "stack empty-state", t("sessions_empty"));
    return;
  }

  sessionsNode.className = "stack";
  sessionsNode.replaceChildren(...bundle.sessions.map((session) => {
    const card = createNode("article", "detail-card");
    appendNode(card, "h3", "", session.name);
    appendNode(card, "p", "session-world", session.worldName);
    const layout = createNode("div", "session-layout");

    const charactersPanel = createNode("section", "subpanel");
    appendNode(charactersPanel, "h4", "", t("meta_characters"));
    renderCharacters(charactersPanel, session.id, session.characters);
    layout.appendChild(charactersPanel);

    const missionsPanel = createNode("section", "subpanel");
    appendNode(missionsPanel, "h4", "", t("player_overlay_missions"));
    renderMissions(missionsPanel, session);
    layout.appendChild(missionsPanel);

    const chatPanel = createNode("section", "subpanel");
    appendNode(chatPanel, "h4", "", t("player_overlay_chat"));
    renderChat(chatPanel, session.chat);
    layout.appendChild(chatPanel);

    card.appendChild(layout);
    return card;
  }));
}

function renderRulesets(bundle) {
  if (!bundle.rulesets.length) {
    renderEmptyMessage(rulesetsNode, "stack empty-state", t("rulesets_empty"));
    return;
  }

  rulesetsNode.className = "stack";
  rulesetsNode.replaceChildren(...bundle.rulesets.map((ruleset) => {
    const card = createNode("article", "ruleset-card");
    appendNode(card, "h3", "", ruleset.name);
    card.appendChild(createMetaList([
      [t("ruleset_weapons"), ruleset.weaponCount],
      [t("ruleset_spells"), ruleset.spellCount],
      [t("ruleset_file"), ruleset.file],
    ]));
    return card;
  }));
}

function renderMedia(bundle) {
  if (!bundle.mediaEntries.length) {
    renderEmptyMessage(mediaNode, "stack empty-state", t("media_empty"));
    return;
  }

  mediaNode.className = "stack";
  mediaNode.replaceChildren(...bundle.mediaEntries.slice(0, 18).map((entry) => {
    const card = createNode("article", "media-card");
    appendNode(card, "strong", "", entry.kind ?? t("media_kind_fallback"));
    appendNode(card, "div", "media-path", entry.bundle_path ?? t("media_no_path"));
    appendNode(
      card,
      "div",
      "meta-note",
      t("media_meta_line", {
        source: entry.original_path ?? "–",
        exists: entry.exists ? t("bool_yes") : t("bool_no"),
        included: entry.included ? t("bool_yes") : t("bool_no"),
      })
    );
    return card;
  }));
}

function renderBundle(bundle) {
  renderSummary(bundle);
  renderWorlds(bundle);
  renderSessions(bundle);
  renderRulesets(bundle);
  renderMedia(bundle);
  syncToolbarButtons();
}

function renderStatBar(current, max, cssClass) {
  const pct = max > 0 && current != null
    ? Math.max(0, Math.min(100, Math.round((current / max) * 100)))
    : 0;
  return `<div class="stat-bar"><div class="stat-bar-fill ${escapeHtml(cssClass)}" style="width:${pct}%"></div></div>`;
}

function commitDeltaUpdate(nextDelta) {
  deltaState = nextDelta;
  if (bundleState) {
    const persisted = saveDeltaSnapshot(bundleState, deltaState);
    if (!persisted) {
      setStatus(t("status_loaded_unpersisted", { name: bundleState.sourceName ?? "Delta" }), true);
    }
    renderBundle(bundleState);
  }
}

function renderPlayerCard(sessionId, characterId, focusSelector = "#player-dialog-title") {
  if (!bundleState) {
    return;
  }
  activePlayerView = { mode: "card", sessionId, characterId };
  const view = getPlayerView(bundleState, sessionId, characterId);
  const character = getEffectiveCharacter(bundleState, deltaState, sessionId, characterId);
  const { activeMissions } = view;
  const charNotes = (deltaState.playerNotes ?? []).filter(
    (note) => note.sessionId === sessionId && (!note.characterId || note.characterId === characterId)
  );
  const { totalCount } = countDeltaEntries(deltaState);

  playerOverlay.innerHTML = `
    <div class="player-card">
      <h2 id="player-dialog-title" tabindex="-1">
        ${escapeHtml(character.name)}
        ${character.hasDelta ? `<span class="delta-badge">${escapeHtml(t("delta_badge_modified"))}</span>` : ""}
      </h2>
      <ul class="meta-list">
        <li><span>${escapeHtml(t("player_overlay_hp"))}</span><strong>${escapeHtml(character.health ?? "–")} / ${escapeHtml(character.maxHealth ?? "–")}</strong></li>
      </ul>
      ${renderStatBar(character.health, character.maxHealth, "hp")}
      <ul class="meta-list">
        <li><span>${escapeHtml(t("player_overlay_mana"))}</span><strong>${escapeHtml(character.mana ?? "–")} / ${escapeHtml(character.maxMana ?? "–")}</strong></li>
      </ul>
      ${renderStatBar(character.mana, character.maxMana, "mana")}
      <ul class="meta-list">
        <li><span>${escapeHtml(t("meta_gold"))}</span><strong>${escapeHtml(character.gold ?? "–")}</strong></li>
      </ul>
      <h3>${escapeHtml(t("player_overlay_missions"))}</h3>
      ${activeMissions.length
        ? `<div class="pill-row">${activeMissions.map((mission) => `<span class="pill">${escapeHtml(mission.name)}</span>`).join("")}</div>`
        : `<p class="meta-note">${escapeHtml(t("player_overlay_no_missions"))}</p>`}

      <section class="delta-panel">
        <h3>${escapeHtml(t("delta_section_title"))}</h3>
        <p id="delta-form-error" class="status is-error hidden" role="alert"></p>
        <form id="delta-stats-form" novalidate>
          <div class="delta-grid">
            <label class="delta-field">
              <span>${escapeHtml(t("player_overlay_hp"))}</span>
              <input id="delta-hp" type="number" required min="0" ${character.maxHealth > 0 ? `max="${escapeHtml(character.maxHealth)}"` : ""} value="${escapeHtml(character.health ?? 0)}">
            </label>
            <label class="delta-field">
              <span>${escapeHtml(t("player_overlay_mana"))}</span>
              <input id="delta-mana" type="number" required min="0" ${character.maxMana > 0 ? `max="${escapeHtml(character.maxMana)}"` : ""} value="${escapeHtml(character.mana ?? 0)}">
            </label>
            <label class="delta-field">
              <span>${escapeHtml(t("meta_gold"))}</span>
              <input id="delta-gold" type="number" required min="0" value="${escapeHtml(character.gold ?? 0)}">
            </label>
          </div>
          <div class="button-row">
            <button type="submit" class="ghost" id="delta-save-stats-btn">${escapeHtml(t("delta_save_stats"))}</button>
          </div>
        </form>

        <form id="delta-note-form" class="delta-note-form">
          <textarea id="delta-note-input" maxlength="500" placeholder="${escapeHtml(t("delta_note_placeholder"))}" aria-label="${escapeHtml(t("delta_note_placeholder"))}"></textarea>
          <div class="button-row">
            <button type="submit" class="ghost" id="delta-add-note-btn">${escapeHtml(t("delta_add_note"))}</button>
            ${totalCount > 0 ? `<button type="button" class="accent-btn" id="delta-inline-export-btn">${escapeHtml(t("action_export_delta", { count: totalCount }))}</button>` : ""}
          </div>
        </form>

        ${charNotes.length
          ? `<ul class="delta-note-list">${charNotes.map((note) => `
              <li class="delta-note-item">
                <span class="delta-note-text">${escapeHtml(note.content)}</span>
                <button type="button" class="ghost delta-remove-btn" data-note-id="${escapeHtml(note.id)}">${escapeHtml(t("delta_remove_note"))}</button>
              </li>
            `).join("")}</ul>`
          : `<p class="meta-note" style="margin-top:10px">${escapeHtml(t("delta_no_notes"))}</p>`}
      </section>

      <div class="button-row">
        <button type="button" class="ghost" id="player-pick">← ${escapeHtml(t("player_overlay_select"))}</button>
        <button type="button" class="ghost" id="player-card-close">${escapeHtml(t("player_overlay_close"))}</button>
      </div>
    </div>
  `;

  const errorBanner = playerOverlay.querySelector("#delta-form-error");
  const showDeltaError = (msg) => {
    if (errorBanner) {
      errorBanner.textContent = msg;
      errorBanner.classList.remove("hidden");
    }
    setStatus(msg, true);
  };

  playerOverlay.querySelector("#delta-stats-form").addEventListener("submit", (event) => {
    event.preventDefault();
    const hpVal = playerOverlay.querySelector("#delta-hp").value;
    const manaVal = playerOverlay.querySelector("#delta-mana").value;
    const goldVal = playerOverlay.querySelector("#delta-gold").value;
    try {
      const updated = recordCharacterPatch(deltaState, bundleState, sessionId, characterId, {
        health: hpVal,
        mana: manaVal,
        gold: goldVal,
      });
      commitDeltaUpdate(updated);
      renderPlayerCard(sessionId, characterId, "#delta-save-stats-btn");
    } catch {
      showDeltaError(t("delta_invalid_input"));
    }
  });

  playerOverlay.querySelector("#delta-note-form").addEventListener("submit", (event) => {
    event.preventDefault();
    const input = playerOverlay.querySelector("#delta-note-input");
    const text = input.value.trim();
    if (!text) {
      return;
    }
    try {
      const updated = addPlayerNote(deltaState, bundleState, {
        sessionId,
        characterId,
        author: character.name,
        content: text,
      });
      commitDeltaUpdate(updated);
      renderPlayerCard(sessionId, characterId, "#delta-note-input");
    } catch (err) {
      showDeltaError(err instanceof Error ? err.message : t("delta_invalid_input"));
    }
  });

  playerOverlay.querySelectorAll(".delta-remove-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      const updated = removePlayerNote(deltaState, btn.dataset.noteId);
      commitDeltaUpdate(updated);
      renderPlayerCard(sessionId, characterId, "#delta-note-input");
    });
  });

  const inlineExport = playerOverlay.querySelector("#delta-inline-export-btn");
  if (inlineExport) {
    inlineExport.addEventListener("click", triggerDeltaDownload);
  }

  playerOverlay.querySelector("#player-pick").addEventListener("click", () => {
    renderPlayerPicker(bundleState);
  });
  playerOverlay.querySelector("#player-card-close").addEventListener("click", hidePlayerMode);

  if (focusSelector) {
    const targetNode = playerOverlay.querySelector(focusSelector) ?? playerOverlay.querySelector("#player-dialog-title");
    if (targetNode && typeof targetNode.focus === "function") {
      targetNode.focus();
    }
  }
}

function renderPlayerPicker(bundle) {
  activePlayerView = { mode: "picker" };
  const characters = getCharacterList(bundle);
  if (!characters.length) {
    playerOverlay.innerHTML = `
      <div class="player-card">
        <h2 id="player-dialog-title">${escapeHtml(t("player_overlay_title"))}</h2>
        <p class="meta-note">${escapeHtml(t("player_overlay_no_characters"))}</p>
        <div class="button-row"><button type="button" class="ghost" id="player-back">← ${escapeHtml(t("player_overlay_close"))}</button></div>
      </div>
    `;
    const closeBtn = playerOverlay.querySelector("#player-back");
    closeBtn.addEventListener("click", hidePlayerMode);
    closeBtn.focus();
    return;
  }

  playerOverlay.innerHTML = `
    <div class="player-card">
      <h2 id="player-dialog-title">${escapeHtml(t("player_overlay_title"))}</h2>
      <p class="meta-note">${escapeHtml(t("player_overlay_select"))}:</p>
      <ul class="character-list">
        ${characters.map((character) => {
          const effective = getEffectiveCharacter(bundle, deltaState, character.sessionId, character.characterId);
          return `
            <li class="character-item"
                tabindex="0"
                role="button"
                data-session="${escapeHtml(character.sessionId)}"
                data-character="${escapeHtml(character.characterId)}">
              <strong>
                ${escapeHtml(character.characterName)}
                ${effective.hasDelta ? `<span class="delta-badge">${escapeHtml(t("delta_badge_modified"))}</span>` : ""}
              </strong>
              <span class="meta-note">${escapeHtml(character.sessionName)}</span>
            </li>
          `;
        }).join("")}
      </ul>
      <div class="button-row"><button type="button" class="ghost" id="player-back">← ${escapeHtml(t("player_overlay_close"))}</button></div>
    </div>
  `;

  playerOverlay.querySelectorAll(".character-item").forEach((item) => {
    const activate = () => {
      renderPlayerCard(item.dataset.session, item.dataset.character);
    };
    item.addEventListener("click", activate);
    item.addEventListener("keydown", (event) => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        activate();
      }
    });
  });
  playerOverlay.querySelector("#player-back").addEventListener("click", hidePlayerMode);
  const firstItem = playerOverlay.querySelector(".character-item");
  if (firstItem) {
    firstItem.focus();
  }
}

function showPlayerMode() {
  if (!bundleState) {
    return;
  }
  previousFocusElement = document.activeElement instanceof HTMLElement ? document.activeElement : playerModeBtn;
  playerOverlay.classList.remove("hidden");
  renderPlayerPicker(bundleState);
}

function hidePlayerMode() {
  const wasOpen = !playerOverlay.classList.contains("hidden");
  playerOverlay.classList.add("hidden");
  activePlayerView = null;
  if (wasOpen && previousFocusElement && typeof previousFocusElement.focus === "function") {
    previousFocusElement.focus();
    previousFocusElement = null;
  }
}

function triggerDeltaDownload() {
  if (!bundleState) {
    return;
  }
  const { totalCount } = countDeltaEntries(deltaState);
  if (totalCount === 0) {
    return;
  }
  const payload = buildCompanionDeltaPayload(bundleState, deltaState);
  const baseStem = String(bundleState.sourceName ?? "campaign")
    .replace(/\.zip$/iu, "")
    .replace(/[^a-zA-Z0-9_-]+/gu, "-")
    .replace(/^-+|-+$/gu, "") || "campaign";
  const filename = `${baseStem}-companion-delta.json`;
  const blob = new Blob([JSON.stringify(payload, null, 2)], {
    type: "application/json;charset=utf-8",
  });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
  setStatus(t("status_delta_exported", { name: filename, count: totalCount }));
}

playerModeBtn.addEventListener("click", showPlayerMode);
exportDeltaBtn.addEventListener("click", triggerDeltaDownload);
resetDeltaBtn.addEventListener("click", () => {
  if (!bundleState) {
    return;
  }
  deltaState = createEmptyCompanionDelta(bundleState);
  clearDeltaSnapshot();
  renderBundle(bundleState);
  if (!playerOverlay.classList.contains("hidden") && activePlayerView) {
    if (activePlayerView.mode === "card") {
      renderPlayerCard(activePlayerView.sessionId, activePlayerView.characterId);
    } else {
      renderPlayerPicker(bundleState);
    }
  }
  setStatus(t("status_delta_reset"));
});

playerOverlay.addEventListener("click", (event) => {
  if (event.target === playerOverlay) {
    hidePlayerMode();
  }
});

document.addEventListener("keydown", (event) => {
  if (playerOverlay.classList.contains("hidden")) {
    return;
  }
  if (event.key === "Escape") {
    event.preventDefault();
    hidePlayerMode();
    return;
  }
  if (event.key === "Tab") {
    const focusables = Array.from(
      playerOverlay.querySelectorAll(
        'button:not([disabled]):not(.hidden), input:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])'
      )
    );
    if (!focusables.length) {
      return;
    }
    const first = focusables[0];
    const last = focusables[focusables.length - 1];
    const active = document.activeElement;
    if (event.shiftKey) {
      if (active === first || !playerOverlay.contains(active)) {
        event.preventDefault();
        last.focus();
      }
    } else if (active === last || !playerOverlay.contains(active)) {
      event.preventDefault();
      first.focus();
    }
  }
});

function applyBundle(bundle, restoredDelta = null) {
  bundleState = bundle;
  deltaState = restoredDelta ?? restoreDeltaSnapshot(bundle);
  renderBundle(bundleState);
  playerModeRow.classList.remove("hidden");
  hidePlayerMode();
  renderInstallHints();
}

async function handleFile(file) {
  const previousBundle = bundleState;
  const previousDelta = deltaState;
  try {
    setStatus(`${t("status_reading")} (${file.name})`);
    const loadedBundle = await loadBundleFromFile(file);
    applyBundle(loadedBundle);
    const persisted = saveBundleSnapshot(bundleState);
    setStatus(
      persisted
        ? t("status_success", {
            name: file.name,
            worlds: loadedBundle.summary.worldCount,
            sessions: loadedBundle.summary.sessionCount,
          })
        : t("status_loaded_unpersisted", { name: file.name }),
      !persisted
    );
  } catch (error) {
    if (previousBundle) {
      applyBundle(previousBundle, previousDelta);
      setStatus(
        t("status_error", { error: error instanceof Error ? error.message : String(error) }),
        true
      );
    } else {
      bundleState = null;
      deltaState = createEmptyCompanionDelta();
      renderEmpty();
      playerModeRow.classList.add("hidden");
      hidePlayerMode();
      renderInstallHints();
      setStatus(t("status_error", { error: error instanceof Error ? error.message : String(error) }), true);
    }
  }
}

fileInput.addEventListener("change", async (event) => {
  const [file] = event.target.files ?? [];
  if (file) {
    await handleFile(file);
    fileInput.value = "";
  }
});

["dragenter", "dragover"].forEach((eventName) => {
  dropzone.addEventListener(eventName, (event) => {
    event.preventDefault();
    dropzone.classList.add("is-dragover");
  });
});

["dragleave", "drop"].forEach((eventName) => {
  dropzone.addEventListener(eventName, (event) => {
    event.preventDefault();
    dropzone.classList.remove("is-dragover");
  });
});

dropzone.addEventListener("drop", async (event) => {
  const [file] = event.dataTransfer?.files ?? [];
  if (file) {
    await handleFile(file);
    fileInput.value = "";
  }
});

clearButton.addEventListener("click", () => {
  bundleState = null;
  deltaState = createEmptyCompanionDelta();
  clearBundleSnapshot();
  clearDeltaSnapshot();
  fileInput.value = "";
  renderEmpty();
  playerModeRow.classList.add("hidden");
  hidePlayerMode();
  renderInstallHints();
  setStatus(t("status_cleared"));
});

function updateActiveLangBtn() {
  const active = getLocale();
  document.querySelectorAll(".lang-btn").forEach((btn) => {
    const isActive = btn.dataset.lang === active;
    btn.classList.toggle("active", isActive);
    btn.setAttribute("aria-pressed", isActive ? "true" : "false");
  });
}

function applyLocale(newLocale) {
  const loc = setLocale(newLocale);
  updateActiveLangBtn();
  translateDocument(document, loc);
  syncToolbarButtons();
  renderInstallHints();
  if (bundleState) {
    renderBundle(bundleState);
    if (!playerOverlay.classList.contains("hidden") && activePlayerView) {
      if (activePlayerView.mode === "card") {
        renderPlayerCard(activePlayerView.sessionId, activePlayerView.characterId);
      } else {
        renderPlayerPicker(bundleState);
      }
    }
  } else {
    renderEmpty();
  }
}

document.querySelectorAll(".lang-btn").forEach((btn) => {
  btn.addEventListener("click", () => {
    const lang = btn.dataset.lang;
    if (lang) {
      applyLocale(lang);
    }
  });
});

if ("serviceWorker" in navigator) {
  window.addEventListener("load", () => {
    navigator.serviceWorker.register("./sw.js").catch(() => {
      // offline cache error
    });
  });
}

window.addEventListener("online", renderInstallHints);
window.addEventListener("offline", renderInstallHints);

// Initial locale setup
const initialLocale = detectLocale();
setLocale(initialLocale);
updateActiveLangBtn();
translateDocument(document, initialLocale);
syncToolbarButtons();
renderEmpty();
renderInstallHints();

const restoredBundle = restoreBundleSnapshot();
if (restoredBundle) {
  applyBundle(restoredBundle);
  setStatus(
    t("status_success", {
      name: restoredBundle.sourceName ?? t("meta_unknown"),
      worlds: restoredBundle.summary.worldCount,
      sessions: restoredBundle.summary.sessionCount,
    })
  );
}
