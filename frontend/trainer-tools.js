window.TrainerTools={
 async groups(){return req('/trainer/groups')},
 async athletes(groupId){return req(`/trainer/groups/${groupId}/athletes`)},
 async render(hostId='trainerTools'){const host=document.getElementById(hostId);if(!host)return;try{const groups=await this.groups();host.innerHTML=(groups||[]).map(g=>`<div class="card"><h3>${g.name||'Группа'}</h3><div class="muted">Код подключения: ${g.join_code||'—'}</div><button class="btn secondary" onclick="TrainerTools.showAthletes(${g.id})">Спортсмены</button></div>`).join('')||'<div class="empty">Групп пока нет</div>'}catch(e){host.innerHTML='<div class="empty">Не удалось загрузить группы</div>'}},
 async showAthletes(id){const rows=await this.athletes(id);alert((rows||[]).map(x=>x.full_name||x.name||`Спортсмен #${x.id}`).join('\n')||'В группе пока нет спортсменов')}
};