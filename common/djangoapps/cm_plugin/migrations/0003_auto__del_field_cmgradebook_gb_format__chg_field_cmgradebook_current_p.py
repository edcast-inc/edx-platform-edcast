# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'CmGradebook.gb_format'
        db.delete_column('cm_plugin_cmgradebook', 'gb_format')


        # Changing field 'CmGradebook.current_page'
        db.alter_column('cm_plugin_cmgradebook', 'current_page', self.gf('django.db.models.fields.IntegerField')(null=True))

        # Changing field 'CmGradebook.headers'
        db.alter_column('cm_plugin_cmgradebook', 'headers', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'CmGradebook.course_id'
        db.alter_column('cm_plugin_cmgradebook', 'course_id', self.gf('django.db.models.fields.CharField')(max_length=255))
        # Deleting field 'CmGradebookRecords.user_id'
        db.delete_column('cm_plugin_cmgradebookrecords', 'user_id_id')

        # Adding field 'CmGradebookRecords.user_email'
        db.add_column('cm_plugin_cmgradebookrecords', 'user_email',
                      self.gf('django.db.models.fields.EmailField')(default=None, max_length=75),
                      keep_default=False)


    def backwards(self, orm):
        # Adding field 'CmGradebook.gb_format'
        db.add_column('cm_plugin_cmgradebook', 'gb_format',
                      self.gf('django.db.models.fields.CharField')(default='CSV', max_length=100),
                      keep_default=False)


        # Changing field 'CmGradebook.current_page'
        db.alter_column('cm_plugin_cmgradebook', 'current_page', self.gf('django.db.models.fields.IntegerField')())

        # Changing field 'CmGradebook.headers'
        db.alter_column('cm_plugin_cmgradebook', 'headers', self.gf('django.db.models.fields.TextField')(default=None))

        # Changing field 'CmGradebook.course_id'
        db.alter_column('cm_plugin_cmgradebook', 'course_id', self.gf('xmodule_django.models.CourseKeyField')(max_length=255))
        # Adding field 'CmGradebookRecords.user_id'
        db.add_column('cm_plugin_cmgradebookrecords', 'user_id',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['auth.User']),
                      keep_default=False)

        # Deleting field 'CmGradebookRecords.user_email'
        db.delete_column('cm_plugin_cmgradebookrecords', 'user_email')


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
            'score': ('django.db.models.fields.FloatField', [], {}),
            'unit_name': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
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