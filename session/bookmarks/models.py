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
	result = User.objects.get(id=Decimal(userId))
	return result[0]

def getUserViaEmail(email):
	result = User.objects.filter(email__iregex=exact(email))
	return result[0] if len(result) > 0 else None

class Cookie(models.Model):
	userId = models.DecimalField()
	token = models.CharField(max_length=64)

def generateCookie(userId):
    cookie = Cookie()
    cookie.userId = userId
    cookie.token = hashlib.md5(userId + str(datetime.now().microsecond)).hexdigest()
    cookie.save()
    return cookie

def getCookie(userId, token):
	result = Cookie.objects.filter(userId=Decimal(userId)).filter(token__iregex=exact(token))
	return result[0] if len(result) > 0 else None