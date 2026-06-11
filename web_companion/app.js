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
  summaryNode.innerHTML = `
    <article class="stat-card">
      <div class="label">Quelle</div>
      <div class="value">${escapeHtml(sourceName)}</div>
    </article>
    <article class="stat-card">
      <div class="label">Welten</div>
      <div class="value">${summary.worldCount}</div>
    </article>
    <article class="stat-card">
      <div class="label">Sessions</div>
      <div class="value">${summary.sessionCount}</div>
    </article>
    <article class="stat-card">
      <div class="label">Charaktere</div>
      <div class="value">${summary.characterCount}</div>
    </article>
    <article class="stat-card">
      <div class="label">Aktive Missionen</div>
      <div class="value">${summary.activeMissionCount}</div>
    </article>
    <article class="stat-card">
      <div class="label">Medienmodus</div>
      <div class="value">${escapeHtml(manifest.media_mode ?? "none")}</div>
    </article>
    <article class="stat-card">
      <div class="label">Exportiert</div>
      <div class="value">${escapeHtml(formatTimestamp(manifest.exported_at))}</div>
    </article>
    <article class="stat-card">
      <div class="label">Schema</div>
      <div class="value">${escapeHtml(manifest.app?.schema_version ?? "–")}</div>
    </article>
  `;
}

function renderWorlds(bundle) {
  if (!bundle.worlds.length) {
    worldsNode.className = "card-grid empty-state";
    worldsNode.innerHTML = "<p>Im Bundle sind keine Welten eingetragen.</p>";
    return;
  }

  worldsNode.className = "card-grid";
  worldsNode.innerHTML = bundle.worlds.map((world) => `
    <article class="detail-card">
      <h3>${escapeHtml(world.name)}</h3>
      <p>${escapeHtml(world.genre)}</p>
      <ul class="meta-list">
        <li><span>Karten</span><strong>${world.mapCount}</strong></li>
        <li><span>Orte</span><strong>${world.locationCount}</strong></li>
        <li><span>Hauptkarte</span><strong>${escapeHtml(world.mapImage ?? "Keine")}</strong></li>
      </ul>
      <div class="pill-row">
        ${world.featuredLocations.length
          ? world.featuredLocations.map((location) => `<span class="pill">${escapeHtml(location)}</span>`).join("")
          : '<span class="pill">Keine markierten Orte</span>'}
      </div>
    </article>
  `).join("");
}

function renderCharacters(characters) {
  if (!characters.length) {
    return "<p class=\"meta-note\">Keine Charaktere in dieser Session.</p>";
  }
  return characters.map((character) => `
    <div class="chat-line">
      <div><strong>${escapeHtml(character.name)}</strong></div>
      <div class="meta-note">
        HP ${escapeHtml(character.health ?? "–")}/${escapeHtml(character.maxHealth ?? "–")}
        · Mana ${escapeHtml(character.mana ?? "–")}/${escapeHtml(character.maxMana ?? "–")}
        · Gold ${escapeHtml(character.gold ?? "–")}
      </div>
    </div>
  `).join("");
}

function renderMissions(session) {
  if (!session.activeMissions.length) {
    return `<p class="meta-note">Keine aktiven Missionen. Abgeschlossen: ${session.completedMissionCount}</p>`;
  }
  return `
    <div class="pill-row">
      ${session.activeMissions.map((mission) => `<span class="pill">${escapeHtml(mission.name)}</span>`).join("")}
    </div>
    <p class="meta-note">Abgeschlossen: ${session.completedMissionCount}</p>
  `;
}

function renderChat(chat) {
  if (!chat.length) {
    return "<p class=\"meta-note\">Kein Chat-Verlauf im Bundle.</p>";
  }
  return chat.map((message) => `
    <div class="chat-line">
      <div class="chat-meta">
        ${escapeHtml(message.role ?? "system")} · ${escapeHtml(message.author ?? "Unbekannt")}
      </div>
      <div class="chat-content">${escapeHtml(message.content ?? "")}</div>
    </div>
  `).join("");
}

function renderSessions(bundle) {
  if (!bundle.sessions.length) {
    sessionsNode.className = "stack empty-state";
    sessionsNode.innerHTML = "<p>Im Bundle sind keine Sessions eingetragen.</p>";
    return;
  }

  sessionsNode.className = "stack";
  sessionsNode.innerHTML = bundle.sessions.map((session) => `
    <article class="detail-card">
      <h3>${escapeHtml(session.name)}</h3>
      <p class="session-world">${escapeHtml(session.worldName)}</p>
      <div class="session-layout">
        <section class="subpanel">
          <h4>Charakterstatus</h4>
          ${renderCharacters(session.characters)}
        </section>
        <section class="subpanel">
          <h4>Missionen</h4>
          ${renderMissions(session)}
        </section>
        <section class="subpanel">
          <h4>Letzte Chat-Zeilen</h4>
          ${renderChat(session.chat)}
        </section>
      </div>
    </article>
  `).join("");
}

function renderRulesets(bundle) {
  if (!bundle.rulesets.length) {
    rulesetsNode.className = "stack empty-state";
    rulesetsNode.innerHTML = "<p>Keine Regelwerke im Bundle gefunden.</p>";
    return;
  }

  rulesetsNode.className = "stack";
  rulesetsNode.innerHTML = bundle.rulesets.map((ruleset) => `
    <article class="ruleset-card">
      <h3>${escapeHtml(ruleset.name)}</h3>
      <ul class="meta-list">
        <li><span>Waffen</span><strong>${ruleset.weaponCount}</strong></li>
        <li><span>Zauber</span><strong>${ruleset.spellCount}</strong></li>
        <li><span>Datei</span><strong>${escapeHtml(ruleset.file)}</strong></li>
      </ul>
    </article>
  `).join("");
}

function renderMedia(bundle) {
  if (!bundle.mediaEntries.length) {
    mediaNode.className = "stack empty-state";
    mediaNode.innerHTML = "<p>Keine Medienreferenzen im Bundle gefunden.</p>";
    return;
  }

  mediaNode.className = "stack";
  mediaNode.innerHTML = bundle.mediaEntries.slice(0, 18).map((entry) => `
    <article class="media-card">
      <strong>${escapeHtml(entry.kind ?? "datei")}</strong>
      <div class="media-path">${escapeHtml(entry.bundle_path ?? "ohne Pfad")}</div>
      <div class="meta-note">
        Quelle: ${escapeHtml(entry.original_path ?? "–")}
        · vorhanden: ${entry.exists ? "ja" : "nein"}
        · eingebettet: ${entry.included ? "ja" : "nein"}
      </div>
    </article>
  `).join("");
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
    fileInput.files = event.dataTransfer.files;
    await handleFile(file);
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
