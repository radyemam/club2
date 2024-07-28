from django.db import models
from django.contrib.auth.models import User

class Expense(models.Model):
    item = models.CharField(max_length=100)
    amount = models.IntegerField()  # تغيير الحقل ليكون رقماً صحيحاً
    date = models.DateField()
    expense_type = models.CharField(max_length=50, default='نقدا')  # إضافة القيمة الافتراضية هنا
    account = models.CharField(max_length=50)
    details = models.TextField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)  # إضافة الحقل user مع قيمة افتراضية

    

    def __str__(self):
        return self.item
