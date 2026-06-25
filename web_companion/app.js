import { loadBundleFromFile, getCharacterList, getPlayerView } from "./library.js";

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
playerModeRow.innerHTML = '<button class="ghost" id="player-mode-btn">Spieler-Modus</button>';
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
      title: standalone ? "iPhone/iPad als App" : "iPhone/iPad installieren",
      body: standalone
        ? "Die PWA läuft im Standalone-Modus. Zuletzt geladene Bundles werden lokal für Offline-Starts wiederhergestellt."
        : "Über Teilen → Zum Home-Bildschirm kann der Companion ohne Safari-Chrome gestartet werden."
    });
  } else if (platform === "android") {
    hints.push({
      title: standalone ? "Android-App aktiv" : "Android installieren",
      body: standalone
        ? "Die PWA läuft installiert. Bundle-Stand und Offline-Shell bleiben lokal auf dem Gerät."
        : "Über Browser-Menü → App installieren oder Zum Startbildschirm hinzufügen wird der Companion zur App."
    });
  } else {
    hints.push({
      title: "Desktop- und Tablet-Companion",
      body: "Für mobile Prüfungen denselben Build als PWA auf Android oder iOS installieren; Desktop bleibt die GM-Hauptlinie."
    });
  }

  hints.push({
    title: navigator.onLine ? "Offline bereit" : "Offline aktiv",
    body: navigator.onLine
      ? "Nach dem ersten Öffnen hält der Service Worker die Shell-Dateien lokal vor. Der letzte geladene Bundle-Stand wird zusätzlich im Gerätespeicher gehalten."
      : "Die App läuft gerade offline. Wenn bereits ein Bundle geladen war, wird der zuletzt gespeicherte Stand lokal wiederhergestellt."
  });

  if (!bundleState) {
    hints.push({
      title: "Erster Testschritt",
      body: "Für Android-/iOS-Smokes zuerst ein kleines Kampagnen-Bundle importieren und danach den Offline-Neustart gegen den Testplan prüfen."
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
  summaryNode.innerHTML = "<p>Nach dem Import erscheinen hier Kampagnenmetadaten und Schnellzahlen.</p>";
  worldsNode.className = "card-grid empty-state";
  worldsNode.innerHTML = "<p>Noch keine Welten geladen.</p>";
  sessionsNode.className = "stack empty-state";
  sessionsNode.innerHTML = "<p>Noch keine Sessions geladen.</p>";
  rulesetsNode.className = "stack empty-state";
  rulesetsNode.innerHTML = "<p>Noch keine Regelwerke geladen.</p>";
  mediaNode.className = "stack empty-state";
  mediaNode.innerHTML = "<p>Noch keine Medienreferenzen geladen.</p>";
}

function formatTimestamp(value) {
  if (!Number.isFinite(value)) {
    return "Unbekannt";
  }
  return new Date(value * 1000).toLocaleString("de-DE", {
    dateStyle: "medium",
    timeStyle: "short",
  });
}

function renderSummary(bundle) {
  const { manifest, summary, sourceName } = bundle;
  summaryNode.className = "summary-grid";
  const rows = [
    ["Quelle", sourceName],
    ["Welten", summary.worldCount],
    ["Sessions", summary.sessionCount],
    ["Charaktere", summary.characterCount],
    ["Aktive Missionen", summary.activeMissionCount],
    ["Medienmodus", manifest.media_mode ?? "none"],
    ["Exportiert", formatTimestamp(manifest.exported_at)],
    ["Schema", manifest.app?.schema_version ?? "–"],
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
    renderEmptyMessage(worldsNode, "card-grid empty-state", "Im Bundle sind keine Welten eingetragen.");
    return;
  }

  worldsNode.className = "card-grid";
  worldsNode.replaceChildren(...bundle.worlds.map((world) => {
    const card = createNode("article", "detail-card");
    appendNode(card, "h3", "", world.name);
    appendNode(card, "p", "", world.genre);
    card.appendChild(createMetaList([
      ["Karten", world.mapCount],
      ["Orte", world.locationCount],
      ["Hauptkarte", world.mapImage ?? "Keine"],
    ]));
    card.appendChild(createPillRow(world.featuredLocations, "Keine markierten Orte"));
    return card;
  }));
}

function renderCharacters(parent, characters) {
  if (!characters.length) {
    parent.appendChild(createNode("p", "meta-note", "Keine Charaktere in dieser Session."));
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
      `HP ${character.health ?? "–"}/${character.maxHealth ?? "–"} · Mana ${character.mana ?? "–"}/${character.maxMana ?? "–"} · Gold ${character.gold ?? "–"}`
    );
    parent.appendChild(line);
  });
}

function renderMissions(parent, session) {
  if (!session.activeMissions.length) {
    parent.appendChild(
      createNode("p", "meta-note", `Keine aktiven Missionen. Abgeschlossen: ${session.completedMissionCount}`)
    );
    return;
  }
  parent.appendChild(createPillRow(session.activeMissions.map((mission) => mission.name), "Keine aktiven Missionen"));
  parent.appendChild(createNode("p", "meta-note", `Abgeschlossen: ${session.completedMissionCount}`));
}

function renderChat(parent, chat) {
  if (!chat.length) {
    parent.appendChild(createNode("p", "meta-note", "Kein Chat-Verlauf im Bundle."));
    return;
  }
  chat.forEach((message) => {
    const line = createNode("div", "chat-line");
    appendNode(line, "div", "chat-meta", `${message.role ?? "system"} · ${message.author ?? "Unbekannt"}`);
    appendNode(line, "div", "chat-content", message.content ?? "");
    parent.appendChild(line);
  });
}

function renderSessions(bundle) {
  if (!bundle.sessions.length) {
    renderEmptyMessage(sessionsNode, "stack empty-state", "Im Bundle sind keine Sessions eingetragen.");
    return;
  }

  sessionsNode.className = "stack";
  sessionsNode.replaceChildren(...bundle.sessions.map((session) => {
    const card = createNode("article", "detail-card");
    appendNode(card, "h3", "", session.name);
    appendNode(card, "p", "session-world", session.worldName);
    const layout = createNode("div", "session-layout");

    const charactersPanel = createNode("section", "subpanel");
    appendNode(charactersPanel, "h4", "", "Charakterstatus");
    renderCharacters(charactersPanel, session.characters);
    layout.appendChild(charactersPanel);

    const missionsPanel = createNode("section", "subpanel");
    appendNode(missionsPanel, "h4", "", "Missionen");
    renderMissions(missionsPanel, session);
    layout.appendChild(missionsPanel);

    const chatPanel = createNode("section", "subpanel");
    appendNode(chatPanel, "h4", "", "Letzte Chat-Zeilen");
    renderChat(chatPanel, session.chat);
    layout.appendChild(chatPanel);

    card.appendChild(layout);
    return card;
  }));
}

function renderRulesets(bundle) {
  if (!bundle.rulesets.length) {
    renderEmptyMessage(rulesetsNode, "stack empty-state", "Keine Regelwerke im Bundle gefunden.");
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
    renderEmptyMessage(mediaNode, "stack empty-state", "Keine Medienreferenzen im Bundle gefunden.");
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
        <li><span>HP</span><strong>${escapeHtml(character.health ?? "–")} / ${escapeHtml(character.maxHealth ?? "–")}</strong></li>
      </ul>
      ${renderStatBar(character.health, character.maxHealth, "hp")}
      <ul class="meta-list">
        <li><span>Mana</span><strong>${escapeHtml(character.mana ?? "–")} / ${escapeHtml(character.maxMana ?? "–")}</strong></li>
      </ul>
      ${renderStatBar(character.mana, character.maxMana, "mana")}
      <ul class="meta-list">
        <li><span>Gold</span><strong>${escapeHtml(character.gold ?? "–")}</strong></li>
      </ul>
      <h3>Aktive Missionen</h3>
      ${activeMissions.length
        ? `<div class="pill-row">${activeMissions.map((mission) => `<span class="pill">${escapeHtml(mission.name)}</span>`).join("")}</div>`
        : '<p class="meta-note">Keine aktiven Missionen.</p>'}
      <div class="button-row"><button class="ghost" id="player-pick">← Auswahl</button></div>
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
        <p class="meta-note">Keine Charaktere im Bundle.</p>
        <div class="button-row"><button class="ghost" id="player-back">← Zurück</button></div>
      </div>
    `;
    playerOverlay.querySelector("#player-back").addEventListener("click", hidePlayerMode);
    return;
  }

  playerOverlay.innerHTML = `
    <div class="player-card">
      <h2>Spieler-Modus</h2>
      <p class="meta-note">Wähle deinen Charakter:</p>
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
      <div class="button-row"><button class="ghost" id="player-back">← Zurück</button></div>
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
    setStatus(`Lade ${file.name} …`);
    const loadedBundle = await loadBundleFromFile(file);
    applyBundle(loadedBundle);
    const persisted = saveBundleSnapshot(bundleState);
    setStatus(
      persisted
        ? `Bundle ${file.name} erfolgreich geladen. Offline-Wiedereinstieg ist vorbereitet.`
        : `Bundle ${file.name} erfolgreich geladen. Die lokale Wiederherstellung konnte auf diesem Gerät nicht gespeichert werden.`,
      !persisted
    );
  } catch (error) {
    if (previousBundle) {
      applyBundle(previousBundle);
      setStatus(
        `${error instanceof Error ? error.message : "Bundle konnte nicht geladen werden."} Das vorherige Bundle bleibt sichtbar.`,
        true
      );
    } else {
      bundleState = null;
      renderEmpty();
      playerModeRow.classList.add("hidden");
      hidePlayerMode();
      renderInstallHints();
      setStatus(error instanceof Error ? error.message : "Bundle konnte nicht geladen werden.", true);
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
  setStatus("Ansicht geleert. Lokaler Bundle-Stand wurde entfernt.");
});

if ("serviceWorker" in navigator) {
  window.addEventListener("load", () => {
    navigator.serviceWorker.register("./sw.js").catch(() => {
      setStatus("Bundle-Import läuft, aber der Offline-Cache konnte nicht registriert werden.", true);
    });
  });
}

window.addEventListener("online", renderInstallHints);
window.addEventListener("offline", renderInstallHints);

renderEmpty();
renderInstallHints();

const restoredBundle = restoreBundleSnapshot();
if (restoredBundle) {
  applyBundle(restoredBundle);
  setStatus(
    `Zuletzt geladenes Bundle ${restoredBundle.sourceName ?? "Unbekannt"} wurde lokal für den Offline-Start wiederhergestellt.`
  );
}
