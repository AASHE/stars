# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Changing field 'ETL.participant_status'
        db.alter_column('etl_export_etl', 'participant_status', self.gf('django.db.models.fields.CharField')(max_length=32, null=True, blank=True))
    
    
    def backwards(self, orm):
        
        # Changing field 'ETL.participant_status'
        db.alter_column('etl_export_etl', 'participant_status', self.gf('django.db.models.fields.CharField')(max_length=8, null=True, blank=True))
    
    
    models = {
        'etl_export.etl': {
            'Meta': {'object_name': 'ETL'},
            'aashe_id': ('django.db.models.fields.IntegerField', [], {}),
            'change_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'current_rating': ('django.db.models.fields.CharField', [], {'max_length': '16', 'null': 'True', 'blank': 'True'}),
            'current_stars_version': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_submission_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'liaison_department': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'liaison_email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'liaison_first_name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'liaison_last_name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'liaison_middle_name': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'liaison_phone': ('django.contrib.localflavor.us.models.PhoneNumberField', [], {}),
            'liaison_title': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'participant_status': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'rating_valid_until': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'submission_due_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'})
        }
    }
    
    complete_apps = ['etl_export']
