window.CmsEditor={
 blocks:[],pageKey:'public_home',title:'',
 types:[['text','Текст'],['image','Изображение'],['hero','Баннер'],['card','Карточка'],['gallery','Галерея'],['button','Кнопка'],['columns','Колонки'],['divider','Разделитель']],
 newBlock(type){return {id:(crypto.randomUUID?crypto.randomUUID():Date.now().toString()),type,visible:true,content:{title:'',text:'',url:'',image:'',caption:'',label:'',button_text:'',button_url:''},style:{background:'',textColor:'',radius:'16',padding:'24',align:'left'}}},
 add(type){this.blocks.push(this.newBlock(type));this.draw()},
 remove(i){this.blocks.splice(i,1);this.draw()},
 duplicate(i){this.blocks.splice(i+1,0,JSON.parse(JSON.stringify(this.blocks[i])));this.draw()},
 move(i,d){const j=i+d;if(j<0||j>=this.blocks.length)return;[this.blocks[i],this.blocks[j]]=[this.blocks[j],this.blocks[i]];this.draw()},
 toggle(i){this.blocks[i].visible=!this.blocks[i].visible;this.draw()},
 set(i,key,val,section='content'){this.blocks[i][section]=this.blocks[i][section]||{};this.blocks[i][section][key]=val},
 renderBlock(b,i){const c=b.content||{},s=b.style||{};return `<div class="cms-block ${b.visible===false?'cms-hidden':''}"><div class="cms-block-head"><b>${i+1}. ${b.type}</b><div class="row"><button class="chip" onclick="CmsEditor.move(${i},-1)">↑</button><button class="chip" onclick="CmsEditor.move(${i},1)">↓</button><button class="chip" onclick="CmsEditor.duplicate(${i})">Копия</button><button class="chip" onclick="CmsEditor.toggle(${i})">${b.visible===false?'Показать':'Скрыть'}</button><button class="chip danger" onclick="CmsEditor.remove(${i})">Удалить</button></div></div><div class="cms-fields"><input class="input" placeholder="Заголовок" value="${esc(c.title||'')}" oninput="CmsEditor.set(${i},'title',this.value)"><textarea class="textarea" placeholder="Текст" oninput="CmsEditor.set(${i},'text',this.value)">${esc(c.text||'')}</textarea><input class="input" placeholder="URL изображения / ссылки" value="${esc(c.url||c.image||'')}" oninput="CmsEditor.set(${i},'url',this.value)"><div class="row"><input class="input" placeholder="Фон" value="${esc(s.background||'')}" oninput="CmsEditor.set(${i},'background',this.value,'style')"><input class="input" placeholder="Цвет текста" value="${esc(s.textColor||'')}" oninput="CmsEditor.set(${i},'textColor',this.value,'style')"></div></div></div>`},
 draw(){const host=document.getElementById('cmsBlocks');if(host)host.innerHTML=this.blocks.map((b,i)=>this.renderBlock(b,i)).join('')||'<div class="empty">Добавьте первый блок страницы.</div>'},
 async load(key){this.pageKey=key;try{const p=await req(`/cms/pages/${key}`);const v=(p.versions||[])[0];this.title=p.title||'';this.blocks=v?.snapshot?.blocks||[]}catch{this.blocks=[]}this.draw()},
 async save(){const title=document.getElementById('cmsPageTitle')?.value||this.title||this.pageKey;const d=await req(`/cms/pages/${this.pageKey}/save`,{method:'POST',body:JSON.stringify({title,blocks:this.blocks})});return d}
};
function esc(v){return String(v??'').replace(/[&<>"']/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]))}
