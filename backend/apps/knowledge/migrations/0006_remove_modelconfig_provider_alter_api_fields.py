# Generated manually to remove provider field and make api fields required
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('knowledge', '0005_alter_document_uploaded_by_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='modelconfig',
            name='provider',
        ),
        migrations.AlterField(
            model_name='modelconfig',
            name='api_key',
            field=models.CharField(max_length=500, verbose_name='API密钥'),
        ),
        migrations.AlterField(
            model_name='modelconfig',
            name='api_base_url',
            field=models.URLField(verbose_name='API基础URL'),
        ),
    ]
