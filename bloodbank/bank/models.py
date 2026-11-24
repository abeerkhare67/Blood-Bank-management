
from django.db import models


class Donor(models.Model):
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    blood_group = models.CharField(max_length=5)
    phone = models.CharField(max_length=15)
    address = models.CharField(max_length=200)
    email = models.EmailField(blank=True, default="")

    def __str__(self):
        return self.name


class Patient(models.Model):
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    blood_group = models.CharField(max_length=5)
    hospital = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    email = models.EmailField(blank=True, default="")

    def __str__(self):
        return self.name


class BloodStock(models.Model):
    blood_group = models.CharField(max_length=5, unique=True)
    quantity = models.IntegerField(default=0)

    def __str__(self):
        return self.blood_group


class BloodRequest(models.Model):
    patient_name = models.CharField(max_length=100)
    blood_group = models.CharField(max_length=5)
    quantity = models.IntegerField()
    hospital = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    email = models.EmailField(blank=True, default="")
    status = models.CharField(max_length=20, default="Waiting")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.patient_name


class Donation(models.Model):
    donor = models.ForeignKey(
        Donor,
        on_delete=models.PROTECT,
        related_name="donations"
    )
    blood_group = models.CharField(max_length=5)
    units = models.PositiveIntegerField(default=1)
    donated_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, default="")

    def __str__(self):
        return (
            f"{self.donor.name} - {self.blood_group} "
            f"({self.units} units)"
        )
