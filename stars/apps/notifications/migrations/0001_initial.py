# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'EmailTemplate'
        db.create_table('notifications_emailtemplate', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=32)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('content', self.gf('django.db.models.fields.TextField')()),
            ('example_data', self.gf('jsonfield.fields.JSONField')(null=True, blank=True)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('notifications', ['EmailTemplate'])

        # Adding model 'CopyEmail'
        db.create_table('notifications_copyemail', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('template', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['notifications.EmailTemplate'])),
            ('address', self.gf('django.db.models.fields.EmailField')(max_length=75)),
            ('bcc', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('notifications', ['CopyEmail'])


    def backwards(self, orm):
        # Deleting model 'EmailTemplate'
        db.delete_table('notifications_emailtemplate')

        # Deleting model 'CopyEmail'
        db.delete_table('notifications_copyemail')


    models = {
        'notifications.copyemail': {
            'Meta': {'object_name': 'CopyEmail'},
            'address': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'bcc': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'template': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['notifications.EmailTemplate']"})
        },
        'notifications.emailtemplate': {
            'Meta': {'ordering': "('slug',)", 'object_name': 'EmailTemplate'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'content': ('django.db.models.fields.TextField', [], {}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'example_data': ('jsonfield.fields.JSONField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '32'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        }
    }

    complete_apps = ['notifications']