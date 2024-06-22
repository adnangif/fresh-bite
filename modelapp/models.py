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


class Restaurant(models.Model):
    owner = models.OneToOneField(Owner, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, blank=True, default='')
    opens_at = models.TimeField(blank=True, default='00:00:00')
    closes_at = models.TimeField(blank=True, default='00:00:00')
    phone = models.CharField(max_length=20, blank=True, default='')
    phone2 = models.CharField(max_length=20, blank=True, default='')

    class Meta:
        indexes = [
            models.Index(fields=['owner']),
        ]

    def __str__(self):
        return self.name + " owned by " + self.owner.email


class Location(models.Model):
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    entity = models.ForeignKey(Person, on_delete=models.CASCADE)

    class Meta:
        indexes = [
            models.Index(fields=['entity']),
        ]

    def __str__(self):
        return str(self.entity.email) + " -> " + str(self.latitude) + " " + str(self.longitude)


class Wallet(models.Model):
    entity = models.OneToOneField(Person, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True, default=0)

    class Meta:
        indexes = [
            models.Index(fields=['entity']),
        ]

    def __str__(self):
        return self.entity.email + " -> " + str(self.amount)


class OrderStatus(models.TextChoices):
    PREPARING = 'PREPARING', 'Preparing'
    RIDER_ON_WAY = 'RIDER_ON_WAY', 'Rider On Way'
    DELIVERED = 'DELIVERED', 'Delivered'
    CANCELLED = 'CANCELLED', 'Cancelled'


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="User")
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE, related_name="Owner")
    rider = models.ForeignKey(Rider, on_delete=models.CASCADE, related_name="Rider")
    status = models.CharField(max_length=100, choices=OrderStatus.choices, blank=True, null=True)

    _total_amount = None

    def total_amount(self):
        if self._total_amount is None:
            items = OrderedItem.objects.filter(order=self)
            amount = 0.0

            for item in items:
                amount += item.price * item.quantity

            self._total_amount = amount

        return self._total_amount

    def __str__(self):
        return (
                str(self.owner.email) + " -> "
                + str(self.rider.email) + " "
                + str(self.user.email) + " "
                + str(self.status)
        )


class Menu(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.name


class MenuItem(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE)
    price = models.IntegerField(default=0)
    image = models.ImageField(upload_to='menu_items/', blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=['menu']),
        ]

    def __str__(self):
        return str(self.menu) + " -> " + self.name + " " + str(self.price)


class OrderedItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        indexes = [
            models.Index(fields=['order'])
        ]

    def __str__(self):
        return str(self.item.name) + " -> " + str(self.quantity)


class Weekdays(models.TextChoices):
    SATURDAY = 'SATURDAY', 'Saturday'
    SUNDAY = 'SUNDAY', 'Sunday'
    MONDAY = 'MONDAY', 'Monday'
    TUESDAY = 'TUESDAY', 'Tuesday'
    WEDNESDAY = 'WEDNESDAY', 'Wednesday'
    THURSDAY = 'THURSDAY', 'Thursday'
    FRIDAY = 'FRIDAY', 'Friday'


class WeeklyHoliday(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    weekday = models.PositiveIntegerField(choices=Weekdays.choices)

    class Meta:
        indexes = [
            models.Index(fields=['restaurant']),
        ]


class ReviewTypes(models.TextChoices):
    RIDER = 'RIDER', 'Rider'
    FOOD = 'FOOD', 'Food'
    PLATFORM = 'PLATFORM', 'Platform'


class Review(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    review_type = models.CharField(max_length=100, choices=ReviewTypes.choices)
    message = models.TextField()
    rating = models.PositiveIntegerField(default=0)

    class Meta:
        indexes = [
            models.Index(fields=['order']),
        ]


class QNA(models.Model):
    question = models.TextField()
    answer = models.TextField()


class Feedback(models.Model):
    email = models.EmailField()
    message = models.TextField()


class TransactionStatuses(models.TextChoices):
    PENDING = 'PENDING', 'Pending'
    ACCEPTED = 'ACCEPTED', 'Accepted'
    REJECTED = 'REJECTED', 'Rejected'


class PaymentTypes(models.TextChoices):
    CASH_ON_DELIVERY = 'CASH_ON_DELIVERY', 'Cash on Delivery'
    STRIPE = 'STRIPE', 'Stripe'


class Transaction(models.Model):
    amount = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    status = models.CharField(max_length=100, choices=TransactionStatuses.choices)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    payment_type = models.CharField(max_length=100, choices=PaymentTypes.choices)

    class Meta:
        indexes = [
            models.Index(fields=['order']),
        ]
