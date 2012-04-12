from django.contrib import admin
import models

class TemplateRegionInline(admin.StackedInline):
    model = models.TemplateRegion

class TemplateAdmin(admin.ModelAdmin):
    inlines = [TemplateRegionInline]

class CompositionRegionInline(admin.StackedInline):
    model = models.CompositionRegion

class CompositionAdmin(admin.ModelAdmin):
    inlines = [CompositionRegionInline]

admin.site.register(models.TemplateFont)
admin.site.register(models.Template, TemplateAdmin)
admin.site.register(models.Composition, CompositionAdmin)
