from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('purchases', '0006_grnheader_grndetail_purchaseorderheader_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchaseorderheader',
            name='converted_purchase',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='source_po', to='purchases.purchaseheader'),
        ),
    ]
