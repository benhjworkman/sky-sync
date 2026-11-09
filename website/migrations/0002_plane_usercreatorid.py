import django.db.models.deletion
from django.db import migrations, models

def get_default_user():
    from django.contrib.auth import get_user_model
    User = get_user_model()
    return User.objects.first().id  # Ensure there is at least one user in the database

class Migration(migrations.Migration):

    dependencies = [
        ('website', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='plane',
            name='userCreatorID',
            field=models.ForeignKey(
                to='auth.User',  # Ensure this points to the correct User model
                on_delete=django.db.models.deletion.CASCADE,
                default=get_default_user,
            ),
            preserve_default=False,
        ),
    ]
