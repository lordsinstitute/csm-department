
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_cleanup'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userregistrationmodel',
            name='status',
            field=models.CharField(default='waiting', max_length=100),
        ),
    ]
