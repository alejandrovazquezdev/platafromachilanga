/* Service worker de Chilangatón: notificaciones push. */
self.addEventListener('install', (event) => {
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(self.clients.claim());
});

self.addEventListener('push', (event) => {
  let data = {};
  try {
    data = event.data ? event.data.json() : {};
  } catch (error) {
    data = { title: 'Chilangatón', body: event.data ? event.data.text() : 'Tienes un nuevo aviso.' };
  }
  const title = data.title || 'Chilangatón';
  const options = {
    body: data.body || 'Tienes un nuevo aviso para tu comercio.',
    icon: data.icon || '/static/img/icon-192.png',
    badge: data.badge || '/static/img/icon-192.png',
    tag: data.tag || 'chilangaton',
    data: { url: data.url || '/noticias' },
    renotify: false,
  };
  event.waitUntil(self.registration.showNotification(title, options));
});

self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  const url = (event.notification.data && event.notification.data.url) || '/noticias';
  event.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true }).then((lista) => {
      for (const cliente of lista) {
        if ('focus' in cliente) {
          cliente.navigate(url);
          return cliente.focus();
        }
      }
      if (clients.openWindow) return clients.openWindow(url);
    })
  );
});
