from django import forms

from shortener.baseconv import base62
from shortener.models import Link

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

        # test for characters in the requested custom alias that are not
        # available in our base62 enconding
        for char in custom:
            if char not in base62.digits:
                raise forms.ValidationError('Invalid character: "%s"' % char)
        # make sure this custom alias is not alrady taken
        id = base62.to_decimal(custom)
        try:
            if Link.objects.filter(id=id).exists():
                raise forms.ValidationError('"%s" is already taken' % custom)
        except OverflowError:
            raise forms.ValidationError(
                "Your custom name is too long. Are you sure you wanted a "
                "shortening service? :)")
        return custom
