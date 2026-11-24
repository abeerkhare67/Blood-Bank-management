
from django.contrib import admin
from .models import Donor, Patient, BloodStock, BloodRequest, Donation


@admin.register(Donor)
class DonorAdmin(admin.ModelAdmin):
    list_display = ("name", "blood_group", "phone", "email")
    search_fields = ("name", "blood_group", "phone", "email")


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ("name", "blood_group", "hospital", "phone", "email")
    search_fields = ("name", "blood_group", "hospital", "email")


@admin.register(BloodStock)
class BloodStockAdmin(admin.ModelAdmin):
    list_display = ("blood_group", "quantity")
    search_fields = ("blood_group",)

    def save_model(self, request, obj, form, change):
        if not change:
            blood_group = obj.blood_group.strip().upper()

            existing_stock = BloodStock.objects.filter(
                blood_group=blood_group
            ).first()

            if existing_stock:
                existing_stock.quantity += obj.quantity
                existing_stock.save()
                obj._merged_into_existing = True
                return

        obj.blood_group = obj.blood_group.strip().upper()
        super().save_model(request, obj, form, change)


@admin.register(BloodRequest)
class BloodRequestAdmin(admin.ModelAdmin):
    list_display = (
        "patient_name", "blood_group", "quantity",
        "hospital", "status", "created_at"
    )
    list_filter = ("blood_group", "status")
    search_fields = ("patient_name", "hospital", "phone", "email")


@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ("donor", "blood_group", "units", "donated_at")
    list_filter = ("blood_group", "donated_at")
    search_fields = ("donor__name", "donor__phone")
    date_hierarchy = "donated_at"
