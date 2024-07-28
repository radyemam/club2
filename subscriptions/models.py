from django.db import models

class Subscriber(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    nationality = models.CharField(max_length=50)
    branch = models.CharField(max_length=100)

    def __str__(self):
        return self.name
