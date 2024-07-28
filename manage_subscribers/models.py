from django.db import models

class Subscriber(models.Model):
    name = models.CharField(max_length=100)
    nationality = models.CharField(max_length=100)
    registration_date = models.DateField()
    subscription = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)

    def __str__(self):
        return self.name
