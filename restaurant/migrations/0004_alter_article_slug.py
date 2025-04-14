from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('restaurant', '0003_alter_article_slug'),
    ]

    operations = [
        migrations.AlterField(
            model_name='Article',
            name='slug',
            field=models.SlugField(max_length=100, unique=True, blank=True),
        ),
    ]