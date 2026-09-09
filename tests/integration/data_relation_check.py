from pathlib import Path
s=Path('backend/app/models.py').read_text(encoding='utf-8')
for model in ['User','Person','Athlete','FamilyLink','GroupMembership','Group','Hall','TrainingSchedule','Application','Message','Attendance','Achievement','RatingHistory']:
    assert f'class {model}' in s, f'model missing: {model}'
print('Federation data relations contract: OK')
