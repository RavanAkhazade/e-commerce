from django import forms
from .models import Listing, Bidding, Comments


class CreateListing(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ["title", "description", "ebid", "image", "category"]


class CreateBid(forms.ModelForm):
    class Meta:
        model = Bidding
        fields = ["bid"]
        widgets = {
            'bid': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Bid'}),
        }


class CreateComment(forms.ModelForm):
    class Meta:
        model = Comments
        fields = ["comment"]
