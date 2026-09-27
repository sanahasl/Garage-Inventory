from django import forms


class StockAdjustForm(forms.Form):
    ACTIONS = [("out", "Take stock out"), ("in", "Add stock")]

    action = forms.ChoiceField(
        choices=ACTIONS, widget=forms.RadioSelect, initial="out"
    )
    quantity = forms.DecimalField(min_value=0.01, decimal_places=2, max_digits=10)
    job_reference = forms.CharField(
        required=False, label="Job / vehicle (optional)"
    )