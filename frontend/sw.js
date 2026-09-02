const CACHE="boxing-full-2";
self.addEventListener("install",e=>e.waitUntil(caches.open(CACHE).then(c=>c.addAll(["/","/index.html","/app.js","/styles.css"]))));
self.addEventListener("fetch",e=>e.respondWith(fetch(e.request).catch(()=>caches.match(e.request))));
self.addEventListener("push",e=>{let p={title:"Федерация бокса",body:"Новое уведомление"};try{p=e.data.json()}catch{}e.waitUntil(self.registration.showNotification(p.title,{body:p.body}))});
