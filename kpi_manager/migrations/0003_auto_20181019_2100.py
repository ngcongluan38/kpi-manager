# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2018-10-19 14:00
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('kpi_manager', '0002_profile_position'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tagperiod',
            name='created_by',
        ),
        migrations.RemoveField(
            model_name='tagperiod',
            name='user',
        ),
        migrations.AlterModelOptions(
            name='tag',
            options={'ordering': ('-created_at',)},
        ),
        migrations.RenameField(
            model_name='department',
            old_name='name',
            new_name='department_name',
        ),
        migrations.RenameField(
            model_name='task',
            old_name='description',
            new_name='task_description',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='name',
        ),
        migrations.RemoveField(
            model_name='tag',
            name='name',
        ),
        migrations.RemoveField(
            model_name='tag',
            name='tag_period',
        ),
        migrations.RemoveField(
            model_name='task',
            name='name',
        ),
        migrations.RemoveField(
            model_name='task',
            name='tag_period',
        ),
        migrations.AddField(
            model_name='profile',
            name='full_name',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name='tag',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='tag',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='tag',
            name='period_end',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='tag',
            name='period_start',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='tag',
            name='state',
            field=models.CharField(blank=True, choices=[('NF', 'Chưa Hoàn Thành'), ('PR', 'Đang Thực Hiện'), ('CO', 'Hoàn Thành')], max_length=2, null=True),
        ),
        migrations.AddField(
            model_name='tag',
            name='tag_description',
            field=models.TextField(blank=True, max_length=2000, null=True),
        ),
        migrations.AddField(
            model_name='tag',
            name='tag_name',
            field=models.TextField(blank=True, max_length=500, null=True),
        ),
        migrations.AddField(
            model_name='tag',
            name='target_num',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
        migrations.AddField(
            model_name='tag',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='tag',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='tag',
            name='weight',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
        migrations.AddField(
            model_name='task',
            name='tag',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='kpi_manager.Tag'),
        ),
        migrations.AddField(
            model_name='task',
            name='task_name',
            field=models.TextField(blank=True, max_length=500, null=True),
        ),
        migrations.DeleteModel(
            name='TagPeriod',
        ),
    ]