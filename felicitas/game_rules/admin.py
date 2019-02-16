from django.contrib import admin
from django.contrib.admin.utils import unquote
from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from django.urls import path

from game_rules.forms import AddPollForm, UploadPollsForm, AddAnswerFormSet, AddAnswerForm
from game_rules.models import GameType, Poll, Answer, Category #, DigitAnswer
from game_rules.utils import upload_polls_from_file


@admin.register(GameType)
class GameTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'pk', 'is_active', 'polls_count', 'created_by')
    list_editable = ('is_active', 'polls_count')
    readonly_fields = ('created_by', )

    def save_model(self, request, game_type, form, change):
        if not game_type.id:
            game_type.created_by = request.user
        game_type.save()

    def get_urls(self):
        return [
            path(
                '<game_id>/polls/upload/',
                self.admin_site.admin_view(self.upload_polls),
                name='upload_polls',
            ),
            path(
                '<game_id>/polls/add/',
                self.admin_site.admin_view(self.add_polls),
                name='add_polls',
            ),
        ] + super().get_urls()

    def add_polls(self, request, game_id):
        if not request.user.has_perms('add_polls'):
            raise PermissionDenied
        game = self.get_object(request, unquote(game_id))

        if request.method == 'POST':
            form = AddPollForm(request.POST)
            if form.is_valid():
                pass
        else:
            form = AddPollForm()

        return render(request, 'game_rules/add_polls.html', {'form': form})

    def upload_polls(self, request, game_id):
        if not request.user.has_perms('add_polls'):
            raise PermissionDenied
        # game = self.get_object(request, unquote(game_id))

        if request.method == 'POST':
            form = UploadPollsForm(files=request.FILES)
            if form.is_valid():
                upload_polls_from_file(game_id, request.FILES.get('polls_file'))
        else:
            form = UploadPollsForm()

        return render(request, 'game_rules/upload_polls.html', {'form': form})


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    pass


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    model = Answer


class AnswerAdminInline(admin.TabularInline):
    model = Answer
    extra = 1

# @admin.register(DigitAnswer)
# class DigitAnswerAdmin(admin.ModelAdmin):
#     pass


@admin.register(Poll)
class PollAdmin(admin.ModelAdmin):
    list_display = ('title', 'game', 'category', 'difficulty', 'poll_type')
    inlines = [AnswerAdminInline, ]

    def delete_queryset(self, request, queryset):
        query_ids = list(queryset.values_list('id', flat=True))
        qs = list(queryset)
        queryset.delete()
        for index, obj in enumerate(qs):
            obj.id = query_ids[index]
            obj._update_game_polls()
