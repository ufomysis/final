from django import forms
from .models import Branch




class BranchCreateUpdateModelForm(forms.ModelForm):



    class Meta:
        model = Branch
        fields = [
            'title',
            'alias',
            'address',
            'image',

            ]
        labels = {
            'title':'ชื่อสาขา',
            'address': 'ที่อยู่สาขา',
            'alias': 'รหัสสาขา',
            'image': 'รูปภาพ',

        }

        error_messages = {
            # "title": {
            #     "max_length": "This title is too long.",
            #     "required": "The title field is required."
            # },
            #  "slug": {
            #     "max_length": "This title is too long.",
            #     "required": "The slug field is required.",
            #     #"unique": "The slug field must be unique."
            # },
        }


        # widgets = {
        #     'title': forms.TextInput(attrs={'placeholder': 'กรอกชื่อรายการ'}),
        #     "description": forms.Textarea(attrs={"rows": 4, "cols": 10}),
        #     "where_to_go": forms.Textarea(attrs={"rows": 4, "cols": 10}),
        #     "meeting_point": forms.Textarea(attrs={"rows": 4, "cols": 10}),
        #     # "meeting_time": DateTimePickerInput()
        # }


    def clean_title(self, *args, **kwargs):
        instance = self.instance
        title = self.cleaned_data.get('title')
        qs = Branch.objects.filter(title__iexact=title)

        if instance is not None:  #when update, it cant post the same title
            qs = qs.exclude(pk=instance.pk) # id=instance.id
        if qs.exists():
            raise forms.ValidationError("This title has already been used. Please try again.")
        return title

