from django.db import models

class Account(models.Model):
    USER_TYPE = (
        ('C', 'Citizen'),
        ('E', 'Employee'),
    )

    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField()
    password = models.CharField(max_length=128)

    fullname = models.CharField(max_length=100)
    dob = models.DateField(null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)

    type = models.CharField(max_length=1, choices=USER_TYPE, default='C')

    def __str__(self):
        return self.fullname