from __future__ import unicode_literals

from django.db import models
from django.core.validators import *

from django.contrib.auth.models import User, Group

from django.contrib import admin

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import base64

class Event(models.Model):
    eventtype = models.CharField(max_length=1000, blank=False)
    timestamp = models.DateTimeField()
    userid = models.CharField(max_length=1000, blank=True)
    requestor = models.GenericIPAddressField(blank=False)

    def __str__(self):
        return str(self.eventtype)

class EventAdmin(admin.ModelAdmin):
    list_display = ('eventtype', 'timestamp')

class ApiKey(models.Model):
    owner = models.CharField(max_length=1000, blank=False)
    key = models.CharField(max_length=5000, blank=False)

    def __str__(self):
        return str(self.owner) + str(self.key)

class ApiKeyAdmin(admin.ModelAdmin):
    list_display = ('owner','key')



def validate_even(value):
    if value >= 10:
        raise ValidationError(
            _('%(value)s is not an even number'),
            params={'value': value},
        )


class Dog(models.Model):
    name = models.CharField(max_length=1000, blank=False)
    age = models.CharField(max_length=5000, blank=False)
    breed = models.ForeignKey('Breed')
    gender = models.CharField(max_length=5000, blank=False)
    color = models.CharField(max_length=1000, blank=False)
    favoritefood = models.CharField(max_length=5000, blank=False)
    favoritetoy = models.CharField(max_length=5000, blank=False)

class Breed(models.Model):
    name = models.CharField(max_length=1000, blank=False)
    DogSize_CHOICES = (
       ('TINY',  'VerySmall'),
       ('SMALL', 'Small'),
       ('MEDIUM', 'Medium'),
       ('LARGE', 'Large')
    )
    size = models.CharField(
       max_length=50,
      choices=DogSize_CHOICES,
       )
    friendliness = models.IntegerField(validators=[validate_even])
    trainability = models.IntegerField(validators=[validate_even])
    sheddingamount = models.IntegerField(validators=[validate_even])
    exerciseneeds = models.IntegerField(validators=[validate_even])
