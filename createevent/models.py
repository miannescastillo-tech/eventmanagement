from django.db import models
from account.models import Account

class Document(models.Model):
    documentID = models.AutoField(primary_key=True)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)

    agency = models.CharField(max_length=100)
    document_type = models.CharField(max_length=100)
    purpose = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)

    status = models.CharField(max_length=20, default="Pending")

    is_imported = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.document_type

class Survey(models.Model):
    document = models.OneToOneField(Document, on_delete=models.CASCADE)

    rating = models.IntegerField()  # 1–5
    comment = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Survey for {self.document.title}"

class Appointment(models.Model):
    appointmentID = models.AutoField(primary_key=True)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)

    agency = models.CharField(max_length=100)
    service = models.CharField(max_length=100)

    appointment_date = models.DateField()
    appointment_time = models.TimeField()

    status = models.CharField(max_length=20, default="Pending")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.service

class AppointmentSurvey(models.Model):

    appointment = models.OneToOneField(
        Appointment,
        on_delete=models.CASCADE
    )

    rating = models.IntegerField()

    comment = models.TextField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"Survey for {self.appointment.service}"