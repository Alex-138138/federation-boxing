window.AthleteTools={
 async me(){return req('/profile/me-athlete')},
 async attendance(id){return req(`/profile/athlete/${id}/attendance`)},
 async render(hostId='athleteExtra'){const host=document.getElementById(hostId);if(!host)return;try{const a=await this.me();const rows=await this.attendance(a.id);host.innerHTML=`<div class="card"><h3>Посещаемость</h3>${(rows||[]).map(x=>`<div class="list-item"><span>${x.date||x.training_date||''}</span><span class="pill ${x.present?'ok':'warn'}">${x.present?'Был':'Отсутствовал'}</span></div>`).join('')||'<div class="empty">Записей пока нет</div>'}</div>`}catch(e){host.innerHTML='<div class="empty">Посещаемость пока недоступна</div>'}}
};