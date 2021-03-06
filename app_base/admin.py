from django.contrib import admin
from django.db.models import Count
from django.utils import timezone
from import_export.admin import ImportExportModelAdmin
from rangefilter.filter import DateRangeFilter

from app_base.models import Blog, Comment, Category
from django_summernote.admin import SummernoteModelAdmin
from django_admin_listfilter_dropdown.filters import RelatedDropdownFilter

from app_base.resources import CommentResource




class CommentInline(admin.TabularInline):
    model = Comment
    fields = ('text', 'is_active')
    extra = 1
    classes = ('collapse',)


class BlogAdmin(SummernoteModelAdmin):
    summernote_fields = ('body',)
    list_display = ['title', 'date_created', 'last_modified', 'is_draft', 'days_since_creation', 'no_of_comments']
    list_filter = ['is_draft', 'date_created']
    search_fields = ['title']
    prepopulated_fields = {'slug': ('title',)}
    list_per_page = 50
    actions = ('set_blog_to_published',)
    date_hierarchy = 'date_created'
    # fields = [('title', 'slug'), 'body', 'is_draft']
    fieldsets = (
        (None, {'fields': (('title', 'slug'), 'body')}),
        (
            'Advanced options', {
                'fields': ('is_draft', 'categories'),
                'description': 'Short description here', 'classes': ('collapse',)}),
    )
    inlines = (CommentInline,)
    filter_vertical = ('categories',)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(comment_count=Count('comments'))
        return queryset

    @staticmethod
    def days_since_creation(blog):
        diff = timezone.now() - blog.date_created
        return diff.days

    @staticmethod
    def no_of_comments(blog):
        return blog.comment_count

    no_of_comments.admin_order_fields = 'comment_count'

    def get_ordering(self, request):
        if request.user.is_superuser:
            return 'title', '-date_created',
        return 'title',

    def set_blog_to_published(self, request, queryset):
        count = queryset.update(is_draft=False)
        self.message_user(request, f"The {count} selected blogs has been published")

    set_blog_to_published.short_description = "Mark selected blogs as published"


class CommentAdmin(ImportExportModelAdmin):
    list_display = ('blog', 'text', 'date_created', 'is_active')
    list_editable = ('text', 'is_active')
    list_filter = (('blog', RelatedDropdownFilter), ('date_created', DateRangeFilter),)
    resource_class = CommentResource


admin.site.register(Blog, BlogAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Category, )
