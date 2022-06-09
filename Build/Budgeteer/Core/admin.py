from django.contrib import admin
from . models import user_data, get_receipt_data

admin.site.register(user_data)
admin.site.register(get_receipt_data)
