from django.contrib import admin
from .models import Listing, Bidding, PassiveListing, Comments

admin.site.register(Listing)
admin.site.register(Bidding)
admin.site.register(PassiveListing)
admin.site.register(Comments)
