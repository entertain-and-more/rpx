import { loadBundleFromFile, getCharacterList, getPlayerView } from "./library.js";
import {
  t,
  translateDocument,
  getLocale,
  setLocale,
  detectLocale,
  formatTimestamp,
  SUPPORTED_LOCALES,
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
document.body.appendChild(playerOverlay);

const playerModeRow = document.createElement("div");
playerModeRow.className = "button-row hidden";
playerModeRow.innerHTML = `<button class="ghost" id="player-mode-btn" data-i18n="action_player_mode">${t("action_player_mode")}</button>`;
statusNode.after(playerModeRow);
playerModeRow.querySelector("#player-mode-btn").addEventListener("click", showPlayerMode);

const STORAGE_KEY = "rpx-companion:last-bundle:v1";
let bundleState = null;

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
  if (/iphone|ipad|ipod/.test(userAgent)) {
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
    ["Medienmodus", manifest.media_mode ?? "none"],
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
      ["Orte", world.locationCount],
      ["Hauptkarte", world.mapImage ?? t("meta_unknown")],
    ]));
    card.appendChild(createPillRow(world.featuredLocations, "–"));
    return card;
  }));
}

function renderCharacters(parent, characters) {
  if (!characters.length) {
    parent.appendChild(createNode("p", "meta-note", "–"));
    return;
  }
  characters.forEach((character) => {
    const line = createNode("div", "chat-line");
    const nameRow = createNode("div");
    appendNode(nameRow, "strong", "", character.name);
    line.appendChild(nameRow);
    appendNode(
      line,
      "div",
      "meta-note",
      `${t("player_overlay_hp")} ${character.health ?? "–"}/${character.maxHealth ?? "–"} · ${t("player_overlay_mana")} ${character.mana ?? "–"}/${character.maxMana ?? "–"} · Gold ${character.gold ?? "–"}`
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
  parent.appendChild(createNode("p", "meta-note", `Abgeschlossen: ${session.completedMissionCount}`));
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
    renderCharacters(charactersPanel, session.characters);
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
      ["Waffen", ruleset.weaponCount],
      ["Zauber", ruleset.spellCount],
      ["Datei", ruleset.file],
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
    appendNode(card, "strong", "", entry.kind ?? "datei");
    appendNode(card, "div", "media-path", entry.bundle_path ?? "ohne Pfad");
    appendNode(
      card,
      "div",
      "meta-note",
      `Quelle: ${entry.original_path ?? "–"} · vorhanden: ${entry.exists ? "ja" : "nein"} · eingebettet: ${entry.included ? "ja" : "nein"}`
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
}

function renderStatBar(current, max, cssClass) {
  const pct = max > 0 && current != null ? Math.round((current / max) * 100) : 0;
  return `<div class="stat-bar"><div class="stat-bar-fill ${escapeHtml(cssClass)}" style="width:${pct}%"></div></div>`;
}

function renderPlayerCard(view) {
  const { character, activeMissions } = view;
  playerOverlay.innerHTML = `
    <div class="player-card">
      <h2>${escapeHtml(character.name)}</h2>
      <ul class="meta-list">
        <li><span>${t("player_overlay_hp")}</span><strong>${escapeHtml(character.health ?? "–")} / ${escapeHtml(character.maxHealth ?? "–")}</strong></li>
      </ul>
      ${renderStatBar(character.health, character.maxHealth, "hp")}
      <ul class="meta-list">
        <li><span>${t("player_overlay_mana")}</span><strong>${escapeHtml(character.mana ?? "–")} / ${escapeHtml(character.maxMana ?? "–")}</strong></li>
      </ul>
      ${renderStatBar(character.mana, character.maxMana, "mana")}
      <ul class="meta-list">
        <li><span>Gold</span><strong>${escapeHtml(character.gold ?? "–")}</strong></li>
      </ul>
      <h3>${escapeHtml(t("player_overlay_missions"))}</h3>
      ${activeMissions.length
        ? `<div class="pill-row">${activeMissions.map((mission) => `<span class="pill">${escapeHtml(mission.name)}</span>`).join("")}</div>`
        : `<p class="meta-note">${escapeHtml(t("player_overlay_no_missions"))}</p>`}
      <div class="button-row"><button class="ghost" id="player-pick">← ${escapeHtml(t("player_overlay_select"))}</button></div>
    </div>
  `;
  playerOverlay.querySelector("#player-pick").addEventListener("click", () => {
    renderPlayerPicker(bundleState);
  });
}

function renderPlayerPicker(bundle) {
  const characters = getCharacterList(bundle);
  if (!characters.length) {
    playerOverlay.innerHTML = `
      <div class="player-card">
        <p class="meta-note">${escapeHtml(t("player_overlay_no_chat"))}</p>
        <div class="button-row"><button class="ghost" id="player-back">← ${escapeHtml(t("player_overlay_close"))}</button></div>
      </div>
    `;
    playerOverlay.querySelector("#player-back").addEventListener("click", hidePlayerMode);
    return;
  }

  playerOverlay.innerHTML = `
    <div class="player-card">
      <h2>${escapeHtml(t("player_overlay_title"))}</h2>
      <p class="meta-note">${escapeHtml(t("player_overlay_select"))}:</p>
      <ul class="character-list">
        ${characters.map((character) => `
          <li class="character-item"
              data-session="${escapeHtml(character.sessionId)}"
              data-character="${escapeHtml(character.characterId)}">
            <strong>${escapeHtml(character.characterName)}</strong>
            <span class="meta-note">${escapeHtml(character.sessionName)}</span>
          </li>
        `).join("")}
      </ul>
      <div class="button-row"><button class="ghost" id="player-back">← ${escapeHtml(t("player_overlay_close"))}</button></div>
    </div>
  `;

  playerOverlay.querySelectorAll(".character-item").forEach((item) => {
    item.addEventListener("click", () => {
      const view = getPlayerView(bundle, item.dataset.session, item.dataset.character);
      renderPlayerCard(view);
    });
  });
  playerOverlay.querySelector("#player-back").addEventListener("click", hidePlayerMode);
}

function showPlayerMode() {
  playerOverlay.classList.remove("hidden");
  renderPlayerPicker(bundleState);
}

function hidePlayerMode() {
  playerOverlay.classList.add("hidden");
}

function applyBundle(bundle) {
  bundleState = bundle;
  renderBundle(bundleState);
  playerModeRow.classList.remove("hidden");
  hidePlayerMode();
  renderInstallHints();
}

async function handleFile(file) {
  const previousBundle = bundleState;
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
        : `${file.name} geladen.`,
      !persisted
    );
  } catch (error) {
    if (previousBundle) {
      applyBundle(previousBundle);
      setStatus(
        t("status_error", { error: error instanceof Error ? error.message : String(error) }),
        true
      );
    } else {
      bundleState = null;
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
  clearBundleSnapshot();
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
    btn.classList.toggle("active", btn.dataset.lang === active);
  });
}

function applyLocale(newLocale) {
  const loc = setLocale(newLocale);
  updateActiveLangBtn();
  translateDocument(document, loc);
  const playerBtn = document.querySelector("#player-mode-btn");
  if (playerBtn) {
    playerBtn.textContent = t("action_player_mode");
  }
  renderInstallHints();
  if (bundleState) {
    renderBundle(bundleState);
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
