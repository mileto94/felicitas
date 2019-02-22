from django.conf import settings
from django.contrib import admin
from django.contrib.admin.utils import unquote
from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from django.urls import path

from game_rules.forms import AddPollForm, UploadPollsForm
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


class LimitedAdminInlineMixin(object):
    """
    InlineAdmin mixin limiting the selection of related items according to
    criteria which can depend on the current parent object being edited.
    A typical use case would be selecting a subset of related items from
    other inlines, ie. images, to have some relation to other inlines.
    Use as follows::
        class MyInline(LimitedAdminInlineMixin, admin.TabularInline):
            def get_filters(self, obj):
                return (('<field_name>', dict(<filters>)),)
    """

    @staticmethod
    def limit_inline_choices(formset, field, empty=False, qs_attr='filter', **filters):
        """
        This function fetches the queryset with available choices for a given
        `field` and filters it based on the criteria specified in filters,
        unless `empty=True`. In this case, no choices will be made available.
        """
        assert formset.form.base_fields.get(field)

        qs = formset.form.base_fields[field].queryset
        if empty:
            formset.form.base_fields[field].queryset = qs.none()
        else:
            qs = getattr(qs, qs_attr)(**filters)

            formset.form.base_fields[field].queryset = qs

    def get_formset(self, request, obj=None, **kwargs):
        """
        Make sure we can only select variations that relate to the current
        item.
        """
        formset = super(LimitedAdminInlineMixin, self).get_formset(
            request, obj, **kwargs)

        qs_attributes = {
            'filter': self.get_filters(obj),
            'exclude': self.get_excludes(obj)
        }
        for attr, options in qs_attributes.items():

            for (field, filters) in options:
                if obj:
                    self.limit_inline_choices(formset, field, qs_attr=attr, **filters)
                else:
                    self.limit_inline_choices(formset, field, empty=True)

        return formset

    def get_filters(self, obj):
        """
        Return filters for the specified fields. Filters should be in the
        following format::
            (('field_name', {'categories': obj}), ...)
        For this to work, we should either override `get_filters` in a
        subclass or define a `filters` property with the same syntax as this
        one.
        """
        return getattr(self, 'filters', ())

    def get_excludes(self, obj):
        """
        Return filters for the specified fields. Filters should be in the
        following format::
            (('field_name', {'categories': obj}), ...)
        For this to work, we should either override `get_filters` in a
        subclass or define a `filters` property with the same syntax as this
        one.
        """
        return getattr(self, 'excludes', ())


class AnswerAdminInline(LimitedAdminInlineMixin, admin.TabularInline):
    model = Answer
    extra = 1
    fk_name = 'poll'

    def get_filters(self, obj):
        game_id = obj.game_id if obj else 0
        return (('next_poll', {'game_id': game_id}), )

    def get_excludes(self, obj):
        obj_id = obj.id if obj else 0
        return (('next_poll', {'id': obj_id}), )


# @admin.register(DigitAnswer)
# class DigitAnswerAdmin(admin.ModelAdmin):
#     pass


@admin.register(Poll)
class PollAdmin(admin.ModelAdmin):
    list_display = ('title', 'game', 'category', 'difficulty', 'poll_type')
    inlines = [AnswerAdminInline, ]
    list_per_page = 30

    def delete_queryset(self, request, queryset):
        query_ids = list(queryset.values_list('id', flat=True))
        qs = list(queryset)
        queryset.delete()
        for index, obj in enumerate(qs):
            obj.id = query_ids[index]
            obj._update_game_polls()
            cache_key = settings.POLL_DATA_KEY.format(id=obj.id)
            cache.delete(cache_key)
