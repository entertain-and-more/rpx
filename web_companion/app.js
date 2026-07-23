import { loadBundleFromFile, getCharacterList, getPlayerView } from "./library.js";
import { t, setLocale, getLocale, getDateLocale, hydrateI18n } from "./i18n.mjs";

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
playerModeRow.innerHTML = `<button class="ghost" id="player-mode-btn">${escapeHtml(t("import.playerMode"))}</button>`;
statusNode.after(playerModeRow);
const langSelect = document.querySelector("#lang-select");
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
      title: standalone ? t("hints.iosAppTitle") : t("hints.iosInstallTitle"),
      body: standalone ? t("hints.iosAppBody") : t("hints.iosInstallBody")
    });
  } else if (platform === "android") {
    hints.push({
      title: standalone ? t("hints.androidAppTitle") : t("hints.androidInstallTitle"),
      body: standalone ? t("hints.androidAppBody") : t("hints.androidInstallBody")
    });
  } else {
    hints.push({
      title: t("hints.desktopTitle"),
      body: t("hints.desktopBody")
    });
  }

  hints.push({
    title: navigator.onLine ? t("hints.offlineReadyTitle") : t("hints.offlineActiveTitle"),
    body: navigator.onLine ? t("hints.offlineReadyBody") : t("hints.offlineActiveBody")
  });

  if (!bundleState) {
    hints.push({
      title: t("hints.firstStepTitle"),
      body: t("hints.firstStepBody")
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
  summaryNode.innerHTML = `<p>${escapeHtml(t("summary.empty"))}</p>`;
  worldsNode.className = "card-grid empty-state";
  worldsNode.innerHTML = `<p>${escapeHtml(t("worlds.empty"))}</p>`;
  sessionsNode.className = "stack empty-state";
  sessionsNode.innerHTML = `<p>${escapeHtml(t("sessions.empty"))}</p>`;
  rulesetsNode.className = "stack empty-state";
  rulesetsNode.innerHTML = `<p>${escapeHtml(t("rulesets.empty"))}</p>`;
  mediaNode.className = "stack empty-state";
  mediaNode.innerHTML = `<p>${escapeHtml(t("media.empty"))}</p>`;
}

function formatTimestamp(value) {
  if (!Number.isFinite(value)) {
    return t("general.unknown");
  }
  return new Date(value * 1000).toLocaleString(getDateLocale(), {
    dateStyle: "medium",
    timeStyle: "short",
  });
}

function renderSummary(bundle) {
  const { manifest, summary, sourceName } = bundle;
  summaryNode.className = "summary-grid";
  summaryNode.innerHTML = `
    <article class="stat-card">
      <div class="label">${escapeHtml(t("summary.source"))}</div>
      <div class="value">${escapeHtml(sourceName)}</div>
    </article>
    <article class="stat-card">
      <div class="label">${escapeHtml(t("summary.worlds"))}</div>
      <div class="value">${summary.worldCount}</div>
    </article>
    <article class="stat-card">
      <div class="label">${escapeHtml(t("summary.sessions"))}</div>
      <div class="value">${summary.sessionCount}</div>
    </article>
    <article class="stat-card">
      <div class="label">${escapeHtml(t("summary.characters"))}</div>
      <div class="value">${summary.characterCount}</div>
    </article>
    <article class="stat-card">
      <div class="label">${escapeHtml(t("summary.activeMissions"))}</div>
      <div class="value">${summary.activeMissionCount}</div>
    </article>
    <article class="stat-card">
      <div class="label">${escapeHtml(t("summary.mediaMode"))}</div>
      <div class="value">${escapeHtml(manifest.media_mode ?? "none")}</div>
    </article>
    <article class="stat-card">
      <div class="label">${escapeHtml(t("summary.exported"))}</div>
      <div class="value">${escapeHtml(formatTimestamp(manifest.exported_at))}</div>
    </article>
    <article class="stat-card">
      <div class="label">${escapeHtml(t("summary.schema"))}</div>
      <div class="value">${escapeHtml(manifest.app?.schema_version ?? "–")}</div>
    </article>
  `;
}

function renderWorlds(bundle) {
  if (!bundle.worlds.length) {
    worldsNode.className = "card-grid empty-state";
    worldsNode.innerHTML = `<p>${escapeHtml(t("worlds.emptyBundle"))}</p>`;
    return;
  }

  worldsNode.className = "card-grid";
  worldsNode.innerHTML = bundle.worlds.map((world) => `
    <article class="detail-card">
      <h3>${escapeHtml(world.name)}</h3>
      <p>${escapeHtml(world.genre)}</p>
      <ul class="meta-list">
        <li><span>${escapeHtml(t("worlds.maps"))}</span><strong>${world.mapCount}</strong></li>
        <li><span>${escapeHtml(t("worlds.locations"))}</span><strong>${world.locationCount}</strong></li>
        <li><span>${escapeHtml(t("worlds.mainMap"))}</span><strong>${escapeHtml(world.mapImage ?? t("worlds.noMap"))}</strong></li>
      </ul>
      <div class="pill-row">
        ${world.featuredLocations.length
          ? world.featuredLocations.map((location) => `<span class="pill">${escapeHtml(location)}</span>`).join("")
          : `<span class="pill">${escapeHtml(t("worlds.noFeatured"))}</span>`}
      </div>
    </article>
  `).join("");
}

function renderCharacters(characters) {
  if (!characters.length) {
    return `<p class="meta-note">${escapeHtml(t("sessions.noCharacters"))}</p>`;
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
    return `<p class="meta-note">${escapeHtml(t("sessions.noActiveMissions"))} ${session.completedMissionCount}</p>`;
  }
  return `
    <div class="pill-row">
      ${session.activeMissions.map((mission) => `<span class="pill">${escapeHtml(mission.name)}</span>`).join("")}
    </div>
    <p class="meta-note">${escapeHtml(t("sessions.completed"))} ${session.completedMissionCount}</p>
  `;
}

function renderChat(chat) {
  if (!chat.length) {
    return `<p class="meta-note">${escapeHtml(t("sessions.noChat"))}</p>`;
  }
  return chat.map((message) => `
    <div class="chat-line">
      <div class="chat-meta">
        ${escapeHtml(message.role ?? "system")} · ${escapeHtml(message.author ?? t("general.unknown"))}
      </div>
      <div class="chat-content">${escapeHtml(message.content ?? "")}</div>
    </div>
  `).join("");
}

function renderSessions(bundle) {
  if (!bundle.sessions.length) {
    sessionsNode.className = "stack empty-state";
    sessionsNode.innerHTML = `<p>${escapeHtml(t("sessions.emptyBundle"))}</p>`;
    return;
  }

  sessionsNode.className = "stack";
  sessionsNode.innerHTML = bundle.sessions.map((session) => `
    <article class="detail-card">
      <h3>${escapeHtml(session.name)}</h3>
      <p class="session-world">${escapeHtml(session.worldName)}</p>
      <div class="session-layout">
        <section class="subpanel">
          <h4>${escapeHtml(t("sessions.characterStatus"))}</h4>
          ${renderCharacters(session.characters)}
        </section>
        <section class="subpanel">
          <h4>${escapeHtml(t("sessions.missions"))}</h4>
          ${renderMissions(session)}
        </section>
        <section class="subpanel">
          <h4>${escapeHtml(t("sessions.lastChat"))}</h4>
          ${renderChat(session.chat)}
        </section>
      </div>
    </article>
  `).join("");
}

function renderRulesets(bundle) {
  if (!bundle.rulesets.length) {
    rulesetsNode.className = "stack empty-state";
    rulesetsNode.innerHTML = `<p>${escapeHtml(t("rulesets.emptyBundle"))}</p>`;
    return;
  }

  rulesetsNode.className = "stack";
  rulesetsNode.innerHTML = bundle.rulesets.map((ruleset) => `
    <article class="ruleset-card">
      <h3>${escapeHtml(ruleset.name)}</h3>
      <ul class="meta-list">
        <li><span>${escapeHtml(t("rulesets.weapons"))}</span><strong>${ruleset.weaponCount}</strong></li>
        <li><span>${escapeHtml(t("rulesets.spells"))}</span><strong>${ruleset.spellCount}</strong></li>
        <li><span>${escapeHtml(t("rulesets.file"))}</span><strong>${escapeHtml(ruleset.file)}</strong></li>
      </ul>
    </article>
  `).join("");
}

function renderMedia(bundle) {
  if (!bundle.mediaEntries.length) {
    mediaNode.className = "stack empty-state";
    mediaNode.innerHTML = `<p>${escapeHtml(t("media.emptyBundle"))}</p>`;
    return;
  }

  mediaNode.className = "stack";
  mediaNode.innerHTML = bundle.mediaEntries.slice(0, 18).map((entry) => `
    <article class="media-card">
      <strong>${escapeHtml(entry.kind ?? t("media.defaultKind"))}</strong>
      <div class="media-path">${escapeHtml(entry.bundle_path ?? t("media.noPath"))}</div>
      <div class="meta-note">
        ${escapeHtml(t("media.source"))} ${escapeHtml(entry.original_path ?? "–")}
        · ${escapeHtml(t("media.exists"))} ${entry.exists ? escapeHtml(t("general.yes")) : escapeHtml(t("general.no"))}
        · ${escapeHtml(t("media.included"))} ${entry.included ? escapeHtml(t("general.yes")) : escapeHtml(t("general.no"))}
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
      <h3>${escapeHtml(t("player.activeMissions"))}</h3>
      ${activeMissions.length
        ? `<div class="pill-row">${activeMissions.map((mission) => `<span class="pill">${escapeHtml(mission.name)}</span>`).join("")}</div>`
        : `<p class="meta-note">${escapeHtml(t("player.noActiveMissions"))}</p>`}
      <div class="button-row"><button class="ghost" id="player-pick">${escapeHtml(t("player.pick"))}</button></div>
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
        <p class="meta-note">${escapeHtml(t("player.noCharacters"))}</p>
        <div class="button-row"><button class="ghost" id="player-back">${escapeHtml(t("player.back"))}</button></div>
      </div>
    `;
    playerOverlay.querySelector("#player-back").addEventListener("click", hidePlayerMode);
    return;
  }

  playerOverlay.innerHTML = `
    <div class="player-card">
      <h2>${escapeHtml(t("player.modeTitle"))}</h2>
      <p class="meta-note">${escapeHtml(t("player.pickPrompt"))}</p>
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
      <div class="button-row"><button class="ghost" id="player-back">${escapeHtml(t("player.back"))}</button></div>
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
    setStatus(t("status.loading", { name: file.name }));
    const loadedBundle = await loadBundleFromFile(file);
    applyBundle(loadedBundle);
    const persisted = saveBundleSnapshot(bundleState);
    setStatus(
      persisted
        ? t("status.loadedPersisted", { name: file.name })
        : t("status.loadedNoPersist", { name: file.name }),
      !persisted
    );
  } catch (error) {
    const message = error instanceof Error ? error.message : t("status.loadFailed");
    if (previousBundle) {
      applyBundle(previousBundle);
      setStatus(t("status.previousKept", { error: message }), true);
    } else {
      bundleState = null;
      renderEmpty();
      playerModeRow.classList.add("hidden");
      hidePlayerMode();
      renderInstallHints();
      setStatus(message, true);
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
  setStatus(t("status.cleared"));
});

if ("serviceWorker" in navigator) {
  window.addEventListener("load", () => {
    navigator.serviceWorker.register("./sw.js").catch(() => {
      setStatus(t("status.swFailed"), true);
    });
  });
}

window.addEventListener("online", renderInstallHints);
window.addEventListener("offline", renderInstallHints);

function applyLocale() {
  hydrateI18n();
  playerModeRow.querySelector("#player-mode-btn").textContent = t("import.playerMode");
  renderInstallHints();
  if (bundleState) {
    renderBundle(bundleState);
  } else {
    renderEmpty();
  }
}

if (langSelect) {
  langSelect.value = getLocale();
  langSelect.addEventListener("change", () => {
    setLocale(langSelect.value);
    applyLocale();
  });
}

hydrateI18n();
renderEmpty();
renderInstallHints();

const restoredBundle = restoreBundleSnapshot();
if (restoredBundle) {
  applyBundle(restoredBundle);
  setStatus(t("status.restored", { name: restoredBundle.sourceName ?? t("general.unknown") }));
}
