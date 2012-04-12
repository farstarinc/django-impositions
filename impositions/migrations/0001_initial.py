# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'TemplateFont'
        db.create_table('impositions_templatefont', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('font_file', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
        ))
        db.send_create_signal('impositions', ['TemplateFont'])

        # Adding model 'Template'
        db.create_table('impositions_template', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('file', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
        ))
        db.send_create_signal('impositions', ['Template'])

        # Adding model 'TemplateImage'
        db.create_table('impositions_templateimage', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('file', self.gf('django.db.models.fields.files.ImageField')(max_length=100)),
        ))
        db.send_create_signal('impositions', ['TemplateImage'])

        # Adding model 'TemplateRegion'
        db.create_table('impositions_templateregion', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('template', self.gf('django.db.models.fields.related.ForeignKey')(related_name='regions', to=orm['impositions.Template'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=150)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('content_type', self.gf('django.db.models.fields.CharField')(max_length=16)),
            ('top', self.gf('django.db.models.fields.IntegerField')()),
            ('left', self.gf('django.db.models.fields.IntegerField')()),
            ('width', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('height', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('allowed_fonts', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('allowed_colors', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('allowed_font_sizes', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('allow_markup', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('text_style', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('justify', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('crop', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('default_value', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('impositions', ['TemplateRegion'])

        # Adding M2M table for field allowed_images on 'TemplateRegion'
        db.create_table('impositions_templateregion_allowed_images', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('templateregion', models.ForeignKey(orm['impositions.templateregion'], null=False)),
            ('templateimage', models.ForeignKey(orm['impositions.templateimage'], null=False))
        ))
        db.create_unique('impositions_templateregion_allowed_images', ['templateregion_id', 'templateimage_id'])

        # Adding model 'Composition'
        db.create_table('impositions_composition', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('template', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['impositions.Template'])),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal('impositions', ['Composition'])

        # Adding model 'CompositionRegion'
        db.create_table('impositions_compositionregion', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('comp', self.gf('django.db.models.fields.related.ForeignKey')(related_name='regions', to=orm['impositions.Composition'])),
            ('template_region', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['impositions.TemplateRegion'])),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=100, blank=True)),
            ('text', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('font', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('font_size', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=8, decimal_places=2, blank=True)),
            ('bg_color', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('fg_color', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('border_color', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('border_size', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal('impositions', ['CompositionRegion'])

    def backwards(self, orm):
        # Deleting model 'TemplateFont'
        db.delete_table('impositions_templatefont')

        # Deleting model 'Template'
        db.delete_table('impositions_template')

        # Deleting model 'TemplateImage'
        db.delete_table('impositions_templateimage')

        # Deleting model 'TemplateRegion'
        db.delete_table('impositions_templateregion')

        # Removing M2M table for field allowed_images on 'TemplateRegion'
        db.delete_table('impositions_templateregion_allowed_images')

        # Deleting model 'Composition'
        db.delete_table('impositions_composition')

        # Deleting model 'CompositionRegion'
        db.delete_table('impositions_compositionregion')

    models = {
        'impositions.composition': {
            'Meta': {'object_name': 'Composition'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'template': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['impositions.Template']"})
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
        'impositions.template': {
            'Meta': {'object_name': 'Template'},
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'impositions.templatefont': {
            'Meta': {'object_name': 'TemplateFont'},
            'font_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
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
            'allowed_colors': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'allowed_font_sizes': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'allowed_fonts': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'allowed_images': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['impositions.TemplateImage']", 'symmetrical': 'False', 'blank': 'True'}),
            'content_type': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'crop': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'default_value': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'height': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'justify': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'left': ('django.db.models.fields.IntegerField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'template': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'regions'", 'to': "orm['impositions.Template']"}),
            'text_style': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'top': ('django.db.models.fields.IntegerField', [], {}),
            'width': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['impositions']