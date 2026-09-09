from pathlib import Path
p=Path('backend/app/models.py').read_text()
models=['User','UserRole','Person','Hall','Group','TrainingSchedule','Athlete','GroupMembership','FamilyLink','JoinCode','Application','Message','Notification','Attendance','Achievement','RatingHistory','Page','PageVersion','AuditLog']
missing=[x for x in models if f'class {x}(' not in p]
if missing: raise SystemExit('Models missing: '+', '.join(missing))
print('Model contract: OK')
