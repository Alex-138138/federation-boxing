const CACHE="boxing-full-2";
self.addEventListener("install",e=>e.waitUntil(caches.open(CACHE).then(c=>c.addAll(["/","/index.html","/app.js","/styles.css"]))));
self.addEventListener("fetch",e=>e.respondWith(fetch(e.request).catch(()=>caches.match(e.request))));
self.addEventListener("push",e=>{let p={title:"Федерация бокса",body:"Новое уведомление"};try{p=e.data.json()}catch{}e.waitUntil(self.registration.showNotification(p.title,{body:p.body}))});

self.addEventListener('push',event=>{let data={};try{data=event.data?event.data.json():{}}catch{data={body:event.data?.text()||''}};const title=data.title||'Федерация бокса Иркутского округа';const options={body:data.body||'Новое уведомление',icon:data.icon||'/icons/icon-192.png',badge:data.badge||'/icons/icon-192.png',data:{url:data.url||'/'},tag:data.tag||'boxing-notification'};event.waitUntil(self.registration.showNotification(title,options))});
self.addEventListener('notificationclick',event=>{event.notification.close();const url=event.notification.data?.url||'/';event.waitUntil(clients.matchAll({type:'window',includeUncontrolled:true}).then(list=>{for(const c of list){if('focus' in c){c.navigate(url);return c.focus()}}return clients.openWindow?clients.openWindow(url):null}))});
