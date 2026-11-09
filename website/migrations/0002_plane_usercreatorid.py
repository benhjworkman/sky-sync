
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='plane',
            name='userCreatorID',
            field=models.ForeignKey(
                to='auth.User',
                on_delete=django.db.models.deletion.CASCADE,
                null=True,
            ),
        ),
    ]
