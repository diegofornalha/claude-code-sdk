/**
 * Service Worker for Neo4j Agent Chat PWA
 * Handles offline functionality and caching
 */

const CACHE_NAME = 'neo4j-chat-v1';
const OFFLINE_URL = '/chat/offline.html';

// Assets to cache on install
const STATIC_CACHE_URLS = [
    '/chat/',
    '/chat/index.html',
    '/chat/styles.css',
    '/chat/app.js',
    '/chat/manifest.json',
    '/chat/favicon.ico'
];

// Install event - cache static assets
self.addEventListener('install', event => {
    console.log('[SW] Installing Service Worker');

    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => {
                console.log('[SW] Caching static assets');
                return cache.addAll(STATIC_CACHE_URLS);
            })
            .then(() => self.skipWaiting())
    );
});

// Activate event - cleanup old caches
self.addEventListener('activate', event => {
    console.log('[SW] Activating Service Worker');

    event.waitUntil(
        caches.keys()
            .then(cacheNames => {
                return Promise.all(
                    cacheNames
                        .filter(cacheName => cacheName !== CACHE_NAME)
                        .map(cacheName => {
                            console.log('[SW] Deleting old cache:', cacheName);
                            return caches.delete(cacheName);
                        })
                );
            })
            .then(() => self.clients.claim())
    );
});

// Fetch event - serve from cache or network
self.addEventListener('fetch', event => {
    const { request } = event;
    const url = new URL(request.url);

    // Skip non-GET requests
    if (request.method !== 'GET') {
        return;
    }

    // Skip API requests - always fetch from network
    if (url.pathname.includes('/api/')) {
        event.respondWith(
            fetch(request)
                .catch(() => {
                    // Return error response for API failures
                    return new Response(
                        JSON.stringify({ error: 'Offline - API unavailable' }),
                        {
                            headers: { 'Content-Type': 'application/json' },
                            status: 503
                        }
                    );
                })
        );
        return;
    }

    // Cache-first strategy for static assets
    if (isStaticAsset(url.pathname)) {
        event.respondWith(
            caches.match(request)
                .then(cachedResponse => {
                    if (cachedResponse) {
                        // Return from cache and update in background
                        fetchAndCache(request);
                        return cachedResponse;
                    }
                    return fetchAndCache(request);
                })
                .catch(() => {
                    // If both cache and network fail, show offline page
                    return caches.match(OFFLINE_URL);
                })
        );
        return;
    }

    // Network-first strategy for HTML pages
    event.respondWith(
        fetch(request)
            .then(response => {
                // Clone the response before caching
                const responseToCache = response.clone();

                caches.open(CACHE_NAME)
                    .then(cache => cache.put(request, responseToCache));

                return response;
            })
            .catch(() => {
                // Try to serve from cache
                return caches.match(request)
                    .then(cachedResponse => {
                        if (cachedResponse) {
                            return cachedResponse;
                        }
                        // Show offline page as fallback
                        return caches.match(OFFLINE_URL);
                    });
            })
    );
});

// Helper function to determine if URL is a static asset
function isStaticAsset(pathname) {
    const staticExtensions = ['.css', '.js', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.woff', '.woff2'];
    return staticExtensions.some(ext => pathname.endsWith(ext));
}

// Helper function to fetch and cache a request
function fetchAndCache(request) {
    return fetch(request)
        .then(response => {
            // Don't cache non-successful responses
            if (!response.ok) {
                return response;
            }

            const responseToCache = response.clone();

            caches.open(CACHE_NAME)
                .then(cache => cache.put(request, responseToCache));

            return response;
        });
}

// Message event - handle messages from the app
self.addEventListener('message', event => {
    if (event.data && event.data.type === 'SKIP_WAITING') {
        self.skipWaiting();
    }

    if (event.data && event.data.type === 'CLEAR_CACHE') {
        caches.delete(CACHE_NAME)
            .then(() => {
                console.log('[SW] Cache cleared');
                event.ports[0].postMessage({ success: true });
            })
            .catch(error => {
                console.error('[SW] Failed to clear cache:', error);
                event.ports[0].postMessage({ success: false, error: error.message });
            });
    }
});

// Background sync for offline messages
self.addEventListener('sync', event => {
    if (event.tag === 'send-messages') {
        event.waitUntil(sendQueuedMessages());
    }
});

// Function to send queued messages when back online
async function sendQueuedMessages() {
    const cache = await caches.open('message-queue');
    const requests = await cache.keys();

    for (const request of requests) {
        try {
            const response = await fetch(request);
            if (response.ok) {
                await cache.delete(request);
            }
        } catch (error) {
            console.error('[SW] Failed to send queued message:', error);
        }
    }
}

// Push notifications support
self.addEventListener('push', event => {
    if (!event.data) return;

    const data = event.data.json();
    const options = {
        body: data.body || 'Nova mensagem do Claude',
        icon: '/chat/icon-192.png',
        badge: '/chat/icon-96.png',
        vibrate: [200, 100, 200],
        data: {
            url: data.url || '/chat/'
        }
    };

    event.waitUntil(
        self.registration.showNotification(data.title || 'Neo4j Agent Chat', options)
    );
});

// Handle notification clicks
self.addEventListener('notificationclick', event => {
    event.notification.close();

    event.waitUntil(
        clients.openWindow(event.notification.data.url)
    );
});