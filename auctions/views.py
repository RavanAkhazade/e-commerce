from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from .models import User, Listing, Bidding, signal_product_manage_latest_version_id, Cart, PassiveListing, Comments
from .forms import CreateListing, CreateBid, CreateComment
from django.db.models import F
from django.contrib.auth.decorators import login_required


def index(request):
    pas_lst = PassiveListing.objects.all()
    lst = 0
    if Listing.objects.all():
        lst = Listing.objects.all()
    return render(request, "auctions/index.html", {
        "listings": lst,
        'pas_lst': pas_lst,
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            for lst in Listing.objects.all():
                if not Cart.objects.filter(author_id=request.user.id, listing2_id=lst.id):
                    Cart.objects.create(author_id=request.user.id, listing2_id=lst.id)
                    wl_lst = Cart.objects.get(author_id=request.user.id, listing2_id=lst.id).listing2
                    wl_lst.inlist = False
                    wl_lst.save()
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        for lst in Listing.objects.all():
            if not Cart.objects.filter(author_id=request.user.id, listing2_id=lst.id):
                Cart.objects.create(author_id=request.user.id, listing2_id=lst.id)
                wl_lst = Cart.objects.get(author_id=request.user.id, listing2_id=lst.id).listing2
                wl_lst.inlist = False
                wl_lst.save()
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


def create_listing(request):
    form = CreateListing(request.POST or None, request.FILES or None)
    if form.is_valid():
        Listing.objects.create(author_id=request.user.id, title=form.cleaned_data['title'], description=form.cleaned_data['description'], ebid=form.cleaned_data['ebid'], image=form.cleaned_data['image'], category=form.cleaned_data['category'])
        lst = Listing.objects.get(title=form.cleaned_data['title'])
        Bidding.objects.create(bid=form.cleaned_data['ebid'], t=lst)
        Cart.objects.create(author_id=request.user.id, listing2_id=lst.id)
        return HttpResponseRedirect(reverse("index"))
    return render(request, "auctions/create_listings.html", {
        "form": CreateListing(),
    })


def listing(request, title):
    err = 0
    bids_amount = 0
    bidding = 0
    lst_bid = 0
    lst = 0
    bid = 0
    comments = 0
    listed_by = 0
    lst_author = Listing.objects.get(title=title).author

    if Listing.objects.all():
        lst_bid = Listing.objects.filter(title=title).values_list('ebid', flat=True)[0]
        lst = Listing.objects.get(title=title)
    if Bidding.objects.all():
        bids_amount = Bidding.objects.filter(t__title=title).values_list("counting", flat=True)[0]
        bidding = Bidding.objects.filter(t__title=title)
        bid = bidding.values_list('bid', flat=True)[0]
    if Comments.objects.all():
        comments = Comments.objects.filter(t__title=title)
    if Cart.objects.filter(listing2_id=lst.id):
        listed_by = Cart.objects.get(listing2__title=title, author=lst_author)

    form = CreateBid(request.POST)
    form2 = CreateComment(request.POST)
    if request.method == "POST" and 'placing' in request.POST:
        if form.is_valid() and int(request.POST.get('bid')) > Listing.objects.get(title=title).ebid and int(request.POST.get('bid')) > signal_product_manage_latest_version_id(Bidding, Bidding.objects.get(t__title=title)).bid:
            Listing.objects.filter(title=title).update(ebid=form.cleaned_data['bid'])
            bidding.update(bid=form.cleaned_data['bid'], counting=F('counting')+1)
            return HttpResponseRedirect(reverse('index'))
        else:
            err = "Bid is not valid"

    if request.method == "POST" and 'commenting' in request.POST:
        if form2.is_valid():
            Comments.objects.create(user=request.user, t=lst, comment=form2.cleaned_data['comment'])
            return HttpResponseRedirect(reverse('listing', args=[title]))

    if request.method == "POST" and 'removing' in request.POST:
        tof = Cart.objects.get(listing2__title=title, author=request.user.id).author
        wl_lst = Cart.objects.get(listing2__title=title, author=tof.id).listing2
        wl_lst.inlist = False
        wl_lst.save()
        return HttpResponseRedirect(reverse('watchlist'))

    if request.method == "POST" and 'winning' in request.POST:
        pas_lst = Listing.objects.get(title=title)
        PassiveListing.objects.create(title=pas_lst.title, description=pas_lst.description, image=pas_lst.image, ebid=Bidding.objects.get(t__title=title).bid)
        Listing.objects.filter(title=title).delete()
        return HttpResponseRedirect(reverse('passive_listing', args=[title]))

    if request.GET.get('wl') and request.user.is_authenticated:
        tof = Cart.objects.get(listing2__title=title, author=request.user.id).author
        wl_lst = Cart.objects.get(listing2__title=title, author=tof.id).listing2
        wl_lst.inlist = True
        wl_lst.save()

    return render(request, "auctions/listing.html", {
        "lst": lst,
        "form": CreateBid(),
        "form2": CreateComment(),
        "err": err,
        "bids_amount": bids_amount,
        "bidding": bidding,
        "lst_bid": lst_bid,
        "bid": bid,
        "comments": comments,
        "lst_by": listed_by
            })


@login_required(login_url='login')
def watchlist(request):
    lst = Cart.objects.filter(author=request.user, listing2__inlist=True)
    return render(request, "auctions/watchlist.html", {
        "lst": lst,
    })


def passive_listing(request, title):
    lst = PassiveListing.objects.get(title=title)
    return render(request, "auctions/passive_listing.html", {
        "lst": lst
    })


def category_listing(request, category):
    lsts = Listing.objects.filter(category=category)
    return render(request, "auctions/category_listing.html", {
        "lsts": lsts
    })


def categories(request):
    cats = []
    for c in Listing.CATEGORIES_CHOICES:
        cats.append(c[0])
    return render(request, "auctions/categories.html", {
        "cats": cats,
    })
