// const CACHE_NAME = 'certverify-v1';
// // This list includes the basic files your app needs to show its main pages offline.
// const urlsToCache = [
//   '/',
//   '/login',
//   '/register',
//   '/dashboard',
//   '/static/css/custom.css',
//   '/static/js/main.js',
//   '/static/logo.svg'
// ];

// // When the app is "installed" on the user's phone, this code runs.
// // It opens a special storage area called a "cache" and saves all the files listed above.
// self.addEventListener('install', event => {
//   event.waitUntil(
//     caches.open(CACHE_NAME)
//       .then(cache => {
//         console.log('Opened cache and saving essential files.');
//         return cache.addAll(urlsToCache);
//       })
//   );
//   self.skipWaiting();
// });

// // Every time the browser tries to load a page or a file from your website, this code runs.
// self.addEventListener('fetch', event => {
//   event.respondWith(
//     // It first checks if a copy of the requested file is already saved in the cache.
//     caches.match(event.request)
//       .then(response => {
//         // If the file is found in the cache, it returns the saved copy immediately. This is what makes it work offline.
//         if (response) {
//           return response;
//         }
//         // If the file is not in the cache, it fetches it from the internet as usual.
//         return fetch(event.request);
//       }
//     )
//   );
// });

