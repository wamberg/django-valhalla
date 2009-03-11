from django.contrib import admin

class DeedAdmin(admin.ModelAdmin):
    list_display = (
            'deed_date',
            'speaker',
            'text'
    )
