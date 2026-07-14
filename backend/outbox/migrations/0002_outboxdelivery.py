import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('outbox', '0001_initial')]

    operations = [
        migrations.CreateModel(
            name='OutboxDelivery',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('handler', models.CharField(max_length=150)),
                ('result', models.JSONField(blank=True, default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('message', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='deliveries', to='outbox.outboxmessage')),
            ],
        ),
        migrations.AddConstraint(
            model_name='outboxdelivery',
            constraint=models.UniqueConstraint(fields=('message', 'handler'), name='uniq_outbox_message_handler'),
        ),
    ]
