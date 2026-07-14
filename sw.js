/**
 * WineDB Enterprise PWA Service Worker
 * Strategy: Network-first for HTML/CSS/JS (visitors always get the current
 * deploy when online; cache is an offline fallback only) and
 * stale-while-revalidate for images/data samples.
 * Cache Name: winedb-public-cache-v2026.07.4
 */

const CACHE_NAME = 'winedb-public-cache-v2026.07.4';
const CORE_ASSETS = [
  '/',
  '/index.html',
  '/index.css',
  '/app.js',
  '/assets/winedb-cover.png',
  '/site.webmanifest',
  '/sitemap.xml',
  '/samples/vintages.csv',
  '/samples/wineries.csv',
  '/samples/wines.csv',
  '/samples/blends.csv'
];

self.addEventListener('install', event => {
  self.skipWaiting();
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      return cache.addAll(CORE_ASSETS);
    })
  );
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys => {
      return Promise.all(
        keys.map(key => {
          if (key !== CACHE_NAME && key.startsWith('winedb-public-cache-')) {
            return caches.delete(key);
          }
        })
      ).then(() => self.clients.claim());
    })
  );
});

self.addEventListener('fetch', event => {
  // 1. Strictly bypass non-GET requests
  if (event.request.method !== 'GET') {
    return;
  }

  const url = new URL(event.request.url);

  // 2. Strictly bypass cross-origin APIs / fonts
  if (url.origin !== self.location.origin) {
    return;
  }

  const isCritical = event.request.mode === 'navigate' ||
    /\.(css|js|html)(\?.*)?$/.test(url.pathname + url.search) ||
    url.pathname === '/';

  if (isCritical) {
    // 3a. Network-first for pages, styles, and scripts: a stale stylesheet or
    // script must never outlive a deploy. Cache is only an offline fallback.
    event.respondWith(
      fetch(event.request).then(networkResponse => {
        if (networkResponse && networkResponse.status === 200 && networkResponse.type === 'basic') {
          const responseToCache = networkResponse.clone();
          caches.open(CACHE_NAME).then(cache => {
            cache.put(event.request, responseToCache);
          });
        }
        return networkResponse;
      }).catch(() => caches.match(event.request))
    );
    return;
  }

  // 3b. Stale-While-Revalidate for images and data samples
  event.respondWith(
    caches.match(event.request).then(cachedResponse => {
      const fetchPromise = fetch(event.request).then(networkResponse => {
        if (networkResponse && networkResponse.status === 200 && networkResponse.type === 'basic') {
          const responseToCache = networkResponse.clone();
          caches.open(CACHE_NAME).then(cache => {
            cache.put(event.request, responseToCache);
          });
        }
        return networkResponse;
      }).catch(() => {
        return cachedResponse;
      });

      return cachedResponse || fetchPromise;
    })
  );
});
