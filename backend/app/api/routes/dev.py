from datetime import date, time
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models import *

router = APIRouter(prefix="/dev", tags=["dev"])

@router.post("/seed")
def seed(db: Session = Depends(get_db)):
    if db.scalar(select(User).where(User.phone == "+79000000001")):
        return {"ok": True, "already_seeded": True}

    admin=User(phone="+79000000001")
    trainer=User(phone="+79000000002")
    parent=User(phone="+79000000003")
    athlete_user=User(phone="+79000000004")
    db.add_all([admin,trainer,parent,athlete_user]); db.flush()

    for u,role in [(admin,"admin"),(trainer,"trainer"),(parent,"parent"),(athlete_user,"athlete")]:
        db.add(UserRole(user_id=u.id,role=role))
    db.add(UserRole(user_id=athlete_user.id,role="parent"))  # multi-role demo

    trainer_person=Person(user_id=trainer.id,first_name="Иван",last_name="Иванов",phone=trainer.phone)
    parent_person=Person(user_id=parent.id,first_name="Мария",last_name="Петрова",phone=parent.phone,address="Иркутский округ")
    athlete_person=Person(user_id=athlete_user.id,first_name="Алексей",last_name="Смирнов",birth_date=date(2008,5,12),phone=athlete_user.phone)
    db.add_all([trainer_person,parent_person,athlete_person]); db.flush()

    hall=Hall(name="Зал №3",address="Иркутский округ, ул. Спортивная, 10",phone="+73952000000")
    db.add(hall); db.flush()
    group=Group(hall_id=hall.id,trainer_user_id=trainer.id,name="Юноши 2008–2010")
    db.add(group); db.flush()

    db.add_all([
        TrainingSchedule(group_id=group.id,weekday=1,start_time=time(18,0),end_time=time(19,30),location=hall.name),
        TrainingSchedule(group_id=group.id,weekday=3,start_time=time(18,0),end_time=time(19,30),location=hall.name),
        TrainingSchedule(group_id=group.id,weekday=5,start_time=time(18,0),end_time=time(19,30),location=hall.name),
    ])

    athlete=Athlete(person_id=athlete_person.id,rating_points=790)
    db.add(athlete); db.flush()
    db.add(GroupMembership(group_id=group.id,athlete_id=athlete.id))
    db.add(Achievement(athlete_id=athlete.id,title="🥇 Турнир округа",description="Первое место"))
    db.add(JoinCode(code="DEMO-GROUP",hall_id=hall.id,trainer_user_id=trainer.id,group_id=group.id))

    # CMS seeded pages
    pages = {
      "public_home": {
        "title":"Федерация бокса Иркутского округа",
        "blocks":[
          {"type":"hero","visible":True,"content":{"title":"Федерация бокса Иркутского округа","text":"Официальное приложение Федерации"}},
          {"type":"card","visible":True,"content":{"title":"Руководство Федерации","text":"Председатель и заместители"}},
          {"type":"card","visible":True,"content":{"title":"Тренерский состав","text":"Тренеры, залы и контакты"}},
          {"type":"card","visible":True,"content":{"title":"Выдающиеся боксёры Иркутской области","text":"История и достижения"}}
        ]
      },
      "parent_home":{"title":"Родитель","blocks":[{"type":"card","visible":True,"content":{"title":"Мой ребёнок","text":"Тренировки, сообщения и достижения"}}]},
      "trainer_home":{"title":"Тренер","blocks":[{"type":"card","visible":True,"content":{"title":"Моя группа","text":"Заявки, спортсмены и сообщения"}}]},
      "athlete_home":{"title":"Спортсмен","blocks":[{"type":"card","visible":True,"content":{"title":"Мой спорт","text":"Расписание, рейтинг и достижения"}}]},
      "admin_home":{"title":"Администратор","blocks":[{"type":"card","visible":True,"content":{"title":"Управление","text":"Контент, пользователи и аудит"}}]}
    }
    for key,snap in pages.items():
        p=Page(page_key=key,title=snap["title"])
        db.add(p); db.flush()
        v=PageVersion(page_id=p.id,version_no=1,snapshot={"page_key":key,**snap},created_by=admin.id)
        db.add(v); db.flush()
        p.published_version_id=v.id

    db.commit()
    return {
        "ok":True,
        "join_code":"DEMO-GROUP",
        "group_id":group.id,
        "athlete_id":athlete.id,
        "phones":{
            "admin":"+79000000001",
            "trainer":"+79000000002",
            "parent":"+79000000003",
            "athlete":"+79000000004"
        },
        "otp":"1234"
    }
