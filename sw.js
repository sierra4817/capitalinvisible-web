const CACHE_NAME = 'capital-invisible-reader-v15';
const ASSETS = [
  './audiolibro-acceso.html',
  './app.html',
  './styles.css',
  './app.js',
  './cover.png',
  './mockup-capital.png',
  './icon.png',
  './manifest.json'
];

self.addEventListener('install', (e) => {
  self.skipWaiting();
  e.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(ASSETS);
    })
  );
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.map((key) => {
          if (key !== CACHE_NAME) {
            return caches.delete(key);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

// Network-first: intenta siempre la red primero para tener el contenido mas
// reciente; si falla (sin conexion), cae al cache como respaldo offline.
self.addEventListener('fetch', (e) => {
  e.respondWith(
    fetch(e.request)
      .then((networkResponse) => {
        const responseClone = networkResponse.clone();
        caches.open(CACHE_NAME).then((cache) => cache.put(e.request, responseClone));
        return networkResponse;
      })
      .catch(() => caches.match(e.request))
  );
});
