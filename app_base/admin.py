

from django.contrib import admin

from app_base.models import Blog


class BlogAdmin(admin.ModelAdmin):
    list_display = ['title', 'date_created', 'last_modified', 'is_draft']
    list_filter = ['is_draft', 'date_created']
    search_fields = ['title']
    prepopulated_fields = {'slug': ('title',)}
    list_per_page = 50
    actions = ('set_blog_to_published',)
    date_hierarchy = 'date_created'

    def get_ordering(self, request):
        if request.user.is_superuser:
            return 'title', '-date_created',
        return 'title',

    def set_blog_to_published(self, request, queryset):
        count = queryset.update(is_draft=False)
        self.message_user(request, f"The {count} selected blogs has been published")

    set_blog_to_published.short_description = "Mark selected blogs as published"


admin.site.register(Blog, BlogAdmin)
