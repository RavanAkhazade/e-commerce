from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver


class User(AbstractUser):
    pass


class Listing(models.Model):
    CATEGORIES_CHOICES = [
        ("Electronics", 'Electronics'),
        ("Sport", 'Sport'),
        ("Clothes", 'Clothes'),
        ("Accessories", 'Accessories'),
        ("No category", 'No Category Listed'),
    ]
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=64, unique=True)
    description = models.TextField(max_length=1000, blank=True)
    ebid = models.PositiveIntegerField(verbose_name="bid")
    image = models.ImageField(upload_to='images', blank=True)
    inlist = models.BooleanField(default=False)
    category = models.CharField(
        max_length=11,
        choices=CATEGORIES_CHOICES,
        default="No category",
    )

    objects = models.Manager()

    def __str__(self):
        return "Title: %s; Description: %s; Bid: %s; " % (self.title, self.description, self.ebid)

    def delete(self, using=None, keep_parents=False):
        self.image.storage.delete(self.image)
        super().delete()


class PassiveListing(models.Model):

    title = models.CharField(max_length=64, unique=True)
    description = models.TextField(max_length=1000)
    ebid = models.PositiveIntegerField()
    image = models.ImageField(upload_to='images', blank=True)

    objects = models.Manager()

    def __str__(self):
        return f'Title: {self.title}; Description: {self.description}; Bid: {self.ebid}'.format(self=self)


class Cart(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    listing2 = models.ForeignKey(Listing, on_delete=models.CASCADE)

    objects = models.Manager()

    def __str__(self):
        return f'{self.author},{self.listing2}'


class Bidding(models.Model):
    bid = models.PositiveIntegerField(verbose_name='')
    t = models.OneToOneField(Listing, on_delete=models.CASCADE, primary_key=True,)
    counting = models.IntegerField(default=0)

    objects = models.Manager()

    def __str__(self):
        return f'Your Bid: {self.bid}, {self.t}, {self.counting}'.format(self=self)


class Comments(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    t = models.ForeignKey(Listing, to_field='title', on_delete=models.CASCADE)
    comment = models.TextField(max_length=1000)

    objects = models.Manager()

    def __str__(self):
        return f'{self.comment}'


@receiver(pre_save, sender=Bidding)
def signal_product_manage_latest_version_id(sender, instance, update_fields=None, **kwargs):
    try:
        old_instance = sender.objects.get(pk=instance.pk)
        return old_instance
    except sender.DoesNotExist:  # to handle initial object creation
        return None  # just exiting from signal
