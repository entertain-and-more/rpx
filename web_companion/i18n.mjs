const LOCALE_KEY = "rpg-companion-locale";

export const catalogs = {
  de: {
    "hero.eyebrow": "Offline Web/PWA Companion",
    "hero.title": "RPX Pro Companion",
    "hero.lead":
      'Liest lokale <code>rpx-campaign-bundle-v1</code>-ZIPs für Kampagnenübersicht, Charakterstatus, Missionen, Karten- und Medienhinweise.',

    "import.title": "Bundle laden",
    "import.description": "Die App arbeitet lokal im Browser. Es werden keine Daten hochgeladen.",
    "import.dropTitle": "ZIP auswählen oder hier ablegen",
    "import.dropCopy": 'Erwartet wird ein Export im Format <code>rpx-campaign-bundle-v1</code>.',
    "import.clear": "Ansicht leeren",
    "import.playerMode": "Spieler-Modus",

    "summary.title": "Kampagnenstand",
    "summary.description": "Direkt aus dem Bundle extrahiert.",
    "summary.empty": "Nach dem Import erscheinen hier Kampagnenmetadaten und Schnellzahlen.",
    "summary.source": "Quelle",
    "summary.worlds": "Welten",
    "summary.sessions": "Sessions",
    "summary.characters": "Charaktere",
    "summary.activeMissions": "Aktive Missionen",
    "summary.mediaMode": "Medienmodus",
    "summary.exported": "Exportiert",
    "summary.schema": "Schema",

    "worlds.title": "Welten",
    "worlds.description": "Kerninfos zu Welten, Orten und Karten.",
    "worlds.empty": "Noch keine Welten geladen.",
    "worlds.emptyBundle": "Im Bundle sind keine Welten eingetragen.",
    "worlds.maps": "Karten",
    "worlds.locations": "Orte",
    "worlds.mainMap": "Hauptkarte",
    "worlds.noMap": "Keine",
    "worlds.noFeatured": "Keine markierten Orte",

    "sessions.title": "Sessions",
    "sessions.description": "Charaktere, Missionen und letzte Chat-Einträge.",
    "sessions.empty": "Noch keine Sessions geladen.",
    "sessions.emptyBundle": "Im Bundle sind keine Sessions eingetragen.",
    "sessions.characterStatus": "Charakterstatus",
    "sessions.missions": "Missionen",
    "sessions.lastChat": "Letzte Chat-Zeilen",
    "sessions.noCharacters": "Keine Charaktere in dieser Session.",
    "sessions.noActiveMissions": "Keine aktiven Missionen. Abgeschlossen:",
    "sessions.completed": "Abgeschlossen:",
    "sessions.noChat": "Kein Chat-Verlauf im Bundle.",

    "rulesets.title": "Regelwerke",
    "rulesets.description": "Mitgelieferte JSON-Regelwerke aus dem Bundle.",
    "rulesets.empty": "Noch keine Regelwerke geladen.",
    "rulesets.emptyBundle": "Keine Regelwerke im Bundle gefunden.",
    "rulesets.weapons": "Waffen",
    "rulesets.spells": "Zauber",
    "rulesets.file": "Datei",

    "media.title": "Karten & Medien",
    "media.description": 'Referenzen aus <code>media/manifest.json</code>.',
    "media.empty": "Noch keine Medienreferenzen geladen.",
    "media.emptyBundle": "Keine Medienreferenzen im Bundle gefunden.",
    "media.defaultKind": "datei",
    "media.noPath": "ohne Pfad",
    "media.source": "Quelle:",
    "media.exists": "vorhanden:",
    "media.included": "eingebettet:",

    "player.modeTitle": "Spieler-Modus",
    "player.pickPrompt": "Wähle deinen Charakter:",
    "player.noCharacters": "Keine Charaktere im Bundle.",
    "player.activeMissions": "Aktive Missionen",
    "player.noActiveMissions": "Keine aktiven Missionen.",
    "player.back": "← Zurück",
    "player.pick": "← Auswahl",

    "status.noBundle": "Noch kein Bundle geladen.",
    "status.cleared": "Ansicht geleert. Lokaler Bundle-Stand wurde entfernt.",
    "status.swFailed": "Bundle-Import läuft, aber der Offline-Cache konnte nicht registriert werden.",
    "status.loadFailed": "Bundle konnte nicht geladen werden.",
    "status.loading": "Lade {name} …",
    "status.loadedPersisted": "Bundle {name} erfolgreich geladen. Offline-Wiedereinstieg ist vorbereitet.",
    "status.loadedNoPersist": "Bundle {name} erfolgreich geladen. Die lokale Wiederherstellung konnte auf diesem Gerät nicht gespeichert werden.",
    "status.previousKept": "{error} Das vorherige Bundle bleibt sichtbar.",
    "status.restored": "Zuletzt geladenes Bundle {name} wurde lokal für den Offline-Start wiederhergestellt.",

    "hints.iosAppTitle": "iPhone/iPad als App",
    "hints.iosInstallTitle": "iPhone/iPad installieren",
    "hints.iosAppBody":
      "Die PWA läuft im Standalone-Modus. Zuletzt geladene Bundles werden lokal für Offline-Starts wiederhergestellt.",
    "hints.iosInstallBody":
      "Über Teilen → Zum Home-Bildschirm kann der Companion ohne Safari-Chrome gestartet werden.",
    "hints.androidAppTitle": "Android-App aktiv",
    "hints.androidInstallTitle": "Android installieren",
    "hints.androidAppBody":
      "Die PWA läuft installiert. Bundle-Stand und Offline-Shell bleiben lokal auf dem Gerät.",
    "hints.androidInstallBody":
      "Über Browser-Menü → App installieren oder Zum Startbildschirm hinzufügen wird der Companion zur App.",
    "hints.desktopTitle": "Desktop- und Tablet-Companion",
    "hints.desktopBody":
      "Für mobile Prüfungen denselben Build als PWA auf Android oder iOS installieren; Desktop bleibt die GM-Hauptlinie.",
    "hints.offlineReadyTitle": "Offline bereit",
    "hints.offlineActiveTitle": "Offline aktiv",
    "hints.offlineReadyBody":
      "Nach dem ersten Öffnen hält der Service Worker die Shell-Dateien lokal vor. Der letzte geladene Bundle-Stand wird zusätzlich im Gerätespeicher gehalten.",
    "hints.offlineActiveBody":
      "Die App läuft gerade offline. Wenn bereits ein Bundle geladen war, wird der zuletzt gespeicherte Stand lokal wiederhergestellt.",
    "hints.firstStepTitle": "Erster Testschritt",
    "hints.firstStepBody":
      "Für Android-/iOS-Smokes zuerst ein kleines Kampagnen-Bundle importieren und danach den Offline-Neustart gegen den Testplan prüfen.",

    "general.unknown": "Unbekannt",
    "general.yes": "ja",
    "general.no": "nein",
    "lang.label": "Sprache",
  },
  en: {
    "hero.eyebrow": "Offline Web/PWA Companion",
    "hero.title": "RPX Pro Companion",
    "hero.lead":
      'Reads local <code>rpx-campaign-bundle-v1</code> ZIPs for campaign overview, character status, missions, map and media references.',

    "import.title": "Load Bundle",
    "import.description": "The app works locally in the browser. No data is uploaded.",
    "import.dropTitle": "Select a ZIP or drop it here",
    "import.dropCopy": 'Expects an export in the <code>rpx-campaign-bundle-v1</code> format.',
    "import.clear": "Clear View",
    "import.playerMode": "Player Mode",

    "summary.title": "Campaign Status",
    "summary.description": "Extracted directly from the bundle.",
    "summary.empty": "Campaign metadata and quick figures appear here after import.",
    "summary.source": "Source",
    "summary.worlds": "Worlds",
    "summary.sessions": "Sessions",
    "summary.characters": "Characters",
    "summary.activeMissions": "Active Missions",
    "summary.mediaMode": "Media Mode",
    "summary.exported": "Exported",
    "summary.schema": "Schema",

    "worlds.title": "Worlds",
    "worlds.description": "Core info on worlds, locations and maps.",
    "worlds.empty": "No worlds loaded yet.",
    "worlds.emptyBundle": "No worlds are listed in the bundle.",
    "worlds.maps": "Maps",
    "worlds.locations": "Locations",
    "worlds.mainMap": "Main Map",
    "worlds.noMap": "None",
    "worlds.noFeatured": "No featured locations",

    "sessions.title": "Sessions",
    "sessions.description": "Characters, missions and latest chat entries.",
    "sessions.empty": "No sessions loaded yet.",
    "sessions.emptyBundle": "No sessions are listed in the bundle.",
    "sessions.characterStatus": "Character Status",
    "sessions.missions": "Missions",
    "sessions.lastChat": "Latest Chat Lines",
    "sessions.noCharacters": "No characters in this session.",
    "sessions.noActiveMissions": "No active missions. Completed:",
    "sessions.completed": "Completed:",
    "sessions.noChat": "No chat history in the bundle.",

    "rulesets.title": "Rule Sets",
    "rulesets.description": "Bundled JSON rule sets from the bundle.",
    "rulesets.empty": "No rule sets loaded yet.",
    "rulesets.emptyBundle": "No rule sets found in the bundle.",
    "rulesets.weapons": "Weapons",
    "rulesets.spells": "Spells",
    "rulesets.file": "File",

    "media.title": "Maps & Media",
    "media.description": 'References from <code>media/manifest.json</code>.',
    "media.empty": "No media references loaded yet.",
    "media.emptyBundle": "No media references found in the bundle.",
    "media.defaultKind": "file",
    "media.noPath": "without path",
    "media.source": "Source:",
    "media.exists": "present:",
    "media.included": "embedded:",

    "player.modeTitle": "Player Mode",
    "player.pickPrompt": "Choose your character:",
    "player.noCharacters": "No characters in the bundle.",
    "player.activeMissions": "Active Missions",
    "player.noActiveMissions": "No active missions.",
    "player.back": "← Back",
    "player.pick": "← Selection",

    "status.noBundle": "No bundle loaded yet.",
    "status.cleared": "View cleared. Local bundle state was removed.",
    "status.swFailed": "Bundle import is running, but the offline cache could not be registered.",
    "status.loadFailed": "Bundle could not be loaded.",
    "status.loading": "Loading {name} …",
    "status.loadedPersisted": "Bundle {name} loaded successfully. Offline re-entry is prepared.",
    "status.loadedNoPersist": "Bundle {name} loaded successfully. The local restore could not be saved on this device.",
    "status.previousKept": "{error} The previous bundle stays visible.",
    "status.restored": "Last loaded bundle {name} was restored locally for the offline start.",

    "hints.iosAppTitle": "iPhone/iPad as an App",
    "hints.iosInstallTitle": "Install on iPhone/iPad",
    "hints.iosAppBody":
      "The PWA runs in standalone mode. Recently loaded bundles are restored locally for offline starts.",
    "hints.iosInstallBody":
      "Use Share → Add to Home Screen to launch the companion without the Safari chrome.",
    "hints.androidAppTitle": "Android App Active",
    "hints.androidInstallTitle": "Install on Android",
    "hints.androidAppBody":
      "The PWA is running installed. Bundle state and offline shell stay local on the device.",
    "hints.androidInstallBody":
      "Use the browser menu → Install app or Add to Home Screen to turn the companion into an app.",
    "hints.desktopTitle": "Desktop and Tablet Companion",
    "hints.desktopBody":
      "For mobile checks install the same build as a PWA on Android or iOS; desktop remains the main GM line.",
    "hints.offlineReadyTitle": "Offline Ready",
    "hints.offlineActiveTitle": "Offline Active",
    "hints.offlineReadyBody":
      "After the first open the service worker keeps the shell files locally. The last loaded bundle state is also held in device storage.",
    "hints.offlineActiveBody":
      "The app is currently offline. If a bundle was already loaded, the last saved state is restored locally.",
    "hints.firstStepTitle": "First Test Step",
    "hints.firstStepBody":
      "For Android/iOS smokes, first import a small campaign bundle and then check the offline restart against the test plan.",

    "general.unknown": "Unknown",
    "general.yes": "yes",
    "general.no": "no",
    "lang.label": "Language",
  },
};

const DATE_LOCALES = { de: "de-DE", en: "en-US" };

let locale = "de";

function detectLocale() {
  if (typeof localStorage !== "undefined") {
    try {
      const stored = localStorage.getItem(LOCALE_KEY);
      if (stored && catalogs[stored]) return stored;
    } catch (_) {}
  }
  if (typeof navigator !== "undefined") {
    const nav = (navigator.language || "de").split("-")[0].toLowerCase();
    if (catalogs[nav]) return nav;
  }
  return "de";
}

export function getLocale() {
  return locale;
}

export function getDateLocale() {
  return DATE_LOCALES[locale] ?? "de-DE";
}

export function setLocale(code) {
  if (!catalogs[code]) return;
  locale = code;
  if (typeof localStorage !== "undefined") {
    try { localStorage.setItem(LOCALE_KEY, code); } catch (_) {}
  }
  if (typeof document !== "undefined") {
    document.documentElement.lang = getDateLocale();
  }
}

export function t(key, params) {
  const template = catalogs[locale]?.[key]
    ?? catalogs.en?.[key]
    ?? catalogs.de?.[key]
    ?? key;
  if (!params) return template;
  return template.replace(/\{(\w+)\}/g, (match, name) =>
    Object.prototype.hasOwnProperty.call(params, name) ? String(params[name]) : match
  );
}

export function hydrateI18n() {
  if (typeof document === "undefined") return;
  for (const el of document.querySelectorAll("[data-i18n]")) {
    el.textContent = t(el.dataset.i18n);
  }
  for (const el of document.querySelectorAll("[data-i18n-html]")) {
    el.innerHTML = t(el.dataset.i18nHtml);
  }
  for (const el of document.querySelectorAll("[data-i18n-placeholder]")) {
    el.placeholder = t(el.dataset.i18nPlaceholder);
  }
}

export function availableLocales() {
  return Object.keys(catalogs);
}

if (typeof navigator !== "undefined") {
  locale = detectLocale();
  if (typeof document !== "undefined") {
    document.documentElement.lang = getDateLocale();
  }
}
