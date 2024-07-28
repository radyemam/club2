from django import forms
from django.contrib.auth.models import User

class ProfileForm(forms.ModelForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email']

    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        # إزالة رسائل المساعدة
        self.fields['username'].help_text = None
