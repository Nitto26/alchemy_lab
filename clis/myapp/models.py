from django.db import models

# Create your models here.
from django.db import models
from django.db.models import Sum, F
from django.core.exceptions import ValidationError


# ============================
# Supplier Table
# ============================
class Supplier(models.Model):
    supplier_id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)
    address = models.TextField()
    contact = models.CharField(max_length=15)
    email = models.EmailField(max_length=255, unique=True)

    def __str__(self):
        return self.name


# ============================
# Purchase Table
# ============================
class Purchase(models.Model):
    purchase_id = models.AutoField(primary_key=True)
    purchase_no = models.CharField(max_length=50, unique=True)
    supplier_code = models.ForeignKey(Supplier, to_field='code', on_delete=models.CASCADE)
    date = models.DateField()
    invoice_no = models.CharField(max_length=50)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    def calculate_total_amount(self):
        """Calculate total amount by summing up PurchaseSub details."""
        total = self.sub_items.aggregate(
            total=Sum(
                (F('nos') * F('rate')) +
                (F('nos') * F('rate') * F('cgst_rate') / 100) +
                (F('nos') * F('rate') * F('sgst_rate') / 100)
            )
        )['total'] or 0.00
        self.total_amount = total
        self.save()

    def __str__(self):
        return self.supplier_code.name


# ============================
# PurchaseSub Table
# ============================
class PurchaseSub(models.Model):
    id = models.AutoField(primary_key=True) 
    code = models.CharField(max_length=50, blank=True, null=True)
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE, related_name='sub_items')
    name_of_item = models.CharField(max_length=255)
    quantity = models.CharField(max_length=255)
    nos = models.IntegerField()
    rate = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    cgst_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    cgst_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    sgst_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    sgst_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    

    def save(self, *args, **kwargs):
        self.total_amount = self.nos * self.rate
        self.cgst_amount = (self.total_amount * self.cgst_rate) / 100
        self.sgst_amount = (self.total_amount * self.sgst_rate) / 100
        super().save(*args, **kwargs)
        self.purchase.calculate_total_amount()
         # ✅ Check if Chemical with the same name exists
        try:
            chemical = Chemical.objects.get(name=self.name_of_item)
        except Chemical.DoesNotExist:
            chemical = None

        # ✅ If a matching Chemical is found, update/create ChemicalSub
        if chemical:
            # Check if ChemicalSub with the same code exists
            chemical_sub, created = ChemicalSub.objects.get_or_create(
                chem_id=chemical,
                code=self.code,
                defaults={
                    'company': self.purchase.supplier_code.name,  # Example
                    'fund': 'N/A',  # Default fund (you can change it)
                    'exp_date': None,  # You can set it to None if not available
                    'quantity': self.quantity,
                    'nos': self.nos,
                    'total_quantity': int(self.quantity) * self.nos,
                }
            )

            # ✅ If ChemicalSub already exists, update quantity and total_quantity
            if not created:
                chemical_sub.nos += self.nos
                chemical_sub.total_quantity = chemical_sub.nos * int(self.quantity)
                chemical_sub.save()

            # ✅ Update total quantity in the Chemical table
            chemical.update_total_quantity()

    def __str__(self):
        return f"{self.name_of_item} - {self.purchase.purchase_no}"


# ============================
# Category Table
# ============================
class Category(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


# ============================
# Item Table
# ============================
class Item(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    specification = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)

    def update_quantity(self):
        self.quantity = self.sub_items.count()
        self.save()

    def __str__(self):
        return self.name


# ============================
# ItemSub Table
# ============================
class ItemSub(models.Model):
    CONDITION_CHOICES = [
        ('working', 'Working'),
        ('repair', 'Repair'),
        ('damaged', 'Damaged'),
    ]

    id = models.AutoField(primary_key=True)
    item_id = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='sub_items')
    item_code = models.CharField(max_length=50, unique=True)
    company = models.CharField(max_length=255)
    fund = models.CharField(max_length=255)
    condition = models.CharField(max_length=10, choices=CONDITION_CHOICES, default='working')
    price = models.DecimalField(max_digits=12, decimal_places=2)

    def save(self, *args, **kwargs):
        if not self.price:
            self.set_price_from_purchasesub()  # Fetch price from PurchaseSub based on code
        super().save(*args, **kwargs)
        self.item_id.update_quantity()

    def set_price_from_purchasesub(self):
        # Get price from PurchaseSub based on item_code
        from myapp.models import PurchaseSub  # Avoid circular import
        try:
            purchase_sub = PurchaseSub.objects.get(code=self.item_code)
            self.price = purchase_sub.rate  # Fetch rate instead of price_per_unit
        except PurchaseSub.DoesNotExist:
            self.price = 0.00  # Set default price if no match found

    def delete(self, *args, **kwargs):
        item = self.item_id
        super().delete(*args, **kwargs)
        item.update_quantity()

    def __str__(self):
        return f"{self.item_id.name} - {self.item_code}"
# ============================
# Department Table
# ============================
class Department(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


# ============================
# CourseType Table
# ============================
class CourseType(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


# ============================
# Student Table
# ============================
class Student(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('passout', 'Passout'),
    ]

    id = models.AutoField(primary_key=True)
    admission_no = models.CharField(max_length=50, unique=True)
    roll_no = models.CharField(max_length=50)
    name = models.CharField(max_length=255)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    year = models.PositiveIntegerField()
    course_type = models.ForeignKey(CourseType, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    batch = models.CharField(max_length=10)

    def __str__(self):
        return self.name


# ============================
# Fine Table
# ============================
class Fine(models.Model):
    STATUS_CHOICES = [
        ('paid', 'Paid'),
        ('not_paid', 'Not Paid'),
    ]

    id = models.AutoField(primary_key=True)
    admission_no = models.ForeignKey(Student, to_field='admission_no', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    department = models.CharField(max_length=255)
    year = models.PositiveIntegerField()
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='not_paid')

    def calculate_total_amount(self):
        total = self.sub_items.aggregate(total=Sum('price'))['total'] or 0.00
        self.total = total
        self.save()

    def save(self, *args, **kwargs):
        if self.admission_no:
            student = self.admission_no
            self.name = student.name
            self.department = student.department.name
            self.year = student.year
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Fine for {self.name} ({self.admission_no})"


# ============================
# FineSub Table
# ============================
class FineSub(models.Model):
    fine = models.ForeignKey(Fine, on_delete=models.CASCADE, related_name='sub_items')
    date = models.DateField()
    item_name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def clean(self):
        if not Item.objects.filter(name=self.item_name).exists():
            raise ValidationError(f"Item '{self.item_name}' does not exist in the Item table.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
        self.fine.calculate_total_amount()

    def delete(self, *args, **kwargs):
        fine = self.fine
        super().delete(*args, **kwargs)
        fine.calculate_total_amount()

    def __str__(self):
        return f"{self.item_name} - {self.fine.name}"


# ============================
# Chemical Table
# ============================
class Chemical(models.Model):
    CATEGORY_CHOICES = [
        ('organic', 'Organic'),
        ('inorganic', 'Inorganic'),
    ]

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    specification = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=255)
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES)
    total_quantity = models.PositiveIntegerField(default=0)

    def update_total_quantity(self):
        total = self.sub_items.aggregate(total=Sum('total_quantity'))['total'] or 0
        self.total_quantity = total
        self.save()

    def __str__(self):
        return self.name



# ============================
# ChemicalSub Table
# ============================
class ChemicalSub(models.Model):
    chem_id = models.ForeignKey(Chemical, on_delete=models.CASCADE, related_name='sub_items')
    code = models.CharField(max_length=50, unique=True)
    company = models.CharField(max_length=255)
    fund = models.CharField(max_length=255)
    exp_date = models.DateField(null=True, blank=True)
    quantity = models.PositiveIntegerField()
    nos = models.PositiveIntegerField()
    total_quantity = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('chem_id', 'exp_date')

    def save(self, *args, **kwargs):
        """ Only set total_quantity initially, don't override after deductions """
        if not self.pk:  # If new entry
            self.total_quantity = self.nos * self.quantity
        super().save(*args, **kwargs)
        self.chem_id.update_total_quantity()

    def deduct_quantity(self, used_quantity):
        """ Deducts quantity when usage is recorded """
        if used_quantity > self.total_quantity:
            raise ValueError(f"Insufficient stock: Available {self.total_quantity}, Requested {used_quantity}")

        self.total_quantity -= used_quantity
        self.save()
        self.chem_id.update_total_quantity()  # Ensure parent updates too

    def __str__(self):
        return f"{self.chem_id.name} - {self.code}"

from django.db import models
from django.db.models import Sum, F

class PendingPurchase(models.Model):
    purchase_no = models.CharField(max_length=50, unique=True)
    supplier_code = models.ForeignKey('Supplier', to_field='code', on_delete=models.CASCADE)
    date = models.DateField()
    invoice_no = models.CharField(max_length=50)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    created_by = models.CharField(max_length=100)  # Assistant username
    status = models.CharField(max_length=10, choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Discarded', 'Discarded')], default='Pending')

    def __str__(self):
        return f"Pending {self.purchase_no}"
    

class PendingPurchaseSub(models.Model):
    purchase = models.ForeignKey(PendingPurchase, on_delete=models.CASCADE, related_name='pending_items')
    code = models.CharField(max_length=50, blank=True, null=True)  # ✅ Added code field
    name_of_item = models.CharField(max_length=255)
    quantity = models.IntegerField()
    nos = models.IntegerField()
    rate = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    cgst_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    cgst_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    sgst_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    sgst_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def save(self, *args, **kwargs):
        self.nos = int(self.nos)
        self.rate = float(self.rate)
        self.total_amount = self.nos * self.rate
        self.cgst_amount = (self.total_amount * float(self.cgst_rate)) / 100
        self.sgst_amount = (self.total_amount * float(self.sgst_rate)) / 100
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Pending {self.name_of_item} - {self.purchase.purchase_no}"

# models.py

class DailyUsage(models.Model):
    usage_id = models.AutoField(primary_key=True)
    date = models.DateField(auto_now_add=True)
    time = models.TimeField(auto_now_add=True)
    item = models.ForeignKey('ChemicalSub', on_delete=models.CASCADE, related_name='daily_usages')
    quantity = models.PositiveIntegerField()
    batch = models.CharField(max_length=100)
    def save(self, *args, **kwargs):
        """ Deducts the used quantity from ChemicalSub """
        self.item.deduct_quantity(self.quantity)  # Reduce stock
        super().save(*args, **kwargs)  # Save usage entry

        def __str__(self):
         return f"Usage {self.usage_id} - {self.item} on {self.date}"
        

class DailyUsagePending(models.Model):
    usage_id = models.AutoField(primary_key=True)
    date = models.DateField(auto_now_add=True)
    time = models.TimeField(auto_now_add=True)
    item = models.ForeignKey('ChemicalSub', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    batch = models.CharField(max_length=100)

    def __str__(self):
        return f"Usage {self.usage_id} - {self.item}"
