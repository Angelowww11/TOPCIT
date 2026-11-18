const CACHE='topcit-study-lab-4';
const BASE=new URL('./',self.location).pathname;
const CORE=['','index.html','style.css','app.js','lessons.js','questions.json','assets/study-lab-hero.webp','assets/icon-192.png'].map(path=>BASE+path);
self.addEventListener('install',event=>event.waitUntil(caches.open(CACHE).then(cache=>cache.addAll(CORE)).then(()=>self.skipWaiting())));
self.addEventListener('activate',event=>event.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(key=>key!==CACHE).map(key=>caches.delete(key)))).then(()=>self.clients.claim())));
self.addEventListener('fetch',event=>{if(event.request.method!=='GET'||new URL(event.request.url).origin!==self.location.origin)return;const isImage=/\.(png|webp|svg)$/.test(new URL(event.request.url).pathname);const online=()=>fetch(event.request,{cache:isImage?'default':'no-store'}).then(response=>{if(response.ok){const copy=response.clone();caches.open(CACHE).then(cache=>cache.put(event.request,copy));}return response;});event.respondWith(isImage?caches.match(event.request).then(hit=>hit||online()):online().catch(()=>caches.match(event.request)));});

