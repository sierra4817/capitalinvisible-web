// ============================================================
// La Mente Millonaria es Invisible — Reproductor de audiolibro
// CAPITULOS viene de capitulos_data.js (26 capítulos, cargado antes)
// ============================================================

const PARTES = {
  '06_cap_tulo_1_la_trampa_del_h_mster_diferencia_letal_': 'Parte I — La ilusión',
  '10_cap_tulo_5_el_coste_de_la_ignorancia_tu_cerebro_no': 'Parte II — La invisibilidad',
  '16_cap_tulo_11_el_presupuesto_no_es_una_dieta_es_un_m': 'Parte III — La construcción',
  '22_cap_tulo_17_la_deuda_que_destruye_patrimonio_deuda': 'Parte IV — La protección',
};

let indiceActual = 0;
let oracionActual = -1;

const audioEl = document.getElementById('audioEl');
const tocEl = document.getElementById('toc');
const readerTitle = document.getElementById('readerTitle');
const readerEyebrow = document.getElementById('readerEyebrow');
const readerText = document.getElementById('readerText');
const playBtn = document.getElementById('playBtn');
const prevBtn = document.getElementById('prevBtn');
const nextBtn = document.getElementById('nextBtn');
const seekBar = document.getElementById('seekBar');
const timeCurrent = document.getElementById('timeCurrent');
const timeTotal = document.getElementById('timeTotal');
const speedSelect = document.getElementById('speedSelect');
const sidebar = document.getElementById('sidebar');
const menuToggle = document.getElementById('menuToggle');
const creditsBtn = document.getElementById('creditsBtn');
const creditsOverlay = document.getElementById('creditsOverlay');
const creditsClose = document.getElementById('creditsClose');
const creditsPlayBtn = document.getElementById('creditsPlayBtn');
const themeToggle = document.getElementById('themeToggle');
const volumeBtn = document.getElementById('volumeBtn');
const volumeBar = document.getElementById('volumeBar');

function formatTime(s) {
  if (!isFinite(s) || s < 0) s = 0;
  const m = Math.floor(s / 60);
  const sec = Math.floor(s % 60);
  return `${m}:${sec.toString().padStart(2, '0')}`;
}

function construirIndice() {
  tocEl.innerHTML = '';
  CAPITULOS.forEach((cap, i) => {
    if (PARTES[cap.id]) {
      const label = document.createElement('div');
      label.className = 'toc-part';
      label.textContent = PARTES[cap.id];
      tocEl.appendChild(label);
    }
    const btn = document.createElement('button');
    btn.className = 'toc-item';
    btn.dataset.index = i;
    const num = String(i).padStart(2, '0');
    btn.innerHTML = `<span class="toc-num">${num}</span><span>${tituloCorto(cap.titulo)}</span><span class="toc-playing">♪</span>`;
    btn.addEventListener('click', () => cargarCapitulo(i, true));
    tocEl.appendChild(btn);
  });
}

function tituloCorto(t) {
  // Si empieza por "PARTE ..." + el título del capítulo va después en el mismo string, nos quedamos con
  // la parte más informativa para la lista lateral.
  if (t.startsWith('PARTE')) return t;
  return t.replace(/^CAPÍTULO\s*\d+:\s*/i, '');
}

function marcarActivoEnIndice() {
  document.querySelectorAll('.toc-item').forEach((el) => {
    el.classList.toggle('active', Number(el.dataset.index) === indiceActual);
  });
  const activo = document.querySelector('.toc-item.active');
  if (activo) activo.scrollIntoView({ block: 'nearest' });
}

function construirTexto(cap) {
  readerText.innerHTML = '';
  cap.oraciones.forEach((frase, i) => {
    const span = document.createElement('span');
    span.className = 'oracion';
    span.dataset.index = i;
    span.textContent = frase + ' ';
    span.addEventListener('click', () => saltarAOracion(i));
    readerText.appendChild(span);
  });
}

function saltarAOracion(i) {
  const cap = CAPITULOS[indiceActual];
  if (!audioEl.duration || !isFinite(audioEl.duration)) return;
  const totalCaracteres = cap.oraciones.reduce((a, s) => a + s.length, 0);
  let acumulado = 0;
  for (let j = 0; j < i; j++) acumulado += cap.oraciones[j].length;
  const fraccion = acumulado / totalCaracteres;
  audioEl.currentTime = fraccion * audioEl.duration;
  
  // Auto-reproducir al hacer clic en la frase
  audioEl.play().then(() => setPlayIcon(true)).catch(() => setPlayIcon(false));
}

function actualizarResaltado() {
  const cap = CAPITULOS[indiceActual];
  if (!cap || !audioEl.duration || !isFinite(audioEl.duration)) return;
  const totalCaracteres = cap.oraciones.reduce((a, s) => a + s.length, 0);
  const fraccionActual = audioEl.currentTime / audioEl.duration;
  let acumulado = 0;
  let nuevoIndex = 0;
  for (let j = 0; j < cap.oraciones.length; j++) {
    acumulado += cap.oraciones[j].length;
    if (acumulado / totalCaracteres > fraccionActual) { nuevoIndex = j; break; }
    nuevoIndex = j;
  }
  if (nuevoIndex !== oracionActual) {
    oracionActual = nuevoIndex;
    document.querySelectorAll('.reader-text .oracion').forEach((el) => {
      const idx = Number(el.dataset.index);
      el.classList.toggle('activa', idx === oracionActual);
      el.classList.toggle('leida', idx < oracionActual);
    });
    const activo = document.querySelector('.oracion.activa');
    if (activo) activo.scrollIntoView({ block: 'center', behavior: 'smooth' });
  }
}

function cargarCapitulo(i, autoplay, saveToStorage = true) {
  if (i < 0 || i >= CAPITULOS.length) return;
  indiceActual = i;
  oracionActual = -1;
  const cap = CAPITULOS[i];

  if (cap.id === 'creditos') {
    readerEyebrow.textContent = 'Antes de empezar';
  } else if (PARTES[cap.id]) {
    readerEyebrow.textContent = 'Portada de parte';
  } else {
    readerEyebrow.textContent = `Capítulo ${i} de ${CAPITULOS.length - 1}`;
  }
  readerTitle.textContent = cap.titulo;
  construirTexto(cap);
  marcarActivoEnIndice();

  audioEl.src = cap.audio;
  audioEl.playbackRate = parseFloat(speedSelect.value);

  if (saveToStorage) {
    localStorage.setItem('audiobook_current_index', i);
    localStorage.setItem('audiobook_current_time', '0');
  }

  if (autoplay) {
    audioEl.play().then(() => setPlayIcon(true)).catch(() => setPlayIcon(false));
  } else {
    setPlayIcon(false);
  }

  if (window.innerWidth <= 720) sidebar.classList.remove('open');
}

function setPlayIcon(reproduciendo) {
  playBtn.textContent = reproduciendo ? '❚❚' : '▶';
  playBtn.setAttribute('aria-label', reproduciendo ? 'Pausa' : 'Reproducir');
}

playBtn.addEventListener('click', () => {
  if (audioEl.paused) {
    audioEl.play().then(() => setPlayIcon(true));
  } else {
    audioEl.pause();
    setPlayIcon(false);
  }
});

prevBtn.addEventListener('click', () => cargarCapitulo(indiceActual - 1, true));
nextBtn.addEventListener('click', () => cargarCapitulo(indiceActual + 1, true));

audioEl.addEventListener('ended', () => {
  if (indiceActual < CAPITULOS.length - 1) {
    cargarCapitulo(indiceActual + 1, true);
  } else {
    setPlayIcon(false);
  }
});

audioEl.addEventListener('timeupdate', () => {
  if (!audioEl.duration || !isFinite(audioEl.duration)) return;
  const pct = (audioEl.currentTime / audioEl.duration) * 100;
  seekBar.value = pct;
  seekBar.style.setProperty('--progress', pct + '%');
  timeCurrent.textContent = formatTime(audioEl.currentTime);
  actualizarResaltado();
  
  // Guardar posición en localStorage
  localStorage.setItem('audiobook_current_time', audioEl.currentTime);
});

audioEl.addEventListener('loadedmetadata', () => {
  timeTotal.textContent = formatTime(audioEl.duration);
});

seekBar.addEventListener('input', () => {
  if (!audioEl.duration || !isFinite(audioEl.duration)) return;
  audioEl.currentTime = (seekBar.value / 100) * audioEl.duration;
});

speedSelect.addEventListener('change', () => {
  const rate = parseFloat(speedSelect.value);
  audioEl.playbackRate = rate;
  localStorage.setItem('audiobook_playback_rate', rate);
});

menuToggle.addEventListener('click', () => sidebar.classList.toggle('open'));

creditsBtn.addEventListener('click', () => creditsOverlay.classList.add('open'));
creditsClose.addEventListener('click', () => creditsOverlay.classList.remove('open'));
creditsOverlay.addEventListener('click', (e) => {
  if (e.target === creditsOverlay) creditsOverlay.classList.remove('open');
});
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') creditsOverlay.classList.remove('open');
});

creditsPlayBtn.addEventListener('click', () => {
  creditsOverlay.classList.remove('open');
  cargarCapitulo(0, true); // "creditos" es ahora el capítulo 0, y encadena solo con el prólogo al terminar
});

document.addEventListener('keydown', (e) => {
  if (e.target.tagName === 'SELECT' || e.target.tagName === 'INPUT') return;
  if (e.code === 'Space') { e.preventDefault(); playBtn.click(); }
  if (e.code === 'ArrowRight' && e.shiftKey) nextBtn.click();
  if (e.code === 'ArrowLeft' && e.shiftKey) prevBtn.click();
});

// Eventos de control de volumen
volumeBar.addEventListener('input', () => {
  const vol = parseFloat(volumeBar.value);
  audioEl.volume = vol;
  audioEl.muted = false;
  volumeBar.style.setProperty('--volume-progress', (vol * 100) + '%');
  actualizarIconoVolumen(vol);
  localStorage.setItem('audiobook_volume', vol);
  localStorage.setItem('audiobook_muted', 'false');
});

volumeBtn.addEventListener('click', () => {
  if (audioEl.muted) {
    audioEl.muted = false;
    actualizarIconoVolumen(audioEl.volume);
    localStorage.setItem('audiobook_muted', 'false');
  } else {
    audioEl.muted = true;
    volumeBtn.textContent = '🔇';
    localStorage.setItem('audiobook_muted', 'true');
  }
});

function actualizarIconoVolumen(vol) {
  if (vol === 0) {
    volumeBtn.textContent = '🔇';
  } else if (vol < 0.4) {
    volumeBtn.textContent = '🔈';
  } else if (vol < 0.7) {
    volumeBtn.textContent = '🔉';
  } else {
    volumeBtn.textContent = '🔊';
  }
}

// Evento de cambio de tema
themeToggle.addEventListener('click', () => {
  const isLight = document.body.classList.toggle('theme-light');
  if (isLight) {
    themeToggle.textContent = '☾';
    localStorage.setItem('audiobook_theme', 'light');
  } else {
    themeToggle.textContent = '☼';
    localStorage.setItem('audiobook_theme', 'dark');
  }
});

// Eventos de carga (spinner)
audioEl.addEventListener('waiting', () => {
  playBtn.classList.add('loading');
});
audioEl.addEventListener('playing', () => {
  playBtn.classList.remove('loading');
});
audioEl.addEventListener('canplay', () => {
  playBtn.classList.remove('loading');
});
audioEl.addEventListener('pause', () => {
  playBtn.classList.remove('loading');
});
audioEl.addEventListener('error', () => {
  playBtn.classList.remove('loading');
});
audioEl.addEventListener('seeking', () => {
  playBtn.classList.add('loading');
});
audioEl.addEventListener('seeked', () => {
  playBtn.classList.remove('loading');
});

// Función de inicialización
function inicializarApp() {
  construirIndice();

  // 1. Cargar volumen
  const savedVolume = localStorage.getItem('audiobook_volume');
  const savedMuted = localStorage.getItem('audiobook_muted');
  if (savedVolume !== null) {
    audioEl.volume = parseFloat(savedVolume);
    volumeBar.value = savedVolume;
    volumeBar.style.setProperty('--volume-progress', (parseFloat(savedVolume) * 100) + '%');
  } else {
    audioEl.volume = 0.8;
    volumeBar.value = 0.8;
    volumeBar.style.setProperty('--volume-progress', '80%');
  }

  if (savedMuted === 'true') {
    audioEl.muted = true;
    volumeBtn.textContent = '🔇';
  } else {
    audioEl.muted = false;
    actualizarIconoVolumen(audioEl.volume);
  }

  // 2. Cargar velocidad de reproducción
  const savedSpeed = localStorage.getItem('audiobook_playback_rate');
  if (savedSpeed !== null) {
    speedSelect.value = savedSpeed;
    audioEl.playbackRate = parseFloat(savedSpeed);
  }

  // 3. Cargar tema
  const savedTheme = localStorage.getItem('audiobook_theme') || 'dark';
  if (savedTheme === 'light') {
    document.body.classList.add('theme-light');
    themeToggle.textContent = '☾';
  } else {
    document.body.classList.remove('theme-light');
    themeToggle.textContent = '☼';
  }

  // 4. Cargar capítulo y segundo
  const savedIndex = localStorage.getItem('audiobook_current_index');
  const savedTime = localStorage.getItem('audiobook_current_time');

  if (savedIndex !== null) {
    indiceActual = parseInt(savedIndex);
  } else {
    indiceActual = 0;
  }

  // Cargar capítulo sin guardarlo a storage de nuevo (para evitar borrar el tiempo guardado)
  cargarCapitulo(indiceActual, false, false);

  if (savedTime !== null && savedTime !== '0') {
    const setSavedTime = () => {
      audioEl.currentTime = parseFloat(savedTime);
      audioEl.removeEventListener('loadedmetadata', setSavedTime);
    };
    audioEl.addEventListener('loadedmetadata', setSavedTime);
  }
}

// Arranque
inicializarApp();
