from django import forms
from django.forms import inlineformset_factory
from .models import Purchase, PurchaseSub

# Form for Purchase
from django import forms
from django.forms import inlineformset_factory
from .models import Purchase, PurchaseSub

# Form for Purchase
class PurchaseForm(forms.ModelForm):
    class Meta:
        model = Purchase
        fields = ['purchase_no', 'supplier_code', 'date', 'invoice_no']

# Form for PurchaseSub
class PurchaseSubForm(forms.ModelForm):
    class Meta:
        model = PurchaseSub
        fields = ['code', 'name_of_item', 'quantity', 'nos', 'rate', 'cgst_rate', 'sgst_rate']

# Create an inline formset to manage multiple PurchaseSub entries for a single Purchase
PurchaseSubFormSet = inlineformset_factory(Purchase, PurchaseSub, form=PurchaseSubForm, extra=1)

from django import forms
from .models import Student, Department, CourseType


# ============================
# ✅ Student Form
# ============================
class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = [
            "admission_no",
            "roll_no",
            "name",
            "department",
            "year",
            "course_type",
            "status",
            "batch",
        ]


# ============================
# ✅ Department Form
# ============================
class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ["name"]


# ============================
# ✅ CourseType Form
# ============================
class CourseTypeForm(forms.ModelForm):
    class Meta:
        model = CourseType
        fields = ["name"]




from django import forms
from django.forms import inlineformset_factory
from .models import Fine, FineSub




from django import forms
from .models import FineSub, Item

class FineSubForm(forms.ModelForm):
    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),  # Date Picker
        input_formats=['%Y-%m-%d']
    )
    item_name = forms.ModelChoiceField(
        queryset=Item.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False
    )

    class Meta:
        model = FineSub
        fields = ['date', 'item_name', 'price']

# Inline Formset to manage FineSub under Fine
FineSubFormSet = inlineformset_factory(Fine, FineSub, form=FineSubForm, extra=1, can_delete=True)

from django import forms
from .models import Fine, Student

class FineForm(forms.ModelForm):
    class Meta:
        model = Fine
        fields = ['admission_no', 'status']

    def __init__(self, *args, **kwargs):
        super(FineForm, self).__init__(*args, **kwargs)
        self.fields['admission_no'].widget.attrs.update({
            'list': 'admission_no_list',
        })


from django import forms
from .models import PendingPurchase, PendingPurchaseSub, Purchase, PurchaseSub

class PendingPurchaseForm(forms.ModelForm):
    class Meta:
        model = PendingPurchase
        fields = ['purchase_no', 'supplier_code', 'date', 'invoice_no', 'total_amount']


class PendingPurchaseSubForm(forms.ModelForm):
    class Meta:
        model = PendingPurchaseSub
        fields = ['code', 'name_of_item', 'quantity', 'nos', 'rate', 'cgst_rate', 'sgst_rate']  # Updated with 'code'


class PurchaseForm(forms.ModelForm):
    class Meta:
        model = Purchase
        fields = ['purchase_no', 'supplier_code', 'date', 'invoice_no', 'total_amount']


class PurchaseSubForm(forms.ModelForm):
    class Meta:
        model = PurchaseSub
        fields = ['code', 'name_of_item', 'quantity', 'nos', 'rate', 'cgst_rate', 'sgst_rate']  # Updated with 'code'


PendingPurchaseSubFormset = forms.inlineformset_factory(
    PendingPurchase, PendingPurchaseSub, form=PendingPurchaseSubForm, extra=1, can_delete=True
)

PurchaseSubFormset = forms.inlineformset_factory(
    Purchase, PurchaseSub, form=PurchaseSubForm, extra=1, can_delete=True
)

from django import forms
from .models import Chemical, ChemicalSub

class ChemicalForm(forms.ModelForm):
    class Meta:
        model = Chemical
        fields = ['name', 'specification', 'location', 'category']

class ChemicalSubForm(forms.ModelForm):
    class Meta:
        model = ChemicalSub
        fields = ['code', 'company', 'fund', 'exp_date', 'quantity', 'nos']

        # forms.py
from django import forms
from .models import DailyUsage


class DailyUsageForm(forms.ModelForm):
    class Meta:
        model = DailyUsage
        fields = ['item', 'quantity', 'batch']


from django import forms
from .models import Item, ItemSub

# ============================
# Item Form
# ============================
class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['name', 'specification', 'location', 'category']


# ============================
# ItemSub Form
# ============================
class ItemSubForm(forms.ModelForm):
    class Meta:
        model = ItemSub
        fields = ['item_code', 'company', 'fund', 'condition']

from django import forms
from .models import DailyUsagePending  # Ensure correct capitalization


class DailyUsagePendingForm(forms.ModelForm):
    class Meta:
        model = DailyUsagePending
        fields = ['item', 'quantity', 'batch']
        widgets = {
            'item': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'batch': forms.TextInput(attrs={'class': 'form-control'}),
        }


from django import forms
from django.forms import inlineformset_factory
from .models import Purchase, PurchaseSub,Supplier
class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['code', 'name', 'address', 'contact','email']
