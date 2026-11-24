
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import transaction
from django.db.models import Sum
from .models import BloodRequest, BloodStock, Donor, Donation
from .email_utils import send_notification_email

def home(request):
    return render(request, 'home.html')


def get_or_merge_stock(blood_group):
    blood_group = blood_group.strip().upper()

    stocks = list(
        BloodStock.objects.select_for_update()
        .filter(blood_group__iexact=blood_group)
        .order_by("id")
    )

    if not stocks:
        return BloodStock.objects.create(
            blood_group=blood_group,
            quantity=0
        )

    # Keep the first record and combine all duplicate quantities.
    stock = stocks[0]
    stock.quantity = sum(item.quantity for item in stocks)
    stock.blood_group = blood_group
    stock.save()

    # Remove duplicate records after combining their quantities.
    for duplicate in stocks[1:]:
        duplicate.delete()

    return stock



def queue_view(request):
    requests = BloodRequest.objects.filter(
        status="Waiting"
    ).order_by("created_at")

    return render(request, 'queue.html', {
        'requests': requests
    })


def add_request(request):
    if request.method == "POST":
        BloodRequest.objects.create(
            patient_name=request.POST['patient_name'],
            blood_group=request.POST['blood_group'],
            quantity=request.POST['quantity'],
            hospital=request.POST['hospital'],
            phone=request.POST['phone'],
            email=request.POST.get('email', '').strip()
        )

        messages.success(request, "Blood request submitted.")
        return redirect('/queue/')

    return render(request, 'request.html')



@transaction.atomic
def dequeue_request(request):
    first_request = (
        BloodRequest.objects.select_for_update()
        .filter(status="Waiting")
        .order_by("created_at")
        .first()
    )

    if first_request:
        stock = get_or_merge_stock(first_request.blood_group)

        if stock.quantity >= first_request.quantity:
            stock.quantity -= first_request.quantity
            stock.save()

            first_request.status = "Served"
            first_request.save()

            messages.success(
                request,
                "Patient served successfully and blood stock updated."
            )
        else:
            messages.error(
                request,
                f"Insufficient blood stock. Available: {stock.quantity} "
                f"units; Required: {first_request.quantity} units."
            )
    else:
        messages.warning(request, "No waiting patients in the queue.")

    return redirect('/queue/')



def peek_request(request):
    first_request = BloodRequest.objects.filter(
        status="Waiting"
    ).order_by("created_at").first()

    return render(request, 'peek.html', {
        'request': first_request
    })


def stock_view(request):
    stocks = BloodStock.objects.all().order_by("blood_group")

    return render(request, 'stock.html', {
        'stocks': stocks
    })


def donation_history(request):
    donations = Donation.objects.select_related('donor').order_by(
        '-donated_at'
    )

    blood_group = request.GET.get('blood_group', '').strip()
    if blood_group:
        donations = donations.filter(blood_group=blood_group)

    total_donations = donations.count()
    total_units = donations.aggregate(total=Sum('units'))['total'] or 0

    return render(request, 'donations.html', {
        'donations': donations,
        'total_donations': total_donations,
        'total_units': total_units,
        'selected_group': blood_group,
        'blood_groups': [
            'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'
        ],
    })


@transaction.atomic
def record_donation(request):
    if request.method != "POST":
        return redirect('/donations/')

    donor_id = request.POST.get('donor')
    blood_group = request.POST.get('blood_group', '').strip().upper()
    units_text = request.POST.get('units', '1').strip()

    try:
        donor = Donor.objects.get(pk=donor_id)
        units = int(units_text)

        if blood_group not in [
            'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'
        ]:
            raise ValueError

        if units < 1:
            raise ValueError

    except (Donor.DoesNotExist, ValueError, TypeError):
        messages.error(request, "Please enter valid donation details.")
        return redirect('/donations/')

    if donor.blood_group.strip().upper() != blood_group:
        messages.error(
            request,
            "The selected blood group does not match the donor's record."
        )
        return redirect('/donations/')

     
    stock = get_or_merge_stock(blood_group)

    Donation.objects.create(
        donor=donor,
        blood_group=blood_group,
        units=units
    )

    stock.quantity += units
    stock.save()

    send_notification_email(
        donor.email,
        "Blood Donation Recorded",
        (
            f"Hello {donor.name},\n\n"
            "Your blood donation has been recorded successfully.\n"
            f"Blood group: {blood_group}\n"
            f"Units recorded: {units}\n\n"
            "Thank you for supporting blood donation.\n"
            "Blood Bank Management System"
        ),
    )

    messages.success(request, "Donation recorded and stock updated.")
    return redirect('/donations/')



def donation_form(request):
    donors = Donor.objects.all().order_by('name')

    return render(request, 'donation_form.html', {
        'donors': donors,
        'blood_groups': [
            'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'
        ],
    })
