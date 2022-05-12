from django.conf import settings
from django.db import models
from django.shortcuts import reverse
from django.utils import timezone


# USER
# "fields": {
#     "password": "pbkdf2_sha256$150000$3riG7P2EZFxw$TZ94aNgQsd7fMROxxK2a/ncyxQENdDt2KOesEQ6m5gE=",
#     "last_login": "2022-04-29T14:10:16.710Z",
#     "is_superuser": true,
#     "username": "DMaxim",
#     "first_name": "",
#     "last_name": "",
#     "email": "maksim.dvornik.2017@gmail.com",
#     "is_staff": true,
#     "is_active": true,
#     "date_joined": "2021-05-20T15:33:55.838Z",
#     "groups": [],
#     "user_permissions": []
#   }


CATEGORY_CHOICES = (
    ('high_boots', 'Сапоги'),
    ('boots', 'Ботинки'),
    ('half_boots', 'П/ботинки'),
    ('shoes', 'Туфли'),
    ('summer_shoes', 'Туфли летние'),
    ('home_shoes', 'Домашняя обувь'),
    ('sport_shoes', 'Обувь для активного отдыха'),
)


OWNER_CHOICES = (
    ('M', 'Man'),
    ('W', 'Woman'),
    ('U', 'Unisex')
)


class SubImage(models.Model):
    title = models.CharField(max_length=100, default='Имя товара')
    image_1 = models.ImageField(null=True, blank=True)
    image_2 = models.ImageField(null=True, blank=True)
    image_3 = models.ImageField(null=True, blank=True)
    image_4 = models.ImageField(null=True, blank=True)

    def __str__(self):
        return self.title


class Item(models.Model):
    title = models.CharField(max_length=100)
    price = models.FloatField()
    discount_price = models.FloatField(blank=True, null=True)
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=26)
    owner = models.CharField(choices=OWNER_CHOICES, max_length=1, default='U')
    slug = models.SlugField(unique=True)
    description = models.TextField()
    image = models.ImageField()
    sub_images = models.OneToOneField(SubImage, blank=True, on_delete='SET_NULL', null=True, verbose_name='Дополнительные картинки')
    prioritize = models.IntegerField(blank=True, default=0)
    data_added = models.DateField(default=timezone.now, blank=True, null=False)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("core:product", kwargs={
            'slug': self.slug
        })


class OrderItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} of {self.item.title}"

    def get_total_item_price(self):
        return self.quantity * self.item.price

    def get_total_discount_item_price(self):
        return self.quantity * self.item.discount_price

    def get_amount_saved(self):
        return self.get_total_item_price() - self.get_total_discount_item_price()

    def get_final_price(self):
        if self.item.discount_price:
            return self.get_total_discount_item_price()
        return self.get_total_item_price()


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    items = models.ManyToManyField(OrderItem)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

    def get_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_final_price()
        return total


class ContactInfo(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.DO_NOTHING)
    letter = models.CharField(max_length=3000)
    destination_email = models.EmailField(max_length=100, default=settings.DEFAULT_CONTACT_EMAIL)

    def __str__(self):
        return f"This is a registered contact from user {self.user.username};\n" \
               f"Letter content: {self.letter};\n\n" \
               f"Dispatch address: {self.user.email};\n" \
               f"Destination address: {self.destination_email}."

