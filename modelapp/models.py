from django.contrib.auth.models import User
from django.db import models


class Person(User):
    class Roles(models.TextChoices):
        USER = "user", "User"
        RIDER = "rider", "Rider"
        RESTAURANT_OWNER = "restaurant_owner", "Restaurant Owner"
        NONE = "none", "None"

    role = models.CharField(max_length=100, choices=Roles.choices, default=Roles.NONE)
    phone = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['role']),
        ]

    def __str__(self):
        return self.username + " " + self.email


class User(Person):
    class Meta:
        proxy = True

    class UserPersonManager(models.Manager):
        def get_queryset(self):
            return super().get_queryset().filter(role=Person.Roles.USER)

    objects = UserPersonManager()

    def save(self, *args, **kwargs):
        kwargs['role'] = Person.Roles.USER
        super().save(self, *args, **kwargs)


class Owner(Person):
    class Meta:
        proxy = True

    class OwnerPersonManager(models.Manager):
        def get_queryset(self):
            return super().get_queryset().filter(role=Person.Roles.RESTAURANT_OWNER)

    objects = OwnerPersonManager()

    def save(self, *args, **kwargs):
        kwargs['role'] = Person.Roles.RESTAURANT_OWNER
        super().save(self, *args, **kwargs)


class Rider(Person):
    class Meta:
        proxy = True

    class RiderPersonManager(models.Manager):
        def get_queryset(self):
            return super().get_queryset().filter(role=Person.Roles.RIDER)

    objects = RiderPersonManager()

    def save(self, *args, **kwargs):
        kwargs['role'] = Person.Roles.RIDER
        super().save(self, *args, **kwargs)
