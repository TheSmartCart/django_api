from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('enseignes', '0002_magasin'),
    ]

    operations = [
        migrations.RenameField(
            model_name='enseigne',
            old_name='logo',
            new_name='logoUrl',
        ),
        migrations.RemoveField(
            model_name='enseigne',
            name='description',
        ),
        migrations.RemoveField(
            model_name='enseigne',
            name='adresse',
        ),
        migrations.RemoveField(
            model_name='enseigne',
            name='horaires_ouverture',
        ),
    ]
