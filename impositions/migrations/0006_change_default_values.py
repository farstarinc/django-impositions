# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'TemplateRegion.default_value'
        db.delete_column('impositions_templateregion', 'default_value')

        # Adding field 'TemplateRegion.default_text'
        db.add_column('impositions_templateregion', 'default_text',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)

        # Adding field 'TemplateRegion.default_image'
        db.add_column('impositions_templateregion', 'default_image',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True),
                      keep_default=False)

    def backwards(self, orm):
        # Adding field 'TemplateRegion.default_value'
        db.add_column('impositions_templateregion', 'default_value',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)

        # Deleting field 'TemplateRegion.default_text'
        db.delete_column('impositions_templateregion', 'default_text')

        # Deleting field 'TemplateRegion.default_image'
        db.delete_column('impositions_templateregion', 'default_image')

    models = {
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'impositions.composition': {
            'Meta': {'object_name': 'Composition'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'template': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['impositions.Template']"})
        },
        'impositions.compositiondatasource': {
            'Meta': {'object_name': 'CompositionDataSource'},
            'composition': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'data_sources'", 'to': "orm['impositions.Composition']"}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'loader': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['impositions.DataLoader']"}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        'impositions.compositionregion': {
            'Meta': {'object_name': 'CompositionRegion'},
            'bg_color': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'border_color': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'border_size': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'comp': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'regions'", 'to': "orm['impositions.Composition']"}),
            'fg_color': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'font': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'font_size': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '8', 'decimal_places': '2', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'template_region': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['impositions.TemplateRegion']"}),
            'text': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        'impositions.dataloader': {
            'Meta': {'object_name': 'DataLoader'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'path': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'prefix': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        'impositions.template': {
            'Meta': {'object_name': 'Template'},
            'color_palette': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'data_loaders': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['impositions.DataLoader']", 'symmetrical': 'False', 'blank': 'True'}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'fonts': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'impositions.templateimage': {
            'Meta': {'object_name': 'TemplateImage'},
            'file': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'impositions.templateregion': {
            'Meta': {'object_name': 'TemplateRegion'},
            'allow_markup': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allowed_colors': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'allowed_font_sizes': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'allowed_fonts': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'allowed_images': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['impositions.TemplateImage']", 'symmetrical': 'False', 'blank': 'True'}),
            'content_type': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'crop': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'default_image': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'default_text': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'height': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'left': ('django.db.models.fields.IntegerField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'default': "'Unnamed Region'", 'max_length': '150'}),
            'template': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'regions'", 'to': "orm['impositions.Template']"}),
            'text_align': ('django.db.models.fields.CharField', [], {'default': "'LEFT'", 'max_length': '20', 'blank': 'True'}),
            'text_style': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'top': ('django.db.models.fields.IntegerField', [], {}),
            'width': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['impositions']