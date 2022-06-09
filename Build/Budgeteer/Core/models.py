from django.db import models
from datetime import date

class user_data(models.Model):

    user_email = models.CharField(primary_key=True, max_length=50)
    user_first_name = models.CharField(max_length=50)
    user_last_name = models.CharField(max_length=50)
    user_password = models.CharField(max_length=50)
    user_DOB = models.DateField()
    user_date_created = models.DateField(default=date.today)

    class Meta:
        db_table = 'user_db'

class get_receipt_data(models.Model):

    product_id = models.IntegerField(primary_key=True)
    product_email = models.CharField(max_length=50)
    product_name = models.CharField(max_length=50)
    product_price = models.FloatField()
    product_vendor = models.CharField(max_length=50)
    product_date = models.DateField()
    product_date_created = models.DateField(default=date.today)

    class Meta:
        db_table = 'receipt_db'
