import stripe
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.transaction import atomic
from django.utils.translation import gettext_lazy as _
from .managers import CustomUserManager, UserPersonManager, OwnerPersonManager, RiderPersonManager, Roles, OrderManager


class Person(AbstractUser):
    username = None
    email = models.EmailField(_("email address"), unique=True)
    role = models.CharField(max_length=100, choices=Roles.choices, default=Roles.NONE)
    phone = models.CharField(max_length=25, blank=True, default='')

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

    def get_location(self):
        location: Location = Location.objects.filter(entity=self).last()
        if location:
            return location.location_in_string
        else:
            return ''

    def get_latitude(self):
        location: Location = Location.objects.filter(entity=self).last()
        if location:
            return location.latitude
        else:
            return ''

    def get_longitude(self):
        location: Location = Location.objects.filter(entity=self).last()
        if location:
            return location.longitude
        else:
            return ''

    def get_location_object(self):
        location: Location = Location.objects.get_or_create(entity=self)[0]
        return location


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
    opens_at = models.TimeField(default='00:00:00')
    closes_at = models.TimeField(default='00:00:00')
    phone = models.CharField(max_length=20, blank=True, default='')
    phone2 = models.CharField(max_length=20, blank=True, default='')
    total_rating = models.IntegerField(default=0)
    total_rating_population = models.IntegerField(default=0)
    average_rating = models.FloatField(default=0)
    restaurant_image = models.ImageField(upload_to='restaurant_images/', null=True, blank=True)
    is_published = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=['owner']),
        ]

    def __str__(self):
        return self.name + " owned by " + self.owner.email

    def get_location(self):
        return self.owner.get_location()

    def get_latitude(self):
        return self.owner.get_latitude()

    def get_longitude(self):
        return self.owner.get_longitude()

    def get_location_object(self):
        return self.owner.get_location_object()

    def get_delivery_zones(self):
        return DeliveryZone.objects.filter(restaurant=self)

    def set_rating(self, rating: int):
        self.total_rating += rating
        self.total_rating_population += 1
        self.save()

        if self.total_rating and self.total_rating_population:
            self.avg_rating = round(self.total_rating / self.total_rating_population, 1)
            self.save()


class DeliveryZone(models.Model):
    latitude = models.DecimalField(max_digits=9, decimal_places=6, default=0)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, default=0)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    location_in_string = models.CharField(max_length=500, blank=True, default='')

    class Meta:
        indexes = [
            models.Index(fields=['restaurant'])
        ]

    def __str__(self):
        return str(self.restaurant.name) + ' -> ' + self.location_in_string + f'[{self.latitude}, {self.longitude}]'


class Location(models.Model):
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    entity = models.ForeignKey(Person, on_delete=models.CASCADE)
    location_in_string = models.CharField(max_length=500, blank=True, default='')

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
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, null=True, blank=True)
    rider = models.ForeignKey(Rider, on_delete=models.CASCADE, related_name="Rider")
    status = models.CharField(max_length=100, choices=OrderStatus.choices, default=OrderStatus.PREPARING)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    is_rated = models.BooleanField(default=False)

    rider_otp = models.IntegerField(blank=True, null=True)
    user_otp = models.IntegerField(blank=True, null=True)

    _total_amount = None
    objects = OrderManager()

    def get_status(self):
        return OrderStatus(self.status).label

    def mark_as_rider_on_way(self):
        self.status = OrderStatus.RIDER_ON_WAY
        self.save()

    def mark_as_delivered(self):
        with atomic():
            transaction = Transaction.objects.get(order=self)
            transaction.status = TransactionStatus.ACCEPTED
            transaction.save()
            self.status = OrderStatus.DELIVERED
            self.save()

    def mark_as_cancelled(self):
        with atomic():
            transaction = Transaction.objects.get(order=self)
            transaction.status = TransactionStatus.REJECTED
            transaction.save()
            self.status = OrderStatus.CANCELLED
            self.save()

    def get_ordered_items(self):
        items = OrderedItem.objects.filter(order=self)
        return items

    def rate_items(self, rating: int):
        if self.is_rated:
            return False

        items = self.get_ordered_items()
        self.is_rated = True
        self.save()
        for ordered_item in items:
            ordered_item.item.save_rating(rating)

    def handle_stripe_dependency(self):
        items = self.get_ordered_items()
        for item in items:
            item.item.get_stripe_price_id()

    def get_status_color(self):
        if self.status == OrderStatus.PREPARING:
            return 'primary'

        if self.status == OrderStatus.RIDER_ON_WAY:
            return 'warning'

        if self.status == OrderStatus.DELIVERED:
            return 'success'

        if self.status == OrderStatus.CANCELLED:
            return 'danger'

    def total_amount(self):
        if self._total_amount is None:
            items = OrderedItem.objects.filter(order=self)
            amount = 0

            for item in items:
                amount += item.item.price * item.quantity

            self._total_amount = amount

        return self._total_amount

    def __str__(self):
        return (
                str(self.restaurant.owner.email) + " -> "
                + str(self.rider.email) + " -> "
                + str(self.user.email) + " -> "
                + str(self.status)
        )


class Menu(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, null=True)

    class Meta:
        indexes = [
            models.Index(fields=['restaurant']),
        ]

    def __str__(self):
        return self.name


class MenuItem(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE)
    price = models.IntegerField(default=0)
    image = models.ImageField(upload_to='menu_items/', blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    stripe_price = models.CharField(max_length=100, default='')
    total_rating = models.IntegerField(default=0)
    total_rating_population = models.IntegerField(default=0)
    average_rating = models.FloatField(default=0)

    class Meta:
        indexes = [
            models.Index(fields=['menu']),
        ]

    def __str__(self):
        return str(self.menu) + " -> " + self.name + " " + str(self.price)

    def get_stripe_price_id(self):
        if self.stripe_price == '':
            try:
                stripe.api_key = settings.STRIPE_SECRET_KEY
                response = stripe.Price.create(
                    currency="pkr",
                    unit_amount=self.price * 100,
                    product_data={"name": self.name},
                )

                self.stripe_price = response['id']
                self.save()

                # print(json.dumps(response, indent=4))

            except Exception as e:
                print("could not create stripe price")
                print(e)

        return self.stripe_price

    def save_rating(self, new_rating: int):
        self.total_rating += new_rating
        self.total_rating_population += 1
        self.save()
        if new_rating:
            self.average_rating = round(self.total_rating / self.total_rating_population, 1)
        self.save()


class OrderedItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        indexes = [
            models.Index(fields=['order'])
        ]

    def get_item_total(self):
        return self.quantity * self.item.price

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
    RESTAURANT = 'RESTAURANT', 'Restaurant'


class Review(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    review_type = models.CharField(max_length=100, choices=ReviewTypes.choices)
    message = models.TextField()
    rating = models.PositiveIntegerField(default=0)

    class Meta:
        indexes = [
            models.Index(fields=['order', 'review_type']),

        ]

    def __str__(self):
        return str(self.order) + " -> " + str(self.review_type)


class QNA(models.Model):
    question = models.TextField()
    answer = models.TextField()


class Feedback(models.Model):
    email = models.EmailField()
    message = models.TextField()


class TransactionStatus(models.TextChoices):
    PENDING = 'PENDING', 'Pending'
    ACCEPTED = 'ACCEPTED', 'Accepted'
    REJECTED = 'REJECTED', 'Rejected'


class PaymentTypes(models.TextChoices):
    CASH_ON_DELIVERY = 'CASH_ON_DELIVERY', 'Cash on Delivery'
    STRIPE = 'STRIPE', 'Stripe'


class Transaction(models.Model):
    amount = models.IntegerField(default=0)
    status = models.CharField(max_length=100, choices=TransactionStatus.choices, default=TransactionStatus.PENDING)
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    payment_type = models.CharField(max_length=100, choices=PaymentTypes.choices)

    class Meta:
        indexes = [
            models.Index(fields=['order']),
        ]


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    payment_type = models.CharField(max_length=100, choices=PaymentTypes.choices, default=PaymentTypes.CASH_ON_DELIVERY)

    class Meta:
        indexes = [
            models.Index(fields=['user', 'restaurant'])
        ]

    def get_cart_total(self):
        cart_items = CartItem.objects.filter(cart=self)

        total = 0

        for cart_item in cart_items:
            total += cart_item.get_item_total()

        return total

    def __str__(self):
        return self.user.email + ' ' + self.payment_type + ' ' + str(self.get_cart_total())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def increment(self):
        self.quantity += 1
        self.save()
        return self.quantity

    def decrement(self):
        self.quantity -= 1
        self.save()

        if self.quantity == 0:
            self.delete()
            return None

        return self.quantity

    def get_item_total(self):
        return self.quantity * self.item.price

    def add_to_order(self, order):
        OrderedItem.objects.create(order=order, item=self.item, quantity=self.quantity)
        self.delete()

    class Meta:
        indexes = [
            models.Index(fields=['cart', 'item']),
            models.Index(fields=['cart'])
        ]

    def __str__(self):
        return str(self.item.name) + " -> " + str(self.quantity)
