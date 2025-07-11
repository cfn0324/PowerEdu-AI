from django.contrib import admin

from .models import Course, Chapter, Video, Comment, UserHub


class ChapterInline(admin.StackedInline):
    model = Chapter
    extra = 0


class VideoInline(admin.StackedInline):
    model = Video
    extra = 0


class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'briefly', 'level', 'study_number', 'label', 'sort_number')
    search_fields = ('name',)
    inlines = [ChapterInline]
    fieldsets = (
        (None, {
            'fields': ('name', 'briefly', 'level', 'tell', 'label', 'image', 'sort_number')
        }),
    )


class ChapterAdmin(admin.ModelAdmin):
    list_display = ('name', 'briefly', 'course', 'sort_number')
    search_fields = ('name',)
    inlines = [VideoInline]
    list_filter = ('course',)


class VideoAdmin(admin.ModelAdmin):
    list_display = ('title', 'chapter',)
    search_fields = ('title',)


class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'content',)
    search_fields = ('user__username', 'course__name',)


class UserHubAdmin(admin.ModelAdmin):
    list_display = ('user', 'act_type', 'course',)
    search_fields = ('user__username', 'course__name',)
    list_filter = ('act_type',)


admin.site.register(Course, CourseAdmin)
admin.site.register(Chapter, ChapterAdmin)
admin.site.register(Video, VideoAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(UserHub, UserHubAdmin)

