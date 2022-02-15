from django import forms


class CouponApplyForm(forms.Form):
    kod = forms.CharField()
