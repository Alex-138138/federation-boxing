window.ParentTools={
 async children(){return req('/profile/children')},
 async render(hostId='parentChildren'){const host=document.getElementById(hostId);if(!host)return;try{const rows=await this.children();host.innerHTML=(rows||[]).map(x=>`<div class="card"><div class="portrait"><div class="avatar">🥊</div><div><h3>${x.full_name||x.name||'Спортсмен'}</h3><div class="muted">Рейтинг: ${x.rating??'—'}</div></div></div><button class="btn secondary" onclick="ParentTools.open(${x.id})">Открыть кабинет</button></div>`).join('')||'<div class="empty">Дети ещё не привязаны</div>'}catch(e){host.innerHTML='<div class="empty">Не удалось загрузить детей</div>'}},
 open(id){location.hash=`athlete:${id}`;if(window.render)render()}
};