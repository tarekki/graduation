import django.db.models.deletion
from django.db import migrations, models


def migrate_user_fields(apps, schema_editor):
    User = apps.get_model("accounts", "User")
    Role = apps.get_model("lookups", "Role")

    for u in User.objects.all():
        full = (getattr(u, "full_name", None) or "").strip()
        if not full:
            u.first_name = "User"
            u.last_name = ""
        else:
            parts = full.split(None, 1)
            u.first_name = parts[0][:75]
            u.last_name = (parts[1] if len(parts) > 1 else "")[:75]

        old_code = getattr(u, "role", None)
        if old_code:
            r = Role.objects.filter(code=old_code).first()
            if r:
                u.role_new_id = r.pk
        if not u.role_new_id:
            owner = Role.objects.filter(code="OWNER").first()
            u.role_new_id = owner.pk if owner else Role.objects.first().pk
        u.save()


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0001_initial"),
        ("lookups", "0002_seed_lookups"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="first_name",
            field=models.CharField(max_length=75, default=""),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="user",
            name="last_name",
            field=models.CharField(max_length=75, default=""),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="user",
            name="role_new",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="lookups.role",
            ),
        ),
        migrations.RunPython(migrate_user_fields, migrations.RunPython.noop),
        migrations.RemoveField(model_name="user", name="full_name"),
        migrations.RemoveField(model_name="user", name="role"),
        migrations.RenameField(model_name="user", old_name="role_new", new_name="role"),
        migrations.AlterField(
            model_name="user",
            name="role",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="users",
                to="lookups.role",
            ),
        ),
    ]
