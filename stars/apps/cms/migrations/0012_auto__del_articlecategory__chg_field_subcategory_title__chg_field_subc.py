# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting model 'ArticleCategory'
        db.delete_table('cms_articlecategory')

        # Changing field 'Subcategory.title'
        db.alter_column('cms_subcategory', 'title', self.gf('django.db.models.fields.CharField')(max_length=64))

        # Changing field 'Subcategory.content'
        db.alter_column('cms_subcategory', 'content', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'Category.title'
        db.alter_column('cms_category', 'title', self.gf('django.db.models.fields.CharField')(max_length=64))

        # Changing field 'Category.content'
        db.alter_column('cms_category', 'content', self.gf('django.db.models.fields.TextField')(null=True))


    def backwards(self, orm):
        
        # Adding model 'ArticleCategory'
        db.create_table('cms_articlecategory', (
            ('ordinal', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('depth', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('term_id', self.gf('django.db.models.fields.IntegerField')(unique=True, primary_key=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50, db_index=True)),
            ('parent_term', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=30)),
        ))
        db.send_create_signal('cms', ['ArticleCategory'])

        # Changing field 'Subcategory.title'
        db.alter_column('cms_subcategory', 'title', self.gf('django.db.models.fields.CharField')(max_length=32))

        # Changing field 'Subcategory.content'
        db.alter_column('cms_subcategory', 'content', self.gf('django.db.models.fields.TextField')(default=' '))

        # Changing field 'Category.title'
        db.alter_column('cms_category', 'title', self.gf('django.db.models.fields.CharField')(max_length=32))

        # Changing field 'Category.content'
        db.alter_column('cms_category', 'content', self.gf('django.db.models.fields.TextField')(default=' '))


    models = {
        'cms.category': {
            'Meta': {'object_name': 'Category'},
            'content': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ordinal': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'published': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        },
        'cms.newarticle': {
            'Meta': {'ordering': "('ordinal', 'title', 'timestamp')", 'object_name': 'NewArticle'},
            'categories': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['cms.Category']", 'null': 'True', 'blank': 'True'}),
            'content': ('django.db.models.fields.TextField', [], {}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'irc_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'ordinal': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'published': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255', 'db_index': 'True'}),
            'subcategories': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['cms.Subcategory']", 'null': 'True', 'blank': 'True'}),
            'teaser': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'cms.subcategory': {
            'Meta': {'object_name': 'Subcategory'},
            'content': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ordinal': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cms.Category']"}),
            'published': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        }
    }

    complete_apps = ['cms']