from fastapi import APIRouter, Depends
from app.services.security import require_roles, CurrentUser

router=APIRouter(prefix="/cms",tags=["cms-blocks"])

BLOCK_TYPES={
 "text":{"label":"Текст","fields":["title","text"]},
 "image":{"label":"Изображение","fields":["url","alt","caption"]},
 "hero":{"label":"Баннер","fields":["title","text","image","button_text","button_url"]},
 "card":{"label":"Карточка","fields":["title","text","image","link"]},
 "gallery":{"label":"Галерея","fields":["title","images"]},
 "button":{"label":"Кнопка","fields":["label","url"]},
 "columns":{"label":"Колонки","fields":["columns"]},
 "divider":{"label":"Разделитель","fields":[]}
}

@router.get("/block-types")
def block_types(c:CurrentUser=Depends(require_roles("admin"))):
    return BLOCK_TYPES

@router.get("/page-keys")
def page_keys(c:CurrentUser=Depends(require_roles("admin"))):
    return [
      {"key":"public_home","label":"Главная Федерации"},
      {"key":"leadership","label":"Руководство"},
      {"key":"coaches","label":"Тренерский состав"},
      {"key":"champions","label":"Выдающиеся боксёры"},
      {"key":"mayor","label":"Мэр Иркутского округа"},
      {"key":"supporters","label":"Помощники Федерации"},
      {"key":"news","label":"Новости и события"},
      {"key":"admin_home","label":"Кабинет администратора"},
      {"key":"trainer_home","label":"Кабинет тренера"},
      {"key":"parent_home","label":"Кабинет родителя"},
      {"key":"athlete_home","label":"Кабинет спортсмена"}
    ]
