from django import forms
from .models import Item, Branch


class DeleteItemForm(forms.Form):
    note = forms.CharField()


class EditItemQuantityForm(forms.Form):
    quantity = forms.IntegerField(label='จำนวนที่ต้องการเปลี่ยนแปลง')

    def __init__(self, *args, **kwargs):
        self.info_obj = kwargs.pop('info_obj')
        super(EditItemQuantityForm, self).__init__(*args, **kwargs)

    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        q = self.info_obj.get_q_this_branch()

        if quantity == 0:
            raise forms.ValidationError("incorrect q")
        if quantity < 0:
            if q.get('all') < -quantity:
                raise forms.ValidationError("ใส่จำนวนมากกว่าจำนวนที่มีในคลังไม่ได้")
            if q.get('available') < -quantity:
                raise forms.ValidationError("อุปกรณ์ที่ต้องการลบต้องมีสถานะว่าง")

        return quantity


class TransferForm(forms.Form):
    amount = forms.IntegerField(initial=1, label='จำนวนที่ต้องการย้าย')
    dst_branch = forms.ModelChoiceField(queryset=None, label='สาขาปลายทางที่ต้องการย้ายไป')

    def __init__(self, *args, **kwargs):
        if kwargs['src_branch_slug'] is not None:
            self.src_branch_slug = kwargs.pop('src_branch_slug')

        super(TransferForm, self).__init__(*args, **kwargs)
        if self.src_branch_slug is not None:
            self.fields['dst_branch'].queryset = Branch.objects.exclude(slug=self.src_branch_slug)
        else:
            self.fields['dst_branch'].queryset = Branch.objects.all()
