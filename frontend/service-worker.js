const CACHE_NAME = "book-reviewing-cache-v1";
const urlsToCache = [
    '/',
    '/dashboard',
    '/reviews',
    '/recommendations',
    '/saved-recommendations',
    '/frontend/style.css',
    '/frontend/darkmode.js',
    '/frontend/src/services/api.js',
    '/frontend/src/services/review.js',
    '/frontend/src/services/recommendation.js',
    '/frontend/src/services/auth.js',
    '/frontend/src/services/logout.js',
    '/frontend/filters.js',
    '/frontend/assets/old-london/Old London.ttf',
    '/frontend/manifest.json'
];

async function preCache() {
    const cache = await caches.open(CACHE_NAME);
    return cache.addAll(urlsToCache);
}

self.addEventListener('install', event => {
    event.waitUntil(preCache());
})


async function fetchAssets(event) {
    try {
        const response = await fetch(event.request);
        return response;
    } catch (error) {
        const cache = await caches.open(CACHE_NAME);
        return cache.match(event.request,{cacheName:CACHE_NAME,ignoreVary:true});
    }
}

self.addEventListener('fetch', (event) => {
    event.respondWith(fetchAssets(event));
})



async function cleanupCache() {
    const keys = await caches.keys();
    const keysToDelete = keys.map(key => {
        if (key !== CACHE_NAME) {
            return caches.delete(key)
        }
    })

    return Promise.all(keysToDelete);
}

self.addEventListener('activate', event => {
    self.skipWaiting();
    event.waitUntil(cleanupCache);
})