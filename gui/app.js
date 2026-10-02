/**
 * OPTIX FORGE // Interactive Controller & Tekken-Impact Sound/Visual System
 */

// SISTEMA DE AUDIO SINTÉTICO (WEBAUDIO API // ZERO DEPENDENCIAS)
class ImpactAudioEngine {
  constructor() {
    this.ctx = null;
  }

  init() {
    if (!this.ctx) {
      const AudioContext = window.AudioContext || window.webkitAudioContext;
      if (AudioContext) {
        this.ctx = new AudioContext();
      }
    }
    if (this.ctx && this.ctx.state === 'suspended') {
      this.ctx.resume();
    }
  }

  // Sonido de golpe seco al seleccionar personaje/juego
  playCardSnap() {
    try {
      this.init();
      if (!this.ctx) return;
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();

      osc.type = 'triangle';
      osc.frequency.setValueAtTime(140, this.ctx.currentTime);
      osc.frequency.exponentialRampToValueAtTime(35, this.ctx.currentTime + 0.08);

      gain.gain.setValueAtTime(0.3, this.ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.01, this.ctx.currentTime + 0.08);

      osc.connect(gain);
      gain.connect(this.ctx.destination);

      osc.start();
      osc.stop(this.ctx.currentTime + 0.08);
    } catch (e) {}
  }

  // Sonido de descarga eléctrica / inyección de parche
  playStrikeZap() {
    try {
      this.init();
      if (!this.ctx) return;
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();

      osc.type = 'sawtooth';
      osc.frequency.setValueAtTime(320, this.ctx.currentTime);
      osc.frequency.exponentialRampToValueAtTime(80, this.ctx.currentTime + 0.16);

      gain.gain.setValueAtTime(0.25, this.ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.01, this.ctx.currentTime + 0.16);

      osc.connect(gain);
      gain.connect(this.ctx.destination);

      osc.start();
      osc.stop(this.ctx.currentTime + 0.16);
    } catch (e) {}
  }

  // Sonido de restauración / advertencia controlada
  playRestoreClang() {
    try {
      this.init();
      if (!this.ctx) return;
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();

      osc.type = 'sine';
      osc.frequency.setValueAtTime(220, this.ctx.currentTime);
      osc.frequency.exponentialRampToValueAtTime(110, this.ctx.currentTime + 0.12);

      gain.gain.setValueAtTime(0.2, this.ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.01, this.ctx.currentTime + 0.12);

      osc.connect(gain);
      gain.connect(this.ctx.destination);

      osc.start();
      osc.stop(this.ctx.currentTime + 0.12);
    } catch (e) {}
  }
}

const sfx = new ImpactAudioEngine();

// ESTADO GLOBAL DE LA APLICACIÓN
const state = {
  drives: [],
  activeDrive: "ALL",
  games: [],
  filteredGames: [],
  selectedGame: null,
  activeFilter: "ALL",
  searchQuery: "",
  selectedAspect: "NATIVE"
};

// INICIALIZACIÓN
document.addEventListener("DOMContentLoaded", () => {
  setupEventListeners();
  waitForPyWebView();
});

function waitForPyWebView() {
  if (window.pywebview && window.pywebview.api) {
    initApp();
  } else {
    window.addEventListener("pywebviewready", initApp);
  }
}

async function initApp() {
  await loadDrives();
  await loadGames();
}

// CONFIGURACIÓN DE EVENT LISTENERS
function setupEventListeners() {
  // Búsqueda
  const searchInput = document.getElementById("search-input");
  const clearBtn = document.getElementById("clear-search-btn");

  searchInput.addEventListener("input", (e) => {
    state.searchQuery = e.target.value.toLowerCase().trim();
    applyFilters();
  });

  clearBtn.addEventListener("click", () => {
    searchInput.value = "";
    state.searchQuery = "";
    applyFilters();
  });

  // Filtros por Píldoras
  document.querySelectorAll(".filter-pills .pill").forEach((btn) => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".filter-pills .pill").forEach((p) => p.classList.remove("active"));
      btn.classList.add("active");
      state.activeFilter = btn.dataset.filter;
      sfx.playCardSnap();
      applyFilters();
    });
  });

  // FOV Slider interactivo
  const fovSlider = document.getElementById("fov-slider");
  const fovDisplay = document.getElementById("fov-val-display");
  fovSlider.addEventListener("input", (e) => {
    fovDisplay.textContent = `${e.target.value}°`;
  });

  // Botones de Aspect Ratio
  document.querySelectorAll(".aspect-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".aspect-btn").forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      state.selectedAspect = btn.dataset.aspect;
      sfx.playCardSnap();
    });
  });

  // Botón Escanear a Fondo
  document.getElementById("btn-deep-scan").addEventListener("click", async () => {
    sfx.playStrikeZap();
    await loadGames(state.activeDrive === "ALL" ? null : state.activeDrive);
  });

  // Botón Añadir Carpeta Personalizada
  document.getElementById("btn-add-folder").addEventListener("click", async () => {
    sfx.playCardSnap();
    if (window.pywebview && window.pywebview.api) {
      const res = await window.pywebview.api.select_folder();
      if (res && res.success) {
        showToast("CARPETA REGISTRADA", res.path);
        await loadGames(state.activeDrive === "ALL" ? null : state.activeDrive);
      }
    }
  });

  // Botón Abrir Carpeta de Configuración
  document.getElementById("btn-open-cfg-folder").addEventListener("click", async () => {
    if (state.selectedGame && state.selectedGame.primary_config) {
      await window.pywebview.api.open_config_folder(state.selectedGame.primary_config);
    }
  });

  // Botón Vincular Archivo de Config Manualmente
  document.getElementById("btn-bind-cfg").addEventListener("click", async () => {
    if (!state.selectedGame) return;
    sfx.playCardSnap();
    if (window.pywebview && window.pywebview.api) {
      const res = await window.pywebview.api.select_config_file(state.selectedGame.name, state.selectedGame.install_path);
      if (res && res.success) {
        state.selectedGame.primary_config = res.path;
        state.selectedGame.has_config = true;
        
        const cfgPathDisplay = document.getElementById("dock-cfg-path");
        cfgPathDisplay.textContent = res.path;
        cfgPathDisplay.title = res.path;
        cfgPathDisplay.style.color = "var(--text-secondary)";
        
        showToast("CONFIGURACIÓN VINCULADA", `Archivo asociado: ${res.path.split('\\').pop()}`);
        
        const st = await window.pywebview.api.get_game_status(res.path);
        if (st && st.success && st.status) {
          applyTweakStatusToUI(st.status);
        }
        applyFilters();
      }
    }
  });

  // Botón Aplicar Parche Optix
  document.getElementById("btn-apply-tweaks").addEventListener("click", handleApplyTweaks);

  // Botón Restaurar Fábrica (.bak)
  document.getElementById("btn-restore-factory").addEventListener("click", handleRestoreFactory);
}

// 1. CARGA DE UNIDADES
async function loadDrives() {
  try {
    const res = await window.pywebview.api.get_drives();
    if (res && res.success) {
      state.drives = res.drives;
      renderDriveChips();
      document.getElementById("telem-drives").textContent = `${res.drives.length} ONLINE (${res.drives.map(d => d.letter + ':').join(', ')})`;
    }
  } catch (e) {
    console.error("Error al cargar unidades:", e);
  }
}

function renderDriveChips() {
  const container = document.getElementById("drive-chips-container");
  container.innerHTML = "";

  // Chip "TODAS LAS UNIDADES"
  const allBtn = document.createElement("button");
  allBtn.className = `drive-chip ${state.activeDrive === 'ALL' ? 'active' : ''}`;
  allBtn.innerHTML = `<span class="drive-icon">⚡</span><span class="drive-name">TODAS LAS UNIDADES</span>`;
  allBtn.addEventListener("click", () => selectDrive("ALL", allBtn));
  container.appendChild(allBtn);

  // Chips por cada disco detectado (C:, D:, etc.)
  state.drives.forEach((d) => {
    const btn = document.createElement("button");
    btn.className = `drive-chip ${state.activeDrive === d.letter ? 'active' : ''}`;
    btn.innerHTML = `<span class="drive-icon">💾</span><span class="drive-name">${d.letter}: (${d.free_gb} GB libres)</span>`;
    btn.addEventListener("click", () => selectDrive(d.letter, btn));
    container.appendChild(btn);
  });
}

function selectDrive(driveLetter, btnElement) {
  document.querySelectorAll(".drive-chip").forEach((c) => c.classList.remove("active"));
  btnElement.classList.add("active");
  state.activeDrive = driveLetter;
  sfx.playCardSnap();
  loadGames(driveLetter === "ALL" ? null : driveLetter);
}

// 2. CARGA Y ESCANEO DE JUEGOS
async function loadGames(driveLetter = null) {
  const grid = document.getElementById("games-grid");
  grid.innerHTML = `
    <div class="loading-matrix">
      <div class="voltage-loader"></div>
      <div class="loading-label">ESCANEANDO BIBLIOTECAS EN ${driveLetter ? 'DISCO ' + driveLetter + ':' : 'TODAS LAS UNIDADES'}...</div>
    </div>
  `;

  try {
    const res = await window.pywebview.api.scan_games(driveLetter);
    if (res && res.success) {
      state.games = res.games;
      document.getElementById("telem-games").textContent = res.total_games;
      applyFilters();
    }
  } catch (e) {
    grid.innerHTML = `<div class="loading-label" style="color: var(--accent-red)">Error al escanear: ${e.message}</div>`;
  }
}

// FILTRADO Y RENDERIZADO
function applyFilters() {
  let filtered = [...state.games];

  // Filtro por texto
  if (state.searchQuery) {
    filtered = filtered.filter(
      (g) =>
        g.name.toLowerCase().includes(state.searchQuery) ||
        g.platform.toLowerCase().includes(state.searchQuery) ||
        g.install_path.toLowerCase().includes(state.searchQuery)
    );
  }

  // Filtro por píldora
  if (state.activeFilter === "UNREAL") {
    filtered = filtered.filter((g) => g.engine_type.toLowerCase().includes("unreal"));
  } else if (state.activeFilter === "CONFIG") {
    filtered = filtered.filter((g) => g.has_config);
  } else if (state.activeFilter === "RESTORE") {
    filtered = filtered.filter((g) => g.is_restorable);
  }

  state.filteredGames = filtered;

  // Actualizar contadores
  document.getElementById("count-all").textContent = state.games.length;
  document.getElementById("count-unreal").textContent = state.games.filter((g) => g.engine_type.toLowerCase().includes("unreal")).length;
  document.getElementById("count-config").textContent = state.games.filter((g) => g.has_config).length;
  document.getElementById("count-restore").textContent = state.games.filter((g) => g.is_restorable).length;

  renderGamesGrid();
}

function renderGamesGrid() {
  const grid = document.getElementById("games-grid");
  grid.innerHTML = "";

  if (state.filteredGames.length === 0) {
    grid.innerHTML = `
      <div class="loading-matrix">
        <div class="empty-crosshair"></div>
        <div class="loading-label">NO SE ENCONTRARON JUEGOS CON EL FILTRO ACTUAL</div>
      </div>
    `;
    return;
  }

  state.filteredGames.forEach((game) => {
    const card = document.createElement("div");
    card.className = `game-card ${state.selectedGame && state.selectedGame.install_path === game.install_path ? 'selected' : ''}`;
    
    // Generar banner procedimental limpio
    card.innerHTML = `
      <div class="card-edge-glow"></div>
      <div class="card-banner-box">
        <div class="card-procedural-banner">
          <div class="card-procedural-grid"></div>
          <div class="card-title-watermark">${escapeHtml(game.name.substring(0, 12))}</div>
        </div>
        <div class="card-badges">
          <span class="badge-platform">${escapeHtml(game.platform)}</span>
          <span class="badge-drive">DISCO ${escapeHtml(game.drive_letter)}:</span>
        </div>
        ${game.is_restorable ? '<span class="badge-bak">.BAK ACTIVO</span>' : ''}
      </div>
      <div class="card-body">
        <div class="card-game-title" title="${escapeHtml(game.name)}">${escapeHtml(game.name)}</div>
        <div class="card-engine-info">
          <span>MOTOR:</span>
          <span class="engine-name">${escapeHtml(game.engine_type)}</span>
        </div>
      </div>
    `;

    card.addEventListener("click", () => {
      selectGame(game, card);
    });

    grid.appendChild(card);
  });
}

// SELECCIONAR JUEGO (TEKKEN FIGHTER LOCK-IN)
async function selectGame(game, cardElement) {
  // Sonido y feedback de impacto
  sfx.playCardSnap();

  // Quitar selección previa y animar tarjeta actual
  document.querySelectorAll(".game-card").forEach((c) => c.classList.remove("selected"));
  cardElement.classList.add("selected");

  // Sacudida sutil en el tweak dock
  const dock = document.getElementById("tweak-dock");
  dock.classList.remove("screen-shake");
  void dock.offsetWidth;
  dock.classList.add("screen-shake");

  state.selectedGame = game;

  // Actualizar estado del dock
  document.getElementById("dock-empty").style.display = "none";
  const activeDock = document.getElementById("dock-active");
  activeDock.classList.remove("hidden");

  // Rellenar cabecera
  document.getElementById("dock-game-name").textContent = game.name;
  document.getElementById("dock-platform").textContent = game.platform;
  document.getElementById("dock-engine").textContent = game.engine_type;
  document.getElementById("dock-drive").textContent = `DISCO ${game.drive_letter}:`;

  const cfgPathDisplay = document.getElementById("dock-cfg-path");
  if (game.primary_config) {
    cfgPathDisplay.textContent = game.primary_config;
    cfgPathDisplay.title = game.primary_config;
    cfgPathDisplay.style.color = "var(--text-secondary)";
  } else {
    cfgPathDisplay.textContent = "SIN ARCHIVO DETECTADO (Usa '📎 VINCULAR ARCHIVO')";
    cfgPathDisplay.title = "Haz clic en '📎 VINCULAR ARCHIVO' para asociar el .ini manualmente";
    cfgPathDisplay.style.color = "var(--accent-amber)";
  }

  // Botón restaurar estado inicial
  const restoreBtn = document.getElementById("btn-restore-factory");
  restoreBtn.style.opacity = game.is_restorable ? "1" : "0.5";

  // Cargar estado de tweaks en el archivo si existe
  if (game.primary_config) {
    try {
      const res = await window.pywebview.api.get_game_status(game.primary_config);
      if (res && res.success && res.status) {
        applyTweakStatusToUI(res.status);
      }
    } catch (e) {
      console.error(e);
    }
  }
}

function applyTweakStatusToUI(status) {
  document.getElementById("chk-motion-blur").checked = status.motion_blur_disabled;
  document.getElementById("chk-dof").checked = status.dof_disabled;
  document.getElementById("chk-chromatic").checked = status.chromatic_aberration_disabled;
  document.getElementById("chk-film-grain").checked = status.film_grain_disabled;
  document.getElementById("chk-vignette").checked = status.vignette_disabled;
  document.getElementById("chk-lens-flare").checked = status.lens_flare_disabled;
  document.getElementById("chk-maintain-y").checked = status.fov_maintain_y;
  document.getElementById("chk-unlock-fps").checked = status.fps_unlocked;
  document.getElementById("chk-anisotropic-16x").checked = status.anisotropic_16x;

  const restoreBtn = document.getElementById("btn-restore-factory");
  restoreBtn.style.opacity = status.has_backup ? "1" : "0.5";
  if (state.selectedGame) {
    state.selectedGame.is_restorable = status.has_backup;
  }
}

// APLICAR TWEAKS
async function handleApplyTweaks() {
  if (!state.selectedGame) return;

  if (!state.selectedGame.primary_config) {
    sfx.playRestoreClang();
    showToast("CONFIGURACIÓN REQUERIDA", "Usa el botón '📎 VINCULAR ARCHIVO' arriba para seleccionar el .ini de este juego.");
    return;
  }

  sfx.playStrikeZap();

  // Sacudida en pantalla
  document.body.classList.add("screen-shake");
  setTimeout(() => document.body.classList.remove("screen-shake"), 300);

  const options = {
    disable_motion_blur: document.getElementById("chk-motion-blur").checked,
    disable_dof: document.getElementById("chk-dof").checked,
    disable_chromatic_aberration: document.getElementById("chk-chromatic").checked,
    disable_film_grain: document.getElementById("chk-film-grain").checked,
    disable_vignette: document.getElementById("chk-vignette").checked,
    disable_lens_flare: document.getElementById("chk-lens-flare").checked,
    force_anisotropic_16x: document.getElementById("chk-anisotropic-16x").checked,
    fix_fov_aspect: document.getElementById("chk-maintain-y").checked,
    custom_fov: parseInt(document.getElementById("fov-slider").value),
    aspect_ratio_mode: state.selectedAspect,
    unlock_fps: document.getElementById("chk-unlock-fps").checked
  };

  const statusMsg = document.getElementById("dock-status-msg");
  statusMsg.style.color = "var(--nvidia-neon)";
  statusMsg.textContent = "INYECTANDO PARCHE DE RENDIMIENTO...";

  try {
    const res = await window.pywebview.api.apply_tweaks(state.selectedGame.primary_config, options);
    if (res && res.success) {
      statusMsg.textContent = "✓ PARCHE INYECTADO Y .BAK RESGUARDADO";
      showToast("PARCHE APLICADO", `Optimizaciones inyectadas en ${state.selectedGame.name}`);
      state.selectedGame.is_restorable = true;
      document.getElementById("btn-restore-factory").style.opacity = "1";
      renderGamesGrid();
    } else {
      statusMsg.style.color = "var(--accent-red)";
      statusMsg.textContent = `✗ ERROR: ${res.error || 'Fallo al aplicar'}`;
    }
  } catch (e) {
    statusMsg.style.color = "var(--accent-red)";
    statusMsg.textContent = `✗ ERROR: ${e.message}`;
  }
}

// RESTAURAR A FÁBRICA (.BAK)
async function handleRestoreFactory() {
  if (!state.selectedGame || !state.selectedGame.primary_config) return;

  sfx.playRestoreClang();

  const statusMsg = document.getElementById("dock-status-msg");
  statusMsg.style.color = "var(--accent-amber)";
  statusMsg.textContent = "RESTAURANDO ESTADO ORIGINAL (.BAK)...";

  try {
    const res = await window.pywebview.api.restore_factory(state.selectedGame.primary_config);
    if (res && res.success) {
      statusMsg.style.color = "var(--nvidia-neon)";
      statusMsg.textContent = "✓ ESTADO DE FÁBRICA RESTAURADO";
      showToast("RESTAURACIÓN EXITOSA", res.message);
      
      // Refrescar toggles al estado restaurado
      const st = await window.pywebview.api.get_game_status(state.selectedGame.primary_config);
      if (st && st.success) {
        applyTweakStatusToUI(st.status);
      }
    } else {
      statusMsg.style.color = "var(--accent-red)";
      statusMsg.textContent = `✗ ${res.error}`;
      showToast("RESTAURACIÓN FALLIDA", res.error);
    }
  } catch (e) {
    statusMsg.style.color = "var(--accent-red)";
    statusMsg.textContent = `✗ ${e.message}`;
  }
}

// TOAST NOTIFICATION
let toastTimer = null;
function showToast(title, desc) {
  const toast = document.getElementById("toast-notify");
  document.getElementById("toast-title").textContent = title;
  document.getElementById("toast-desc").textContent = desc;

  toast.classList.add("active");
  if (toastTimer) clearTimeout(toastTimer);
  toastTimer = setTimeout(() => {
    toast.classList.remove("active");
  }, 4000);
}

function escapeHtml(text) {
  if (!text) return "";
  return String(text)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
