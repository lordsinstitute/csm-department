from django.db import models


# Create your models here.
class UserRegistrationModel(models.Model):
    name = models.CharField(max_length=100)
    loginid = models.CharField(unique=True, max_length=100)
    password = models.CharField(max_length=100)
    mobile = models.CharField(unique=True, max_length=100)
    email = models.CharField(unique=True, max_length=100)
    locality = models.CharField(max_length=100)
    address = models.CharField(max_length=1000)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    status = models.CharField(max_length=100)

    def __str__(self):
        return self.loginid

    class Meta:
        db_table = 'UserRegistrations'


class TokenCountModel(models.Model):
    loginid = models.CharField(unique=True, max_length=100)
    count = models.IntegerField()

    def __str__(self):
        return self.loginid

    class Meta:
        db_table = 'TokenCountTable'


class UserFilesModel(models.Model):
    username = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    filename = models.CharField(max_length=100)
    enckey = models.CharField(max_length=1000)
    file = models.FileField(upload_to='actual/')
    cdate = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.id

    class Meta:
        db_table = 'uploadeddata'



class TransactionModel(models.Model):
    sender_id = models.CharField(max_length=100)
    recipient_id = models.CharField(max_length=100)
    amount = models.FloatField()
    remarks = models.CharField(max_length=100)
    otp = models.CharField(max_length=100)
    transaction_id = models.CharField(max_length=100)
    cdate = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.transaction_id

    class Meta:
        db_table = 'TransactionTable'