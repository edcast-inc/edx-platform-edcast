# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'CmGradebook.gb_type'
        db.delete_column('cm_plugin_cmgradebook', 'gb_type')


    def backwards(self, orm):
        # Adding field 'CmGradebook.gb_type'
        db.add_column('cm_plugin_cmgradebook', 'gb_type',
                      self.gf('django.db.models.fields.CharField')(default='blank', max_length=200),
                      keep_default=False)


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'cm_plugin.cmgradebook': {
            'Meta': {'object_name': 'CmGradebook'},
            'count_per_gradebook': ('django.db.models.fields.IntegerField', [], {'default': '100'}),
            'course_id': ('xmodule_django.models.CourseKeyField', [], {'max_length': '255'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'current_page': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'gb_format': ('django.db.models.fields.CharField', [], {'default': "'CSV'", 'max_length': '100'}),
            'headers': ('django.db.models.fields.TextField', [], {}),
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
            'user_id': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
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
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['cm_plugin']