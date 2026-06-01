# Exportformat – `rpx-campaign-bundle-v1`

Stand: 2026-05-24

## Zweck

`rpx-campaign-bundle-v1` ist das portable Austauschformat für RPX Pro. Es bündelt Welten, Sessions, Regelwerk-Dateien und optionale Medien in einer ZIP-Datei, damit Desktop, späterer Web/PWA-Companion und andere Geräte denselben Kampagnenstand lesen können.

## Container

- Dateityp: `.zip`
- Pflichtdateien:
  - `manifest.json`
  - `worlds/<world_id>.json`
  - `sessions/<session_id>.json`
  - `rulesets/<name>.json`
  - `media/manifest.json`
- Optionale Dateien:
  - `media/images/...`
  - `media/maps/...`
  - `media/music/...`
  - `media/sounds/...`
  - `media/misc/...`

Beispiel:

```text
campaign.zip
├── manifest.json
├── worlds/
│   └── 3801d703.json
├── sessions/
│   └── e19fa19c.json
├── rulesets/
│   ├── dnd5e.json
│   ├── dsa5.json
│   └── generic_fantasy.json
└── media/
    ├── manifest.json
    ├── images/
    ├── maps/
    ├── music/
    └── sounds/
```

## `manifest.json`

`manifest.json` beschreibt den Bundle-Kopf und die enthaltenen Daten:

```json
{
  "format": "rpx-campaign-bundle-v1",
  "exported_at": 1779645600.0,
  "app": {
    "title": "RPX Pro",
    "version": "1.0.0",
    "schema_version": "1.0"
  },
  "media_mode": "manifest",
  "worlds": [],
  "sessions": [],
  "rulesets": [],
  "media": []
}
```

Wichtige Felder:

| Feld | Bedeutung |
|---|---|
| `format` | Formatkennung. Importer müssen vor dem Einlesen darauf prüfen. |
| `exported_at` | Unix-Zeitstempel des Exports. |
| `app` | RPX-Pro-Version und Daten-Schema des exportierenden Clients. |
| `media_mode` | `none`, `manifest` oder `files`. |
| `worlds` | Enthaltene Welten mit `id`, `name`, `genre`, `file`. |
| `sessions` | Enthaltene Sessions mit `id`, `world_id`, `name`, `file`. |
| `rulesets` | Mitgelieferte Regelwerk-Dateien. |
| `media` | Medienreferenzen mit Originalpfad, Bundle-Ziel und Include-Status. |

## Relative Pfade

Alle exportierten Welt- und Session-Dateien verwenden im Bundle relative Medienpfade:

- `media/images/...`
- `media/maps/...`
- `media/music/...`
- `media/sounds/...`
- `media/misc/...`

Absolute lokale Desktop-Pfade dürfen im Bundle nicht verbleiben. Wenn RPX Pro lokale Dateien außerhalb von `rpx_pro_data/media/` referenziert, werden sie beim Export auf einen stabilen Bundle-Pfad unter `media/...` umgebogen und zusätzlich im Medien-Manifest dokumentiert.

## Medienmodi

### `none`

- Exportiert nur Daten und Regelwerke.
- `media/manifest.json` bleibt als Referenzliste erhalten.
- `included` ist immer `false`.

### `manifest`

- Standardmodus.
- Schreibt relative Medienpfade in die JSON-Dateien und dokumentiert alle gefundenen Dateien in `media/manifest.json`.
- Die eigentlichen Mediendateien werden nicht eingebettet.

### `files`

- Schreibt Daten wie `manifest`.
- Kopiert zusätzlich vorhandene Mediendateien in die ZIP unter ihren relativen Bundle-Pfaden.

## `media/manifest.json`

Jeder Eintrag beschreibt genau eine referenzierte Datei:

| Feld | Bedeutung |
|---|---|
| `original_path` | Ursprünglicher Wert aus Welt/Session vor der Umschreibung |
| `bundle_path` | Relativer Zielpfad im Bundle |
| `kind` | `image`, `map`, `music`, `sound` oder `document` |
| `exists` | Datei war beim Export lokal vorhanden |
| `included` | Datei wurde in die ZIP kopiert |
| `source_path` | Absoluter Quellpfad auf dem exportierenden System oder `null` |
| `size_bytes` | Dateigröße der Quelle, sofern vorhanden |

## Auswahlregeln

- Ohne Filter exportiert RPX Pro alle geladenen Welten und Sessions.
- Mit `world_ids` werden nur diese Welten und die dazugehörigen Sessions exportiert.
- Mit `session_ids` werden nur diese Sessions exportiert; ihre referenzierten Welten werden automatisch ergänzt.
- Regelwerk-Dateien aus `rulesets/*.json` werden immer mitgenommen, damit ein Companion dieselben Basisdaten lesen kann.

## Stabilitätsregeln

- Importer sollen unbekannte zusätzliche Felder ignorieren.
- Vorhandene Felder dürfen nur additiv erweitert werden.
- Eine zukünftige v2 bekommt eine neue `format`-Kennung statt stiller Breaking Changes.

## API / CLI

Die Bundle-Erzeugung und der Bundle-Import sind über die Python-API und die JSON-RPC-CLI erreichbar:

```json
{
  "id": 7,
  "method": "export_campaign_bundle",
  "params": {
    "destination": "releases/campaigns/demo.zip",
    "include_media": "manifest"
  }
}
```

Optionale Parameter:

- `world_ids`: Liste expliziter Welt-IDs
- `session_ids`: Liste expliziter Session-IDs
- `include_media`: `none`, `manifest` oder `files`

Import-Beispiel:

```json
{
  "id": 8,
  "method": "import_campaign_bundle",
  "params": {
    "source": "releases/campaigns/demo.zip",
    "conflict_strategy": "rename"
  }
}
```

## Importregeln

- `import_campaign_bundle` akzeptiert die Konfliktstrategien `rename`, `replace` und `skip`.
- Bundle-Medienpfade wie `media/maps/...` werden beim Import auf lokale Desktop-Pfade unter `rpx_pro_data/media/...` normalisiert.
- Ältere relative Pfade wie `maps/...`, `images/...`, `music/...` oder `sounds/...` bleiben importierbar und werden auf dieselbe Zielstruktur abgebildet.
- Bei `rename` erhalten kollidierende Welt-/Session-IDs und Regelwerk-Dateien neue eindeutige Namen; Medien werden auf freie lokale Dateinamen umgebogen.
- Bei `replace` überschreibt das Bundle vorhandene Welten, Sessions, Regelwerk-Dateien und Medien mit denselben Zielnamen.
- Bei `skip` bleiben vorhandene Konflikte unangetastet; der Import verwendet dann die bestehenden lokalen Ziele.
