from __future__ import unicode_literals

from django.db import migrations, models


def fix_rated_reports(apps, schema_editor):
    Inst = apps.get_model('institutions', 'Institution')
    for i in Inst.objects.all():
        if i.rated_submission is None and i.latest_expired_submission is not None:
            i.rated_submission = i.latest_expired_submission
            i.save()


class Migration(migrations.Migration):

    dependencies = [
        ('institutions', '0003_auto_20190612_0938'),
    ]

    operations = [
        migrations.RunPython(fix_rated_reports),
    ]
