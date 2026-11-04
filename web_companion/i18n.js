/**
 * RPX Pro Web-Companion Internationalization (i18n)
 * Supports DE, EN, ES, ZH, JA, and RU with 4-stage fallback chain: requested -> en -> de -> key
 */

export const SUPPORTED_LOCALES = ["de", "en", "es", "zh", "ja", "ru"];
export const DEFAULT_LOCALE = "de";
export const STORAGE_KEY = "rpx-companion:language";

export const DATE_LOCALES = {
  de: "de-DE",
  en: "en-US",
  es: "es-ES",
  zh: "zh-CN",
  ja: "ja-JP",
  ru: "ru-RU",
};

export const TRANSLATIONS = {
  de: {
    doc_title: "RPX Pro Companion",
    meta_description: "Offline-PWA-Companion für RPX-Pro-Kampagnen-Bundles.",
    eyebrow: "Offline Web/PWA Companion",
    hero_title: "RPX Pro Companion",
    hero_lead: "Liest lokale rpx-campaign-bundle-v1-ZIPs für Kampagnenübersicht, Charakterstatus, Missionen, Karten- und Medienhinweise.",
    panel_import_title: "Bundle laden",
    panel_import_lead: "Die App arbeitet lokal im Browser. Es werden keine Daten hochgeladen.",
    dropzone_title: "ZIP auswählen oder hier ablegen",
    dropzone_copy: "Erwartet wird ein Export im Format rpx-campaign-bundle-v1.",
    action_clear: "Ansicht leeren",
    action_player_mode: "Spieler-Modus",
    status_empty: "Noch kein Bundle geladen.",
    status_reading: "Bundle wird gelesen...",
    status_success: "{name} erfolgreich geladen ({worlds} Welten, {sessions} Sessions).",
    status_cleared: "Ansicht geleert.",
    status_error: "Fehler beim Laden des Bundles: {error}",
    summary_empty: "Nach dem Import erscheinen hier Kampagnenmetadaten und Schnellzahlen.",
    worlds_empty: "Noch keine Welten geladen.",
    sessions_empty: "Noch keine Sessions geladen.",
    rulesets_empty: "Noch keine Regelwerke geladen.",
    media_empty: "Noch keine Medienreferenzen geladen.",
    panel_summary_title: "Kampagnenstand",
    panel_summary_lead: "Direkt aus dem Bundle extrahiert.",
    panel_worlds_title: "Welten",
    panel_worlds_lead: "Kerninfos zu Welten, Orten und Karten.",
    panel_sessions_title: "Sessions",
    panel_sessions_lead: "Charaktere, Missionen und letzte Chat-Einträge.",
    panel_rulesets_title: "Regelwerke",
    panel_rulesets_lead: "Mitgelieferte JSON-Regelwerke aus dem Bundle.",
    panel_media_title: "Karten & Medien",
    panel_media_lead: "Referenzen aus media/manifest.json.",
    meta_source: "Quelle",
    meta_worlds: "Welten",
    meta_sessions: "Sessions",
    meta_characters: "Charaktere",
    meta_exported: "Exportiert",
    meta_app: "App",
    meta_schema: "Schema",
    meta_unknown: "Unbekannt",
    player_overlay_title: "Spieler-Modus",
    player_overlay_select: "Charakter auswählen",
    player_overlay_close: "Schließen",
    player_overlay_hp: "LP",
    player_overlay_mana: "Mana",
    player_overlay_missions: "Aktive Missionen",
    player_overlay_chat: "Chat-Protokoll",
    player_overlay_no_missions: "Keine aktiven Missionen.",
    player_overlay_no_chat: "Keine Chat-Einträge.",
    hint_ios_standalone_title: "iPhone/iPad als App",
    hint_ios_standalone_body: "Die PWA läuft im Standalone-Modus. Zuletzt geladene Bundles werden lokal für Offline-Starts wiederhergestellt.",
    hint_ios_browser_title: "iPhone/iPad installieren",
    hint_ios_browser_body: "Über Teilen → Zum Home-Bildschirm kann der Companion ohne Safari-Chrome gestartet werden.",
    hint_android_standalone_title: "Android-App aktiv",
    hint_android_standalone_body: "Die PWA läuft installiert. Bundle-Stand und Offline-Shell bleiben lokal auf dem Gerät.",
    hint_android_browser_title: "Android installieren",
    hint_android_browser_body: "Über Browser-Menü → App installieren oder Zum Startbildschirm hinzufügen wird der Companion zur App.",
    hint_desktop_title: "Desktop- und Tablet-Companion",
    hint_desktop_body: "Für mobile Prüfungen denselben Build als PWA auf Android oder iOS installieren; Desktop bleibt die GM-Hauptlinie.",
    hint_offline_ready_title: "Offline bereit",
    hint_offline_ready_body: "Nach dem ersten Öffnen hält der Service Worker die Shell-Dateien lokal vor. Der letzte geladene Bundle-Stand wird zusätzlich im Gerätespeicher gehalten.",
    hint_offline_active_title: "Offline aktiv",
    hint_offline_active_body: "Die App läuft gerade offline. Wenn bereits ein Bundle geladen war, wird der zuletzt gespeicherte Stand lokal wiederhergestellt.",
    hint_test_step_title: "Erster Testschritt",
    hint_test_step_body: "Für Android-/iOS-Smokes zuerst ein kleines Kampagnen-Bundle importieren und danach den Offline-Neustart gegen den Testplan prüfen.",
  },
  en: {
    doc_title: "RPX Pro Companion",
    meta_description: "Offline PWA companion for RPX Pro campaign bundles.",
    eyebrow: "Offline Web/PWA Companion",
    hero_title: "RPX Pro Companion",
    hero_lead: "Reads local rpx-campaign-bundle-v1 ZIPs for campaign overview, character stats, quests, map and media references.",
    panel_import_title: "Load Bundle",
    panel_import_lead: "The app works locally in your browser. No data is uploaded.",
    dropzone_title: "Select ZIP or drop here",
    dropzone_copy: "Expected export format: rpx-campaign-bundle-v1.",
    action_clear: "Clear view",
    action_player_mode: "Player Mode",
    status_empty: "No bundle loaded yet.",
    status_reading: "Reading bundle...",
    status_success: "{name} loaded successfully ({worlds} worlds, {sessions} sessions).",
    status_cleared: "View cleared.",
    status_error: "Error loading bundle: {error}",
    summary_empty: "Campaign metadata and quick stats will appear here after import.",
    worlds_empty: "No worlds loaded yet.",
    sessions_empty: "No sessions loaded yet.",
    rulesets_empty: "No rulesets loaded yet.",
    media_empty: "No media references loaded yet.",
    panel_summary_title: "Campaign Status",
    panel_summary_lead: "Extracted directly from the bundle.",
    panel_worlds_title: "Worlds",
    panel_worlds_lead: "Core details on worlds, locations and maps.",
    panel_sessions_title: "Sessions",
    panel_sessions_lead: "Characters, quests and latest chat log.",
    panel_rulesets_title: "Rulesets",
    panel_rulesets_lead: "Bundled JSON rulesets from the package.",
    panel_media_title: "Maps & Media",
    panel_media_lead: "References from media/manifest.json.",
    meta_source: "Source",
    meta_worlds: "Worlds",
    meta_sessions: "Sessions",
    meta_characters: "Characters",
    meta_exported: "Exported",
    meta_app: "App",
    meta_schema: "Schema",
    meta_unknown: "Unknown",
    player_overlay_title: "Player Mode",
    player_overlay_select: "Select Character",
    player_overlay_close: "Close",
    player_overlay_hp: "HP",
    player_overlay_mana: "Mana",
    player_overlay_missions: "Active Quests",
    player_overlay_chat: "Chat Log",
    player_overlay_no_missions: "No active quests.",
    player_overlay_no_chat: "No chat entries.",
    hint_ios_standalone_title: "iPhone/iPad as App",
    hint_ios_standalone_body: "PWA runs in standalone mode. Recently loaded bundles are restored locally for offline launches.",
    hint_ios_browser_title: "Install on iPhone/iPad",
    hint_ios_browser_body: "Use Share → Add to Home Screen to launch the companion without Safari browser controls.",
    hint_android_standalone_title: "Android App Active",
    hint_android_standalone_body: "PWA is installed. Bundle state and offline shell remain locally on your device.",
    hint_android_browser_title: "Install on Android",
    hint_android_browser_body: "Use Browser Menu → Install App or Add to Home Screen to turn the companion into an app.",
    hint_desktop_title: "Desktop and Tablet Companion",
    hint_desktop_body: "Install this build as a PWA on Android or iOS for mobile testing; Desktop remains the primary GM workstation.",
    hint_offline_ready_title: "Offline Ready",
    hint_offline_ready_body: "After the first launch, the service worker caches all shell files locally. The last loaded bundle is also saved in device storage.",
    hint_offline_active_title: "Offline Active",
    hint_offline_active_body: "The app is currently offline. If a bundle was previously loaded, the saved state will be restored locally.",
    hint_test_step_title: "First Test Step",
    hint_test_step_body: "For Android/iOS smoke tests, import a small campaign bundle and verify offline restart against the test plan.",
  },
  es: {
    doc_title: "RPX Pro Companion",
    meta_description: "Compañero PWA sin conexión para paquetes de campaña de RPX Pro.",
    eyebrow: "Compañero PWA / Web sin conexión",
    hero_title: "RPX Pro Companion",
    hero_lead: "Lee archivos ZIP rpx-campaign-bundle-v1 para resumen de campaña, estado de personajes, misiones y referencias multimedia.",
    panel_import_title: "Cargar paquete",
    panel_import_lead: "La aplicación funciona localmente en el navegador. No se sube ningún dato.",
    dropzone_title: "Seleccionar ZIP o soltar aquí",
    dropzone_copy: "Se espera el formato de exportación rpx-campaign-bundle-v1.",
    action_clear: "Limpiar vista",
    action_player_mode: "Modo jugador",
    status_empty: "Aún no se ha cargado ningún paquete.",
    status_reading: "Leyendo paquete...",
    status_success: "{name} cargado correctamente ({worlds} mundos, {sessions} sesiones).",
    status_cleared: "Vista limpiada.",
    status_error: "Error al cargar el paquete: {error}",
    summary_empty: "Los metadatos de la campaña y estadísticas rápidas aparecerán aquí tras la importación.",
    worlds_empty: "Aún no se han cargado mundos.",
    sessions_empty: "Aún no se han cargado sesiones.",
    rulesets_empty: "Aún no se han cargado reglamentos.",
    media_empty: "Aún no se han cargado referencias multimedia.",
    panel_summary_title: "Estado de la campaña",
    panel_summary_lead: "Extraído directamente del paquete.",
    panel_worlds_title: "Mundos",
    panel_worlds_lead: "Detalles clave sobre mundos, ubicaciones y mapas.",
    panel_sessions_title: "Sesiones",
    panel_sessions_lead: "Personajes, misiones y último registro de chat.",
    panel_rulesets_title: "Reglamentos",
    panel_rulesets_lead: "Reglamentos JSON incluidos en el paquete.",
    panel_media_title: "Mapas y medios",
    panel_media_lead: "Referencias de media/manifest.json.",
    meta_source: "Fuente",
    meta_worlds: "Mundos",
    meta_sessions: "Sesiones",
    meta_characters: "Personajes",
    meta_exported: "Exportado",
    meta_app: "App",
    meta_schema: "Esquema",
    meta_unknown: "Desconocido",
    player_overlay_title: "Modo jugador",
    player_overlay_select: "Seleccionar personaje",
    player_overlay_close: "Cerrar",
    player_overlay_hp: "PV",
    player_overlay_mana: "Maná",
    player_overlay_missions: "Misiones activas",
    player_overlay_chat: "Registro de chat",
    player_overlay_no_missions: "Sin misiones activas.",
    player_overlay_no_chat: "Sin entradas de chat.",
    hint_ios_standalone_title: "iPhone/iPad como App",
    hint_ios_standalone_body: "La PWA funciona en modo independiente. Los paquetes cargados se restauran localmente sin conexión.",
    hint_ios_browser_title: "Instalar en iPhone/iPad",
    hint_ios_browser_body: "Use Compartir → Añadir a pantalla de inicio para abrir el compañero sin controles de Safari.",
    hint_android_standalone_title: "App Android activa",
    hint_android_standalone_body: "La PWA está instalada. El paquete y la interfaz permanecen seguros en su dispositivo.",
    hint_android_browser_title: "Instalar en Android",
    hint_android_browser_body: "Use Menú del navegador → Instalar aplicación o Añadir a pantalla de inicio.",
    hint_desktop_title: "Compañero para escritorio y tableta",
    hint_desktop_body: "Instale esta PWA en Android o iOS para pruebas móviles; el escritorio sigue siendo el centro GM principal.",
    hint_offline_ready_title: "Listo sin conexión",
    hint_offline_ready_body: "Tras el primer inicio, el service worker guarda los archivos en caché. El último paquete también se almacena localmente.",
    hint_offline_active_title: "Modo sin conexión activo",
    hint_offline_active_body: "La app está funcionando sin conexión. Se restaurará el último estado guardado.",
    hint_test_step_title: "Paso de prueba inicial",
    hint_test_step_body: "Para pruebas en Android/iOS, importe un paquete pequeño y verifique el reinicio sin conexión.",
  },
  zh: {
    doc_title: "RPX Pro 协同伴侣",
    meta_description: "用于 RPX Pro 战役数据包的离线 PWA 协同伴侣。",
    eyebrow: "离线 Web/PWA 协同伴侣",
    hero_title: "RPX Pro 协同伴侣",
    hero_lead: "读取本地 rpx-campaign-bundle-v1 压缩包，浏览战役概览、角色状态、任务日志及地图与媒体索引。",
    panel_import_title: "加载战役包",
    panel_import_lead: "应用完全在浏览器本地运行，不会上传任何数据。",
    dropzone_title: "选择 ZIP 文件或拖放到此处",
    dropzone_copy: "支持的格式为 rpx-campaign-bundle-v1。",
    action_clear: "清空视图",
    action_player_mode: "玩家模式",
    status_empty: "尚未加载任何战役包。",
    status_reading: "正在读取战役包...",
    status_success: "成功加载 {name}（{worlds} 个世界，{sessions} 个会话）。",
    status_cleared: "视图已清空。",
    status_error: "加载战役包失败：{error}",
    summary_empty: "导入战役包后，此处将显示概览元数据与统计数字。",
    worlds_empty: "尚未加载任何世界。",
    sessions_empty: "尚未加载任何会话。",
    rulesets_empty: "尚未加载任何规则书。",
    media_empty: "尚未加载任何媒体引用。",
    panel_summary_title: "战役状态",
    panel_summary_lead: "直接从战役包中提取。",
    panel_worlds_title: "游戏世界",
    panel_worlds_lead: "世界、地点与地图的核心信息。",
    panel_sessions_title: "跑团会话",
    panel_sessions_lead: "角色状态、当前任务与最新聊天记录。",
    panel_rulesets_title: "规则体系",
    panel_rulesets_lead: "数据包中附带的 JSON 规则书。",
    panel_media_title: "地图与媒体",
    panel_media_lead: "来自 media/manifest.json 的索引。",
    meta_source: "来源",
    meta_worlds: "世界数",
    meta_sessions: "会话数",
    meta_characters: "角色数",
    meta_exported: "导出时间",
    meta_app: "主程序",
    meta_schema: "架构版本",
    meta_unknown: "未知",
    player_overlay_title: "玩家模式",
    player_overlay_select: "选择角色",
    player_overlay_close: "关闭",
    player_overlay_hp: "生命值",
    player_overlay_mana: "法力值",
    player_overlay_missions: "当前任务",
    player_overlay_chat: "聊天日志",
    player_overlay_no_missions: "暂无进行中的任务。",
    player_overlay_no_chat: "暂无聊天记录。",
    hint_ios_standalone_title: "iPhone/iPad 独立应用模式",
    hint_ios_standalone_body: "PWA 正在独立窗口中运行。最近载入的数据将保存在本地供离线使用。",
    hint_ios_browser_title: "在 iPhone/iPad 上安装",
    hint_ios_browser_body: "通过 Safari 分享按钮 → 添加到主屏幕，即可无边框启动伴侣应用。",
    hint_android_standalone_title: "Android 应用已激活",
    hint_android_standalone_body: "PWA 已安装运行。战役包与离线外壳始终保存在您的设备中。",
    hint_android_browser_title: "在 Android 上安装",
    hint_android_browser_body: "通过浏览器菜单 → 安装应用或添加到主屏幕，即可转为独立 App。",
    hint_desktop_title: "桌面与平板伴侣",
    hint_desktop_body: "可在 Android 或 iOS 上安装此 PWA 用于移动测试；桌面版仍为主持人工作台。",
    hint_offline_ready_title: "离线就绪",
    hint_offline_ready_body: "首次打开后，Service Worker 已缓存离线资源。最后载入的数据包也会持久保存在设备存储中。",
    hint_offline_active_title: "离线模式运行中",
    hint_offline_active_body: "应用当前处于离线状态。先前保存的战役数据已自动恢复。",
    hint_test_step_title: "测试建议",
    hint_test_step_body: "建议先导入小型战役包，然后验证无网络环境下的重启恢复情况。",
  },
  ja: {
    doc_title: "RPX Pro コンパニオン",
    meta_description: "RPX Pro キャンペーンバンドル用オフラインPWAコンパニオン。",
    eyebrow: "オフライン Web/PWA コンパニオン",
    hero_title: "RPX Pro コンパニオン",
    hero_lead: "ローカルの rpx-campaign-bundle-v1 ZIPを読み込み、キャンペーン概要、キャラ情報、クエスト、マップ・メディアを参照できます。",
    panel_import_title: "バンドル読み込み",
    panel_import_lead: "ブラウザのローカル環境でのみ動作し、データが外部に送信されることはありません。",
    dropzone_title: "ZIPファイルを選択またはドロップ",
    dropzone_copy: "形式: rpx-campaign-bundle-v1",
    action_clear: "表示をクリア",
    action_player_mode: "プレイヤーモード",
    status_empty: "バンドルが読み込まれていません。",
    status_reading: "バンドルを読み込み中...",
    status_success: "{name} を読み込みました ({worlds} 個のワールド、{sessions} セッション)。",
    status_cleared: "表示をクリアしました。",
    status_error: "読み込みエラー: {error}",
    summary_empty: "インポート後、ここにキャンペーンメタデータと統計が表示されます。",
    worlds_empty: "ワールドがありません。",
    sessions_empty: "セッションがありません。",
    rulesets_empty: "ルールセットがありません。",
    media_empty: "メディア参照がありません。",
    panel_summary_title: "キャンペーン状況",
    panel_summary_lead: "バンドルから直接抽出された情報です。",
    panel_worlds_title: "ワールド",
    panel_worlds_lead: "世界観、ロケーション、マップ情報。",
    panel_sessions_title: "セッション",
    panel_sessions_lead: "キャラクター、クエスト、チャットログ。",
    panel_rulesets_title: "ルールセット",
    panel_rulesets_lead: "バンドルに含まれるJSONルールセット。",
    panel_media_title: "マップ＆メディア",
    panel_media_lead: "media/manifest.json の参照一覧。",
    meta_source: "ソース",
    meta_worlds: "ワールド数",
    meta_sessions: "セッション数",
    meta_characters: "キャラクター数",
    meta_exported: "エクスポート日",
    meta_app: "アプリ",
    meta_schema: "スキーマ",
    meta_unknown: "不明",
    player_overlay_title: "プレイヤーモード",
    player_overlay_select: "キャラクター選択",
    player_overlay_close: "閉じる",
    player_overlay_hp: "HP",
    player_overlay_mana: "MP",
    player_overlay_missions: "アクティブクエスト",
    player_overlay_chat: "チャットログ",
    player_overlay_no_missions: "クエストはありません。",
    player_overlay_no_chat: "チャットログはありません。",
    hint_ios_standalone_title: "iPhone/iPad アプリモード",
    hint_ios_standalone_body: "スタンドアロンモードで動作中。読み込んだデータは端末に保存されオフラインで起動できます。",
    hint_ios_browser_title: "iPhone/iPad にインストール",
    hint_ios_browser_body: "共有ボタン → ホーム画面に追加 を選択するとフルスクリーンで起動できます。",
    hint_android_standalone_title: "Android アプリ動作中",
    hint_android_standalone_body: "PWAがインストールされています。データは端末内に安全に保持されます。",
    hint_android_browser_title: "Android にインストール",
    hint_android_browser_body: "メニュー → アプリをインストール または ホーム画面に追加 を選択してください。",
    hint_desktop_title: "デスクトップ＆タブレット",
    hint_desktop_body: "モバイル端末へのPWA導入で卓上端末としてテスト可能。メインGM機能はデスクトップ版が担います。",
    hint_offline_ready_title: "オフライン準備完了",
    hint_offline_ready_body: "初回の読み込みで全リソースがキャッシュされました。最後に開いたデータも端末内に保存されます。",
    hint_offline_active_title: "オフライン動作中",
    hint_offline_active_body: "ネットワーク未接続です。保存済みのデータから自動復元されました。",
    hint_test_step_title: "テスト推奨手順",
    hint_test_step_body: "小規模なバンドルを読み込み、オフライン状態での再起動テストを行ってください。",
  },
  ru: {
    doc_title: "RPX Pro Companion",
    meta_description: "Офлайн-PWA компаньон для пакетов кампаний RPX Pro.",
    eyebrow: "Офлайн Web/PWA Компаньон",
    hero_title: "RPX Pro Companion",
    hero_lead: "Чтение локальных ZIP-пакетов rpx-campaign-bundle-v1: обзор кампании, состояние персонажей, задания и медиа-материалы.",
    panel_import_title: "Загрузить пакет",
    panel_import_lead: "Приложение работает локально в браузере. Данные никуда не передаются.",
    dropzone_title: "Выберите ZIP-файл или перетащите сюда",
    dropzone_copy: "Ожидается формат rpx-campaign-bundle-v1.",
    action_clear: "Очистить",
    action_player_mode: "Режим игрока",
    status_empty: "Пакет кампании пока не загружен.",
    status_reading: "Чтение пакета...",
    status_success: "{name} успешно загружен ({worlds} миров, {sessions} сессий).",
    status_cleared: "Окно очищено.",
    status_error: "Ошибка загрузки: {error}",
    summary_empty: "После импорта здесь появятся метаданные кампании и сводная статистика.",
    worlds_empty: "Миры не загружены.",
    sessions_empty: "Сессии не загружены.",
    rulesets_empty: "Своды правил не загружены.",
    media_empty: "Ссылки на медиа не загружены.",
    panel_summary_title: "Статус кампании",
    panel_summary_lead: "Извлечено напрямую из пакета.",
    panel_worlds_title: "Миры",
    panel_worlds_lead: "Ключевая информация о мирах, локациях и картах.",
    panel_sessions_title: "Сессии",
    panel_sessions_lead: "Персонажи, текущие задания и журнал чата.",
    panel_rulesets_title: "Своды правил",
    panel_rulesets_lead: "Правила в формате JSON из загруженного пакета.",
    panel_media_title: "Карты и медиа",
    panel_media_lead: "Ссылки из файла media/manifest.json.",
    meta_source: "Источник",
    meta_worlds: "Миры",
    meta_sessions: "Сессии",
    meta_characters: "Персонажи",
    meta_exported: "Экспорт",
    meta_app: "Приложение",
    meta_schema: "Схема",
    meta_unknown: "Неизвестно",
    player_overlay_title: "Режим игрока",
    player_overlay_select: "Выберите персонажа",
    player_overlay_close: "Закрыть",
    player_overlay_hp: "ОЗ",
    player_overlay_mana: "Мана",
    player_overlay_missions: "Активные задания",
    player_overlay_chat: "Журнал чата",
    player_overlay_no_missions: "Нет активных заданий.",
    player_overlay_no_chat: "Журнал чата пуст.",
    hint_ios_standalone_title: "iPhone/iPad как приложение",
    hint_ios_standalone_body: "PWA работает автономно. Последний загруженный пакет сохраняется локально для офлайн-запуска.",
    hint_ios_browser_title: "Установка на iPhone/iPad",
    hint_ios_browser_body: "Нажмите Поделиться → На экран «Домой» для запуска без элементов интерфейса Safari.",
    hint_android_standalone_title: "Приложение Android активно",
    hint_android_standalone_body: "PWA установлено. Данные пакета остаются на вашем устройстве.",
    hint_android_browser_title: "Установка на Android",
    hint_android_browser_body: "Используйте Меню браузера → Установить приложение или Добавить на главный экран.",
    hint_desktop_title: "Компаньон для ПК и планшетов",
    hint_desktop_body: "Установите как PWA на мобильные устройства для тестирования; ПК остается главным рабочим местом ведущего.",
    hint_offline_ready_title: "Готово к работе офлайн",
    hint_offline_ready_body: "Файлы оболочки сохранены сервис-воркером. Последний пакет также сохраняется в памяти устройства.",
    hint_offline_active_title: "Офлайн-режим активен",
    hint_offline_active_body: "Нет подключения к сети. Восстановлено последнее сохраненное состояние.",
    hint_test_step_title: "Первый шаг проверки",
    hint_test_step_body: "Загрузите небольшой пакет и проверьте работу в автономном режиме согласно тест-плану.",
  },
};

let currentLocale = DEFAULT_LOCALE;

export function normalizeLocale(lang) {
  if (!lang || typeof lang !== "string") {
    return DEFAULT_LOCALE;
  }
  const clean = lang.toLowerCase().trim();
  for (const sup of SUPPORTED_LOCALES) {
    if (clean === sup || clean.startsWith(sup + "-") || clean.startsWith(sup + "_")) {
      return sup;
    }
  }
  return DEFAULT_LOCALE;
}

export function detectLocale() {
  try {
    if (typeof localStorage !== "undefined") {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) {
        return normalizeLocale(stored);
      }
    }
    if (typeof navigator !== "undefined" && navigator.languages) {
      for (const l of navigator.languages) {
        const norm = normalizeLocale(l);
        if (norm !== DEFAULT_LOCALE || l.toLowerCase().startsWith("de")) {
          return norm;
        }
      }
    }
    if (typeof navigator !== "undefined" && navigator.language) {
      return normalizeLocale(navigator.language);
    }
  } catch {
    // fallback
  }
  return DEFAULT_LOCALE;
}

export function getLocale() {
  return currentLocale;
}

export function setLocale(newLocale) {
  currentLocale = normalizeLocale(newLocale);
  try {
    if (typeof localStorage !== "undefined") {
      localStorage.setItem(STORAGE_KEY, currentLocale);
    }
  } catch {
    // ignore
  }
  return currentLocale;
}

export function t(key, params = {}, locale = currentLocale) {
  const normLocale = normalizeLocale(locale);
  const dict = TRANSLATIONS[normLocale] || TRANSLATIONS[DEFAULT_LOCALE];
  let text = dict[key];

  if (text === undefined && normLocale !== "en" && TRANSLATIONS.en) {
    text = TRANSLATIONS.en[key];
  }
  if (text === undefined && normLocale !== "de" && TRANSLATIONS.de) {
    text = TRANSLATIONS.de[key];
  }
  if (text === undefined) {
    return key;
  }

  return String(text).replace(/\{(\w+)\}/g, (_, name) => {
    return params[name] !== undefined ? String(params[name]) : `{${name}}`;
  });
}

export function formatTimestamp(value, locale = currentLocale) {
  if (!Number.isFinite(value)) {
    return t("meta_unknown", {}, locale);
  }
  const dateLocale = DATE_LOCALES[normalizeLocale(locale)] || "de-DE";
  try {
    return new Date(value * 1000).toLocaleString(dateLocale, {
      dateStyle: "medium",
      timeStyle: "short",
    });
  } catch {
    return new Date(value * 1000).toISOString();
  }
}

export function translateDocument(root = typeof document !== "undefined" ? document : null, locale = currentLocale) {
  if (!root) return;

  const norm = normalizeLocale(locale);
  if (root.documentElement) {
    root.documentElement.lang = norm;
  }

  const textNodes = root.querySelectorAll("[data-i18n]");
  for (const node of textNodes) {
    const key = node.dataset.i18n;
    if (key) {
      node.textContent = t(key, {}, norm);
    }
  }

  const htmlNodes = root.querySelectorAll("[data-i18n-html]");
  for (const node of htmlNodes) {
    const key = node.dataset.i18nHtml;
    if (key) {
      node.innerHTML = t(key, {}, norm);
    }
  }

  const placeholders = root.querySelectorAll("[data-i18n-placeholder]");
  for (const node of placeholders) {
    const key = node.dataset.i18nPlaceholder;
    if (key) {
      node.placeholder = t(key, {}, norm);
    }
  }

  const ariaLabels = root.querySelectorAll("[data-i18n-aria-label]");
  for (const node of ariaLabels) {
    const key = node.dataset.i18nAriaLabel;
    if (key) {
      node.setAttribute("aria-label", t(key, {}, norm));
    }
  }
}
