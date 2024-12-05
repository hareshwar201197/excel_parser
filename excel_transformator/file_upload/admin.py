from django.contrib import admin

from .models import Companies, Lob, Categories


# Register your models here.

class CompaniesAdmin(admin.ModelAdmin):
    list_display = [field.attname for field in Companies._meta.fields]

class LobAdmin(admin.ModelAdmin):
    list_display = [field.attname for field in Lob._meta.fields]

class CategoriesAdmin(admin.ModelAdmin):
    list_display = [field.attname for field in Categories._meta.fields]


admin.site.register(Companies, CompaniesAdmin)
admin.site.register(Lob, LobAdmin)
admin.site.register(Categories, CategoriesAdmin)

