from django.contrib import admin
from .models import User, Banner, Feedback
from django.utils.html import format_html

# 导入成就相关admin
from .achievement_admin import *

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'nickname', 'avatar')
    search_fields = ('username', 'nickname')
    list_filter = ('username',)
    ordering = ('-id',)


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ('image', 'to_id', 'sort_number')
    ordering = ('sort_number',)


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('user', 'content', 'status', 'phone')
    list_filter = ('status',)
    ordering = ('-id',)


admin.site.site_header = "电力知识库与在线学习平台后台"
admin.site.site_index = "电力知识库与在线学习平台后台"
admin.site.site_title = "电力知识库与在线学习平台后台"

