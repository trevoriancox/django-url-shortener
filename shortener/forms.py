from django import forms

from shortener.baseconv import base62, DecodingError
from shortener.models import Link


too_long_error = "Your custom name is too long. Are you sure you wanted a shortening service? :)"


class LinkSubmitForm(forms.Form):
    url = forms.URLField(
        label='URL to be shortened',)
    custom = forms.CharField(
        label='Custom shortened name',
        required=False,)

    def clean_custom(self):
        custom = self.cleaned_data['custom']
        if not custom:
            return

        # they specified a custom url to shorten to. verify that we can decode
        # that shortened form, and that it's not already taken
        try:
            id = base62.to_decimal(custom)
        except DecodingError as e:
            raise forms.ValidationError(e)

        try:
            if Link.objects.filter(id=id).exists():
                raise forms.ValidationError('"%s" is already taken' % custom)
        except OverflowError:
            raise forms.ValidationError(too_long_error)
        return custom
