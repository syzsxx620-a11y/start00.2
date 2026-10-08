from django import forms


class CheckoutForm(forms.Form):
    full_name = forms.CharField(max_length=120, label="Full name")
    email = forms.EmailField(label="Email")
    phone = forms.CharField(max_length=40, label="Phone")
    company = forms.CharField(max_length=120, required=False, label="Company (optional)")
    country = forms.CharField(max_length=80, label="Country")
    address = forms.CharField(
        max_length=255,
        widget=forms.Textarea(attrs={"rows": 3}),
        label="Address",
    )
    city = forms.CharField(max_length=80, label="City")
    state = forms.CharField(max_length=80, required=False, label="State / Province")
    postal_code = forms.CharField(max_length=20, required=False, label="Postal code")
    notes = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 3}), required=False, label="Order notes"
    )
