# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-12-01 20:12
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Chatroom',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=255, null=True)),
                ('hasProject', models.BooleanField(default=False)),
                ('isDirectMessage', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='Chattext',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('content', models.CharField(default='', max_length=2000)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='author_char', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Project Chat',
                'ordering': ('-date',),
            },
        ),
        migrations.CreateModel(
            name='DirectMessage',
            fields=[
                ('chatroom_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='chat.Chatroom')),
            ],
            bases=('chat.chatroom',),
        ),
        migrations.AddField(
            model_name='chattext',
            name='room',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='chat', to='chat.Chatroom'),
        ),
        migrations.AddField(
            model_name='chatroom',
            name='user',
            field=models.ManyToManyField(related_name='rooms', to=settings.AUTH_USER_MODEL),
        ),
    ]
