# -*- coding: utf-8 -*-

from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.db.models import F
from django.forms import TextInput
from django.utils.translation import ugettext_lazy as _

from .forms import UserCreationForm
from .models import NLURequest, Profile, User


@admin.register(User)
class UserAdmin(auth_admin.UserAdmin):
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2')}
        ),
    )
    add_form = UserCreationForm
    exclude = ('username',)
    fieldsets = auth_admin.UserAdmin.fieldsets
    fieldsets[0][1]['fields'] = ('email', 'password')
    fieldsets[1][1]['fields'] = ('first_name', 'last_name')
    list_display = ('email', 'first_name', 'last_name', 'is_active',
                    'is_staff')
    ordering = ('email',)
    search_fields = ('email', 'first_name', 'last_name',)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['user', 'preferences']}),
    ]
    list_display = ('user',)
    ordering = ('user',)


@admin.register(NLURequest)
class NLURequestAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        return NLURequest.objects.annotate(response_time=F('updated_at') - F('created_at'))

    def show_response_time(self, inst):
        return inst.response_time

    fieldsets = [
        (None, {'fields': ['user', 'params', 'nlu_model_output',
                           'intent_output', 'answer']}),
    ]
    list_display = ('user', 'params', 'nlu_model_output', 'intent_output',
                    'answer', 'show_response_time')
    list_filter = ('user', 'updated_at')
    ordering = ('-updated_at',)
    readonly_fields = ('user', 'params', 'nlu_model_output', 'intent_output',
                       'answer', 'updated_at')
    show_response_time.admin_order_field = 'response_time'
    show_response_time.short_description = _('Response time')
