# -*- coding: utf-8 -*-

from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from profiles.user_manager import UserManager


class SingleLineTextField(models.TextField):
    pass


class User(AbstractBaseUser, PermissionsMixin):
    objects = UserManager()
    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created at')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Updated at')
    )

    email = models.EmailField(
        unique=True,
        verbose_name=_('Email')
    )
    first_name = SingleLineTextField(
        blank=True,
        null=True,
        verbose_name=_('First name')
    )
    last_name = SingleLineTextField(
        blank=True,
        null=True,
        verbose_name=_('Last name')
    )
    date_joined = models.DateTimeField(
        default=timezone.now,
        verbose_name=_('Date joined')
    )
    is_staff = models.BooleanField(
        _('Staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this site.'),
    )
    is_active = models.BooleanField(
        _('Active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. ' +
            'Unselect this instead of deleting accounts.'
        ),
    )

    def __str__(self):
        return self.get_short_name()

    def get_full_name(self):
        return '%s %s' % (self.first_name, self.last_name)

    def get_short_name(self):
        return self.first_name if self.first_name else self.email

    class Meta:
        ordering = ('email',)
        verbose_name = _('User')
        verbose_name_plural = _('Users')


class Profile(models.Model):
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created at')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Updated at')
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        models.CASCADE,
        related_name='profile',
        verbose_name=_('User')
    )
    preferences = JSONField(
        default={},
        verbose_name=_('Preferences')
    )

    def __str__(self):
        return self.user.get_short_name()

    class Meta:
        ordering = ('user',)
        verbose_name = _('Profile')
        verbose_name_plural = _('Profiles')
