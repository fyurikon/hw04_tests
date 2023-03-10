from django.contrib import admin

from .models import CensoredWord, Group, Post


class PostAdmin(admin.ModelAdmin):
    # Fields visible in the admin panel
    list_display = (
        'pk',
        'text',
        'pub_date',
        'author',
        'group',
    )
    list_editable = ('group',)
    # Fields for search
    search_fields = ('text',)
    # Filters
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'


class GroupAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title', 'description')
    search_fields = ('title', 'description')
    empty_value_display = '-пусто-'


class CensoredWordAdmin(admin.ModelAdmin):
    list_display = ('pk', 'word')
    search_fields = ('word',)
    empty_value_display = '-пусто-'


admin.site.register(Post, PostAdmin)

admin.site.register(Group, GroupAdmin)

admin.site.register(CensoredWord, CensoredWordAdmin)
