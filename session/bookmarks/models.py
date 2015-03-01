from django.db import models

import json
import hashlib
from datetime import datetime
from decimal import Decimal


def exact(str):
    return r'\b' + str + r'\b'

class User(models.Model):
    name = models.CharField(max_length=32)
    phone = models.CharField(max_length=16)
    email = models.EmailField()
    password = models.CharField(max_length=32)

    def json(self):
        dict = {}
        dict["name"] = self.name
        dict["phone"] = self.phone
        dict["email"] = self.email

        return json.dumps(dict)

def getUserViaId(userId):
	result = User.objects.get(id=int(userId))
	return result

def getUserViaEmail(email):
	result = User.objects.filter(email__iregex=exact(email))
	return result[0] if len(result) > 0 else None

class Cookie(models.Model):
	userId = models.IntegerField()
	token = models.CharField(max_length=64)

def generateCookie(userId):
    cookie = Cookie()
    cookie.userId = userId
    id = str(userId)
    msc = str(datetime.now().microsecond)
    cookie.token = hashlib.md5(str(userId) + str(datetime.now().microsecond)).hexdigest()
    cookie.save()
    return cookie

def getCookie(id, token):
    cookieList = Cookie.objects.filter(id=Decimal(id))
    if len(cookieList) > 0 and cookieList[0].token == token:
        return cookieList[0]

    return None
