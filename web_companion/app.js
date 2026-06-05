import { loadBundleFromFile } from "./library.js";

const fileInput = document.querySelector("#bundle-file");
const dropzone = document.querySelector(".dropzone");
const clearButton = document.querySelector("#clear-button");
const statusNode = document.querySelector("#status");
const summaryNode = document.querySelector("#summary");
const worldsNode = document.querySelector("#worlds");
const sessionsNode = document.querySelector("#sessions");
const rulesetsNode = document.querySelector("#rulesets");
const mediaNode = document.querySelector("#media");

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

async function handleFile(file) {
  try {
    setStatus(`Lade ${file.name} …`);
    bundleState = await loadBundleFromFile(file);
    renderBundle(bundleState);
    setStatus(`Bundle ${file.name} erfolgreich geladen.`);
  } catch (error) {
    bundleState = null;
    renderEmpty();
    setStatus(error instanceof Error ? error.message : "Bundle konnte nicht geladen werden.", true);
  }
}

fileInput.addEventListener("change", async (event) => {
  const [file] = event.target.files ?? [];
  if (file) {
    await handleFile(file);
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
  fileInput.value = "";
  renderEmpty();
  setStatus("Ansicht geleert.");
});

if ("serviceWorker" in navigator) {
  window.addEventListener("load", () => {
    navigator.serviceWorker.register("./sw.js").catch(() => {
      setStatus("Bundle-Import läuft, aber der Offline-Cache konnte nicht registriert werden.", true);
    });
  });
}

renderEmpty();
