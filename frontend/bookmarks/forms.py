__author__ = 'orps'
from django import forms
from django.utils.safestring import mark_safe

import json

class RegisterForm(forms.Form):
	name = forms.CharField(label=mark_safe('<br>Your name<br>'), max_length=32)
	email = forms.EmailField(label=mark_safe('<br>Email<br>'))
	phone = forms.CharField(label=mark_safe('<br>Your phone<br>'), max_length=16)
	password = forms.CharField(label=mark_safe('<br>Password<br>'), max_length=32)

	def json(self):
		data = self.cleaned_data
		result = {
			'email': data['email'],
			'password': data['password'],
			'phone': data['phone'],
			'name': data['name']
		}

		return result

class SigninForm(forms.Form):
	email = forms.EmailField(label=mark_safe('<br>Your email<br>'))
	password = forms.CharField(label=mark_safe('<br>Your password<br>'), max_length=32)

	def json(self):
		data = self.cleaned_data
		result = {"email": data['email'], 'password': data['password']}

		return result