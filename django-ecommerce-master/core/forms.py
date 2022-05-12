from django import forms


class Product(forms.Form):
    count = forms.IntegerField(label='Количество')


class Contact(forms.Form):
    letter = forms.CharField(label="Ваше сообщение", widget=forms.Textarea)
    destination_email = forms.EmailField(label="Ваша почта")


class AccountInfo(forms.Form):
    first_name = forms.CharField(label="Ваше имя", help_text="Введите имя",
                                 widget=forms.TextInput(attrs={'size': 35}))
    last_name = forms.CharField(label="Ваша фамилия", help_text="Введите фамилию",
                                widget=forms.TextInput(attrs={'size': 35}))
    user_email = forms.EmailField(label="Ваш E-mail", help_text="Введите E-mail",
                                  widget=forms.EmailInput(attrs={'size': 35}))
