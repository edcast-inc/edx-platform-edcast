# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding index on 'CmGradebookRecords', fields ['user_email']
        db.create_index('cm_plugin_cmgradebookrecords', ['user_email', 'unit_name', 'cm_gradebook_id'], unique=True)


    def backwards(self, orm):
        # Removing index on 'CmGradebookRecords', fields ['user_email']
        db.delete_index('cm_plugin_cmgradebookrecords', ['user_email', 'unit_name', 'cm_gradebook_id'])


    models = {
        'cm_plugin.cmgradebook': {
            'Meta': {'object_name': 'CmGradebook'},
            'count_per_gradebook': ('django.db.models.fields.IntegerField', [], {'default': '100'}),
            'course_id': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'current_page': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True'}),
            'headers': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'default': "'pending'", 'max_length': '100'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'cm_plugin.cmgradebookrecords': {
            'Meta': {'object_name': 'CmGradebookRecords'},
            'cm_gradebook': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cm_plugin.CmGradebook']"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'score': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'unit_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'user_email': ('django.db.models.fields.EmailField', [], {'max_length': '75'})
        },
        'cm_plugin.healthcheck': {
            'Meta': {'object_name': 'HealthCheck'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'test': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'cm_plugin.xmodule_metadata_cache': {
            'Meta': {'object_name': 'XModule_Metadata_Cache'},
            'cm_id': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'course': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'due': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'obj_type': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'posted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'start': ('django.db.models.fields.DateTimeField', [], {}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'url': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'video_url': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'})
        }
    }

    complete_apps = ['cm_plugin']