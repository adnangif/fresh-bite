from xml.dom.minidom import Entity

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from .managers import CustomUserManager, UserPersonManager, OwnerPersonManager, RiderPersonManager, Roles


class Person(AbstractUser):
    username = None
    email = models.EmailField(_("email address"), unique=True)
    role = models.CharField(max_length=100, choices=Roles.choices, default=Roles.NONE)
    phone = models.CharField(max_length=25, null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    class Meta:
        indexes = [
            models.Index(fields=['role']),
        ]

    def __str__(self):
        return self.email

    @property
    def is_restaurant_owner(self):
        return self.role == Roles.RESTAURANT_OWNER

    @property
    def is_rider(self):
        return self.role == Roles.RIDER

    @property
    def is_user(self):
        return self.role == Roles.USER


class User(Person):
    class Meta:
        proxy = True

    objects = UserPersonManager()

    def save(self, *args, **kwargs):
        self.role = Roles.USER

        super(User, self).save(*args, **kwargs)


class Owner(Person):
    class Meta:
        proxy = True

    objects = OwnerPersonManager()

    def save(self, *args, **kwargs):
        self.role = Roles.RESTAURANT_OWNER
        super(Owner, self).save(*args, **kwargs)


class Rider(Person):
    class Meta:
        proxy = True

    objects = RiderPersonManager()

    def save(self, *args, **kwargs):
        self.role = Roles.RIDER
        super(Rider, self).save(*args, **kwargs)


class Menu(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.name


class MenuItem(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    image = models.ImageField(upload_to='items', blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return str(self.menu) + " -> " + self.name + " " + str(self.price)


class Location(models.Model):
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    entity = models.ForeignKey(Person, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.entity.email) + " -> " + str(self.latitude) + " " + str(self.longitude)


class Wallet(models.Model):
    entity = models.ForeignKey(Person, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True, default=0)

    def __str__(self):
        return self.entity.email + " -> " + str(self.amount)


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="User")
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE, related_name="Owner")
    rider = models.ForeignKey(Rider, on_delete=models.CASCADE, related_name="Rider")

    status = models.CharField(max_length=100, blank=True, null=True)

    def total_amount(self):
        items = OrderItem.objects.filter(order=self)
        amount = 0.0

        for item in items:
            amount += item.price * item.quantity

        return amount



    def __str__(self):
        return (
                str(self.owner.email) + " -> "
                + str(self.rider.email) + " "
                + str(self.user.email) + " "
                + str(self.status)
                )


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return str(self.item.name) + " -> " + str(self.quantity)


class Restaurant(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    opens_at = models.TimeField(blank=True, null=True)
    closes_at = models.TimeField(blank=True, null=True)

