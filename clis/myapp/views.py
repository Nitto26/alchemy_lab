from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Supplier, Purchase, PurchaseSub
from .forms import PurchaseForm, PurchaseSubForm, PurchaseSubFormSet


# ============================
# ✅ Login View
# ============================
def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        # ✅ Authenticate the user
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            # ✅ Redirect based on username after authentication
            if user.username == "hod":
                return redirect("hod_home")
            elif user.username == "assistant":
                return redirect("assistant_home")
            elif user.username == "keeper":
                return redirect("storekeeper_home")
            else:
                return redirect("hod_home")  # Default Home Page
        else:
            messages.error(request, "Invalid username or password")

    return render(request, "login.html")


@login_required
def hod_dashboard(request):
    return render(request, "home_hod.html")


@login_required
def assistant_dashboard(request):
    return render(request, "home_assistant.html")


@login_required
def storekeeper_dashboard(request):
    return render(request, "home_storekeeper.html")


def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully!")
    return redirect("login")


# ============================
# ✅ Supplier Management
# ============================
def supplier_list(request):
    suppliers = Supplier.objects.all()
    return render(request, "supplier_list.html", {"suppliers": suppliers})


def add_supplier(request):
    if request.method == "POST":
        code = request.POST.get("code")
        name = request.POST.get("name")
        address = request.POST.get("address")
        contact = request.POST.get("contact")
        email = request.POST.get("email")

        # Check for duplicate supplier
        if Supplier.objects.filter(code=code).exists():
            messages.error(request, "Supplier Code already exists!")
        elif Supplier.objects.filter(email=email).exists():
            messages.error(request, "Email already exists!")
        else:
            Supplier.objects.create(
                code=code, name=name, address=address, contact=contact, email=email
            )
            messages.success(request, "Supplier added successfully!")
            return redirect("supplier_list")

    return render(request, "add_supplier.html")


def update_supplier(request, supplier_id):
    supplier = get_object_or_404(Supplier, id=supplier_id)

    if request.method == "POST":
        supplier.code = request.POST.get("code")
        supplier.name = request.POST.get("name")
        supplier.address = request.POST.get("address")
        supplier.contact = request.POST.get("contact")
        supplier.email = request.POST.get("email")
        supplier.save()

        messages.success(request, "Supplier updated successfully!")
        return redirect("supplier_list")

    return render(request, "update_supplier.html", {"supplier": supplier})


def delete_supplier(request, supplier_id):
    supplier = get_object_or_404(Supplier, id=supplier_id)
    supplier.delete()
    messages.success(request, "Supplier deleted successfully!")
    return redirect("supplier_list")


# ============================
# ✅ Purchase Management
# ============================
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Sum, F
from django.contrib import messages
from .models import Purchase, PurchaseSub, Supplier
from .forms import PurchaseForm, PurchaseSubForm, PurchaseSubFormSet

# ============================
# ✅ Purchase Management
# ============================
def purchase_list(request):
    purchases = Purchase.objects.all()
    suppliers = Supplier.objects.all()
    return render(request, "purchase_list.html", {"purchases": purchases, "suppliers": suppliers})


def add_purchase(request):
    if request.method == "POST":
        purchase_form = PurchaseForm(request.POST)
        formset = PurchaseSubFormSet(request.POST)

        if purchase_form.is_valid() and formset.is_valid():
            purchase = purchase_form.save()

            sub_items = formset.save(commit=False)
            for sub in sub_items:
                sub.purchase = purchase
                if not sub.code:
                    sub.code = f"{purchase.purchase_no}-{sub.name_of_item[:3].upper()}"
                sub.save()

            messages.success(request, "Purchase added successfully!")
            return redirect("purchase_list")

    else:
        purchase_form = PurchaseForm()
        formset = PurchaseSubFormSet()

    return render(request, "add_purchase.html", {"purchase_form": purchase_form, "formset": formset})


def edit_purchase(request, purchase_id):
    purchase = get_object_or_404(Purchase, pk=purchase_id)
    if request.method == "POST":
        form = PurchaseForm(request.POST, instance=purchase)
        if form.is_valid():
            form.save()
            messages.success(request, "Purchase updated successfully!")
            return redirect("purchase_list")
    else:
        form = PurchaseForm(instance=purchase)
    return render(request, "edit_purchase.html", {"form": form, "purchase": purchase})


def delete_purchase(request, purchase_id):
    purchase = get_object_or_404(Purchase, pk=purchase_id)
    purchase.delete()
    messages.success(request, "Purchase deleted successfully!")
    return redirect("purchase_list")


def purchase_detail(request, purchase_id):
    purchase = get_object_or_404(Purchase, pk=purchase_id)
    sub_items = PurchaseSub.objects.filter(purchase=purchase)
    form = PurchaseSubForm()
    return render(
        request, "purchase_detail.html", {"purchase": purchase, "sub_items": sub_items, "form": form}
    )


def add_purchase_sub(request, purchase_id):
    purchase = get_object_or_404(Purchase, pk=purchase_id)
    if request.method == "POST":
        form = PurchaseSubForm(request.POST)
        if form.is_valid():
            sub_item = form.save(commit=False)
            sub_item.purchase = purchase
            if not sub_item.code:
                sub_item.code = f"{purchase.purchase_no}-{sub_item.name_of_item[:3].upper()}"
            sub_item.save()
            messages.success(request, "Item added successfully!")
            return redirect("purchase_detail", purchase_id=purchase.purchase_id)
    return redirect("purchase_detail", purchase_id=purchase.purchase_id)


def edit_purchase_sub(request, sub_id):
    sub_item = get_object_or_404(PurchaseSub, pk=sub_id)
    if request.method == "POST":
        form = PurchaseSubForm(request.POST, instance=sub_item)
        if form.is_valid():
            form.save()
            messages.success(request, "Item updated successfully!")
            return redirect("purchase_detail", purchase_id=sub_item.purchase.id)
    else:
        form = PurchaseSubForm(instance=sub_item)
    return render(request, "edit_purchase_sub.html", {"form": form, "sub_item": sub_item})


from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import PurchaseSub

def delete_purchase_sub(request, sub_id):
    # Get the PurchaseSub instance or return 404 if not found
    sub_item = get_object_or_404(PurchaseSub, pk=sub_id)

    # Get the related purchase
    purchase = sub_item.purchase

    # Delete the sub_item
    sub_item.delete()

    # Recalculate total amount after deletion
    purchase.calculate_total_amount()

    # Success message
    messages.success(request, "Item deleted successfully!")

    # Redirect to the purchase details page
    return redirect('purchase_details', purchase_id=purchase.purchase_id)


from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib import messages
from .models import Student, Department, CourseType
from .forms import StudentForm, DepartmentForm, CourseTypeForm


# ============================
# ✅ Add New Department (Ajax)
# ============================
def add_department(request):
    if request.method == "POST":
        form = DepartmentForm(request.POST)
        if form.is_valid():
            department = form.save()
            return JsonResponse({"success": True, "id": department.id, "name": department.name})
    return JsonResponse({"success": False})


# ============================
# ✅ Add New CourseType (Ajax)
# ============================
def add_course_type(request):
    if request.method == "POST":
        form = CourseTypeForm(request.POST)
        if form.is_valid():
            course_type = form.save()
            return JsonResponse({"success": True, "id": course_type.id, "name": course_type.name})
    return JsonResponse({"success": False})


# ============================
# ✅ Promote Students to Next Year
# ============================
def promote_students(request):
    students = Student.objects.filter(status="active")

    for student in students:
        # Final year check logic
        if (
            (student.course_type.name == "UG" and student.year == 3)
            or (student.course_type.name == "PG" and student.year == 2)
            or (student.course_type.name == "4-Year Course" and student.year == 4)
        ):
            student.status = "passout"
        else:
            student.year += 1

        student.save()

    messages.success(request, "✅ Students promoted to the next academic year successfully!")
    return redirect("student_list")


# ============================
# ✅ Student List with Search & Filters
# ============================
def student_list(request):
    search_query = request.GET.get("search", "")
    department_id = request.GET.get("department", "")
    year = request.GET.get("year", "")
    batch = request.GET.get("batch", "")

    students = Student.objects.select_related("department", "course_type").all()

    # Search by name
    if search_query:
        students = students.filter(name__icontains=search_query)

    # Filter by department
    if department_id:
        students = students.filter(department_id=department_id)

    # Filter by year and batch
    if year:
        students = students.filter(year=year)
    if batch:
        students = students.filter(batch=batch)

    context = {
        "students": students,
        "departments": Department.objects.all(),
        "course_types": CourseType.objects.all(),
        "search_query": search_query,
        "department_id": department_id,
        "year": year,
        "batch": batch,
    }
    return render(request, "student_list.html", context)


# ============================
# ✅ Add Student
# ============================
def student_add(request):
    if request.method == "POST":
        form = StudentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Student added successfully!")
            return redirect("student_list")
    else:
        form = StudentForm()
    return render(request, "add_student.html", {"form": form})


# ============================
# ✅ Edit Student
# ============================
def student_edit(request, pk):
    student = get_object_or_404(Student, pk=pk)

    if request.method == "POST":
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Student updated successfully!")
            return redirect("student_list")
    else:
        form = StudentForm(instance=student)
    return render(request, "edit_student.html", {"form": form})


# ============================
# ✅ Delete Student
# ============================
def student_delete(request, pk):
    student = get_object_or_404(Student, pk=pk)
    student.delete()
    messages.success(request, "❌ Student deleted successfully!")
    return redirect("student_list")


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Fine, FineSub
from .forms import FineForm, FineSubForm, FineSubFormSet


# ============================
# List Fine Table
# ============================
def fine_list(request):
    fines = Fine.objects.all()
    return render(request, "fine_list.html", {"fines": fines})


# ============================
# Add Fine and FineSub
# ============================
from django.shortcuts import render, redirect
from .models import Fine, Student
from .forms import FineForm, FineSubFormSet
from django.contrib import messages

def add_fine(request):
    students = Student.objects.all()  # Move this line outside the if-else block

    if request.method == "POST":
        fine_form = FineForm(request.POST)
        formset = FineSubFormSet(request.POST)

        if fine_form.is_valid() and formset.is_valid():
            fine = fine_form.save()
            sub_items = formset.save(commit=False)
            for sub in sub_items:
                sub.fine = fine
                sub.save()

            messages.success(request, "Fine added successfully!")
            return redirect("fine_list")
    else:
        fine_form = FineForm()
        formset = FineSubFormSet()

    return render(request, "add_fine.html", {
        "fine_form": fine_form,
        "formset": formset,
        "students": students,  # Now it will be available in all cases
    })

# ============================
# Edit Fine
# ============================
def edit_fine(request, fine_id):
    fine = get_object_or_404(Fine, pk=fine_id)
    if request.method == "POST":
        fine_form = FineForm(request.POST, instance=fine)
        if fine_form.is_valid():
            fine_form.save()
            messages.success(request, "Fine updated successfully!")
            return redirect("fine_list")
    else:
        fine_form = FineForm(instance=fine)
    return render(request, "edit_fine.html", {"fine_form": fine_form, "fine": fine})


# ============================
# Delete Fine
# ============================
def delete_fine(request, fine_id):
    fine = get_object_or_404(Fine, pk=fine_id)
    fine.delete()
    messages.success(request, "Fine deleted successfully!")
    return redirect("fine_list")


# ============================
# Fine Details (with FineSub)
# ============================
def fine_detail(request, fine_id):
    fine = get_object_or_404(Fine, pk=fine_id)
    sub_items = FineSub.objects.filter(fine=fine)
    form = FineSubForm()
    return render(request, "fine_detail.html", {"fine": fine, "sub_items": sub_items, "form": form})


# ============================
# Add FineSub to Fine
# ============================
def add_fine_sub(request, fine_id):
    fine = get_object_or_404(Fine, pk=fine_id)
    if request.method == "POST":
        form = FineSubForm(request.POST)
        if form.is_valid():
            sub_item = form.save(commit=False)
            sub_item.fine = fine
            sub_item.save()
            messages.success(request, "Fine item added successfully!")
            return redirect("fine_detail", fine_id=fine.id)
    return redirect("fine_detail", fine_id=fine.id)


# ============================
# Edit FineSub
# ============================
def edit_fine_sub(request, sub_id):
    sub_item = get_object_or_404(FineSub, pk=sub_id)
    if request.method == "POST":
        form = FineSubForm(request.POST, instance=sub_item)
        if form.is_valid():
            form.save()
            messages.success(request, "Fine item updated successfully!")
            return redirect("fine_detail", fine_id=sub_item.fine.id)
    else:
        form = FineSubForm(instance=sub_item)
    return render(request, "edit_fine_sub.html", {"form": form, "sub_item": sub_item})


# ============================
# Delete FineSub
# ============================
def delete_fine_sub(request, sub_id):
    sub_item = get_object_or_404(FineSub, pk=sub_id)
    fine_id = sub_item.fine.id
    sub_item.delete()
    messages.success(request, "Fine item deleted successfully!")
    return redirect("fine_detail", fine_id=fine_id)


from django.shortcuts import get_object_or_404, redirect
from .models import Fine
from django.contrib import messages

def toggle_fine_status(request, fine_id):
    fine = get_object_or_404(Fine, pk=fine_id)

    if fine.status == "paid":
        fine.status = "not_paid"
        messages.success(request, "Fine status changed to 'Pay'.")
    else:
        fine.status = "paid"
        messages.success(request, "Fine status changed to 'Paid'.")
    
    fine.save()
    return redirect("fine_list")



from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import PendingPurchase, PendingPurchaseSub
from .forms import PendingPurchaseForm, PendingPurchaseSubForm

# Assistant: Create Purchase Request
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import PendingPurchaseForm, PendingPurchaseSubFormset
from .models import PendingPurchase


from django.shortcuts import render, redirect, get_object_or_404
from django.forms import modelformset_factory
from django.contrib import messages
import pandas as pd
from .models import Purchase, PurchaseSub
from .forms import PurchaseForm, PurchaseSubForm


# ============================
# Create Purchase View
# ============================
from django.shortcuts import render, redirect, get_object_or_404
from django.forms import inlineformset_factory
from django.contrib import messages
from .models import Purchase, PurchaseSub
from .forms import PurchaseForm, PurchaseSubForm
import pandas as pd

def create_purchase(request):
    # Formset for PurchaseSub
    PurchaseSubFormSet = inlineformset_factory(
        Purchase, PurchaseSub, form=PurchaseSubForm, extra=1, can_delete=True
    )

    # Initialize forms to avoid UnboundLocalError
    purchase_form = PendingPurchaseForm()
    formset = PendingPurchaseSubFormset()

    if request.method == 'POST':
        # Handling Excel Upload
        if 'upload_submit' in request.POST:
            purchase_form = PendingPurchaseForm(request.POST)
            
            if purchase_form.is_valid():
                purchase = purchase_form.save()
                purchase.created_by = request.user.username
                purchase.save()
                excel_file = request.FILES.get('excel_file')

                if excel_file:
                    try:
                        df = pd.read_excel(excel_file, engine='openpyxl')
                        for index, row in df.iterrows():
                            PendingPurchaseSub.objects.create(
                                purchase=purchase,
                                code=row.get('code', ''),
                                name_of_item=row.get('name_of_item', ''),
                                quantity=row.get('quantity', ''),
                                nos=row.get('nos', 0),
                                rate=row.get('rate', 0.00),
                                cgst_rate=row.get('cgst_rate', 0.00),
                                sgst_rate=row.get('sgst_rate', 0.00)
                            )
                        messages.success(request, "Items uploaded successfully!")
                        # ✅ Correct redirect
                        return redirect('pending_purchase_assistant')
                    except Exception as e:
                        messages.error(request, f"Error: {str(e)}")
                        return redirect('create_purchase')

        # Handling Manual Entry
        elif 'manual_submit' in request.POST:
            purchase_form = PendingPurchaseForm(request.POST)
            formset = PendingPurchaseSubFormset(request.POST)

            if purchase_form.is_valid():
                purchase = purchase_form.save(commit=False)
                purchase.created_by = request.user.username
                purchase.save()
                
                if formset.is_valid():
                    sub_items = formset.save(commit=False)
                    for item in sub_items:
                        item.purchase = purchase
                        item.save()
                    
                    messages.success(request, "Purchase added successfully!")
                    # ✅ Correct redirect
                    return redirect('pending_purchase_assistant')
            else:
                # If form is invalid, reinitialize the formset with POST data
                formset = PendingPurchaseSubFormset(request.POST)

    # If it's a GET request or form submission fails, render the form with errors
    return render(request, 'create_purchase.html', {
        'form': purchase_form,
        'formset': formset
    })


def edit_purchase_sub(request, sub_id):
    # ✅ Get the PurchaseSub object or show 404 if not found
    purchase_sub = get_object_or_404(PurchaseSub, id=sub_id)

    if request.method == 'POST':
        # ✅ Bind form with request data and instance of purchase_sub
        form = PurchaseSubForm(request.POST, instance=purchase_sub)
        if form.is_valid():
            purchase_sub = form.save()

            # ✅ Check if purchase_sub has a valid purchase before redirecting
            if purchase_sub.purchase:
                return redirect(reverse('purchase_detail', args=[purchase_sub.purchase.id]))
            else:
                # ✅ Fallback if purchase is missing
                print("❌ No purchase associated with this sub-item!")
                return redirect('purchase_list')  # Fallback to purchase list if no purchase is linked
    else:
        # ✅ Render the form with the existing purchase_sub instance
        form = PurchaseSubForm(instance=purchase_sub)

    # ✅ Render the edit page with form and sub-item data
    return render(request, 'myapp/purchase_sub_edit.html', {'form': form, 'purchase_sub': purchase_sub})

@login_required
def pending_purchase_assistant(request):
    purchases = PendingPurchase.objects.filter(status='Pending')
    return render(request, 'pending_purchase_assistant.html', {'purchases': purchases})

# HOD: View Pending Purchases
@login_required
def pending_purchases(request):
    purchases = PendingPurchase.objects.filter(status='Pending')
    return render(request, 'pending_purchases.html', {'purchases': purchases})


# ============================
# HOD: View Pending Purchase Details
# ============================
@login_required
def pending_purchase_detail(request, pk):
    purchase = get_object_or_404(PendingPurchase, pk=pk)
    return render(request, 'pending_purchase_detail.html', {'purchase': purchase})


# ============================
# HOD: Approve Purchase
# ============================
@login_required
def approve_purchase(request, pk):
    purchase = get_object_or_404(PendingPurchase, pk=pk)

    # Move data to approved Purchase tables
    new_purchase = Purchase.objects.create(
        purchase_no=purchase.purchase_no,
        supplier_code=purchase.supplier_code,
        date=purchase.date,
        invoice_no=purchase.invoice_no,
        total_amount=purchase.total_amount,
    )

    for item in purchase.pending_items.all():
        PurchaseSub.objects.create(
            purchase=new_purchase,
            code=item.code,  # New Column
            name_of_item=item.name_of_item,
            quantity=item.quantity,
            nos=item.nos,
            rate=item.rate,
            total_amount=item.total_amount,
            cgst_rate=item.cgst_rate,
            cgst_amount=item.cgst_amount,
            sgst_rate=item.sgst_rate,
            sgst_amount=item.sgst_amount,
        )

    # Delete PendingPurchase and PendingPurchaseSub
    purchase.delete()
    return redirect('pending_purchases')


# ============================
# HOD: Discard Purchase
# ============================
@login_required
def discard_purchase(request, pk):
    purchase = get_object_or_404(PendingPurchase, pk=pk)
    purchase.delete()
    return redirect('pending_purchases')


import pandas as pd
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Purchase, PurchaseSub


def upload_excel(request, purchase_id):
    # Get the purchase object
    purchase = get_object_or_404(Purchase, pk=purchase_id)

    if request.method == 'POST' and request.FILES.get('excel_file'):
        excel_file = request.FILES['excel_file']

        try:
            # Read Excel file
            df = pd.read_excel(excel_file, engine='openpyxl')

            # Required columns
            required_columns = ['code', 'name_of_item', 'quantity', 'nos', 'rate', 'cgst_rate', 'sgst_rate']

            # Validate Excel columns
            if not all(column in df.columns for column in required_columns):
                messages.error(request, 'Invalid Excel format. Please include all required columns.')
                return redirect(request.META.get('HTTP_REFERER', '/'))

            # Loop through rows and create PurchaseSub objects
            for _, row in df.iterrows():
                PurchaseSub.objects.create(
                    purchase=purchase,
                    code=row['code'],
                    name_of_item=row['name_of_item'],
                    quantity=row['quantity'],
                    nos=row['nos'],
                    rate=row['rate'],
                    cgst_rate=row['cgst_rate'],
                    sgst_rate=row['sgst_rate'],
                    total_amount=(row['nos'] * row['rate']) + ((row['nos'] * row['rate'] * row['cgst_rate']) / 100) + ((row['nos'] * row['rate'] * row['sgst_rate']) / 100)
                )

            # Success message and redirect to same page
            messages.success(request, "Items uploaded successfully!")
            return redirect(request.META.get('HTTP_REFERER', f'/purchase/{purchase_id}/'))

        except Exception as e:
            messages.error(request, f'Error processing file: {str(e)}')
            return redirect(request.META.get('HTTP_REFERER', f'/purchase/{purchase_id}/'))

    messages.error(request, "No file uploaded!")
    return redirect(request.META.get('HTTP_REFERER', f'/purchase/{purchase_id}/'))


def purchase_details(request, purchase_id):
    # Get the purchase object based on the provided ID
    purchase = get_object_or_404(Purchase, pk=purchase_id)

    # Retrieve all sub-items related to the purchase
    sub_items = PurchaseSub.objects.filter(purchase=purchase)

    # Create an empty form for adding new items
    form = PurchaseSubForm()

    # Pass data to the template
    return render(request, 'purchase_details.html', {
        'purchase': purchase,
        'sub_items': sub_items,
        'form': form
    })
from django.shortcuts import render, get_object_or_404, redirect
from .models import Chemical, ChemicalSub
from .forms import ChemicalForm, ChemicalSubForm
from django.utils.timezone import now
from django.forms import inlineformset_factory

# ============================
# Display List of Chemicals
# ============================
def chemical_list(request):
    chemicals = Chemical.objects.all()
    return render(request, 'chemical_list.html', {'chemicals': chemicals})

# ============================
# View ChemicalSub Details
# ============================
def chemical_detail(request, chem_id):
    chemical = get_object_or_404(Chemical, id=chem_id)
    sub_chemicals = ChemicalSub.objects.filter(chem_id=chemical)

    today = now().date()  # Get today's date

    # Process each sub-chemical to add highlighting properties
    for sub in sub_chemicals:
        sub.is_low_quantity = sub.total_quantity < 100  # Highlight if < 100
        sub.is_expired = sub.exp_date and sub.exp_date < today  # Highlight if expired
        sub.is_critical = sub.is_low_quantity and sub.is_expired  # Both conditions met

    context = {
        'chemical': chemical,
        'sub_chemicals': sub_chemicals,
        'today': today,  
    }
    return render(request, 'chemical_detail.html', context)
# ============================
# Add/Edit Chemical
# ============================
def chemical_create(request):
    if request.method == 'POST':
        form = ChemicalForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('chemical_list')
    else:
        form = ChemicalForm()
    return render(request, 'chemical_form.html', {'form': form})

# ============================
# Add ChemicalSub for a Chemical
# ============================
def chemicalsub_create(request, chem_id):
    chemical = get_object_or_404(Chemical, id=chem_id)
    ChemicalSubFormSet = inlineformset_factory(Chemical, ChemicalSub, fields=('code', 'company', 'fund', 'exp_date', 'quantity', 'nos'), extra=1)

    if request.method == 'POST':
        formset = ChemicalSubFormSet(request.POST, instance=chemical)
        if formset.is_valid():
            formset.save()
            return redirect('chemical_detail', chem_id=chem_id)
    else:
        formset = ChemicalSubFormSet(instance=chemical)
    return render(request, 'chemicalsub_form.html', {'formset': formset, 'chemical': chemical})
from django.shortcuts import render, get_object_or_404, redirect
from .models import Chemical, ChemicalSub
from .forms import ChemicalSubForm

# Edit ChemicalSub
def chemicalsub_edit(request, pk):
    sub = get_object_or_404(ChemicalSub, pk=pk)
    if request.method == 'POST':
        form = ChemicalSubForm(request.POST, instance=sub)
        if form.is_valid():
            form.save()
            return redirect('chemical_detail', sub.chem_id.id)

    else:
        form = ChemicalSubForm(instance=sub)

    return render(request, 'chemicalsubedit_form.html', {'form': form, 'chemical': sub.chem_id})

# Delete ChemicalSub
def chemicalsub_delete(request, pk):
    sub = get_object_or_404(ChemicalSub, pk=pk)
    chemical_id = sub.chem_id.id
    sub.delete()
    return redirect('chemical_detail', pk=chemical_id)

# views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from .models import DailyUsage, ChemicalSub
from .forms import DailyUsageForm
from django.db.models import Sum


# ============================
# Daily Usage List
# ============================
def dailyusage_list(request):
    usages = DailyUsage.objects.all()
    return render(request, 'dailyusage_list.html', {'usages': usages})


# ============================
# Create Daily Usage
# ============================
def dailyusage_create(request):
    if request.method == 'POST':
        form = DailyUsageForm(request.POST)
        if form.is_valid():
            usage = form.save()
            return redirect('dailyusage_list')
    else:
        form = DailyUsageForm()

    return render(request, 'dailyusage_form.html', {'form': form})


# ============================
# Edit Daily Usage
# ============================
def dailyusage_edit(request, usage_id):
    usage = get_object_or_404(DailyUsage, pk=usage_id)

    if request.method == 'POST':
        form = DailyUsageForm(request.POST, instance=usage)
        if form.is_valid():
            form.save()
            return redirect('dailyusage_list')
    else:
        form = DailyUsageForm(instance=usage)

    return render(request, 'dailyusage_form.html', {'form': form})


# ============================
# Delete Daily Usage
# ============================
def dailyusage_delete(request, usage_id):
    usage = get_object_or_404(DailyUsage, pk=usage_id)
    if request.method == 'POST':
        # Add the quantity back to ChemicalSub before deleting
        usage.item.total_quantity += usage.quantity
        usage.item.save()
        usage.delete()
        usage.item.chem_id.update_total_quantity()
        return redirect('dailyusage_list')

    return render(request, 'dailyusage_confirm_delete.html', {'usage': usage})


from django.shortcuts import render, get_object_or_404, redirect
from .models import Item, ItemSub
from .forms import ItemForm, ItemSubForm
from django.forms import inlineformset_factory

# ============================
# List All Items
# ============================
def item_list(request):
    items = Item.objects.all()
    return render(request, 'item_list.html', {'items': items})


# ============================
# Item Detail with Sub-Items
# ============================
def item_detail(request, pk):
    """
    Display item details and its sub-items.
    """
    item = get_object_or_404(Item, id=pk)
    item_subs = ItemSub.objects.filter(item_id=item)
    return render(request, 'item_detail.html', {'item': item, 'item_subs': item_subs})


# ============================
# Create Item
# ============================
def item_create(request):
    if request.method == 'POST':
        form = ItemForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('item_list')
    else:
        form = ItemForm()
    return render(request, 'item_form.html', {'form': form})


# ============================
# Edit Item
# ============================
def item_edit(request, pk):
    item = get_object_or_404(Item, id=pk)
    if request.method == 'POST':
        form = ItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect('item_list')
    else:
        form = ItemForm(instance=item)
    return render(request, 'item_form.html', {'form': form})


# ============================
# Delete Item
# ============================
def item_delete(request, pk):
    item = get_object_or_404(Item, id=pk)
    item.delete()
    return redirect('item_list')


# ============================
# Create ItemSub for an Item
# ============================
def itemsub_create(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    if request.method == 'POST':
        form = ItemSubForm(request.POST)
        if form.is_valid():
            item_sub = form.save(commit=False)
            item_sub.item_id = item
            item_sub.save()
            return redirect('item_detail', pk=item.id)
    else:
        form = ItemSubForm()
    return render(request, 'itemsub_form.html', {'form': form, 'item': item})


# ============================
# Edit ItemSub
# ============================
def itemsub_edit(request, pk):
    item_sub = get_object_or_404(ItemSub, id=pk)
    if request.method == 'POST':
        form = ItemSubForm(request.POST, instance=item_sub)
        if form.is_valid():
            form.save()
            return redirect('item_detail', pk=item_sub.item_id.id)
    else:
        form = ItemSubForm(instance=item_sub)
    return render(request, 'itemsub_edit.html', {'form': form, 'item': item_sub.item_id})


# ============================
# Delete ItemSub
# ============================
def itemsub_delete(request, pk):
    item_sub = get_object_or_404(ItemSub, id=pk)
    item_id = item_sub.item_id.id
    item_sub.delete()
    return redirect('item_detail', pk=item_id)

from django.db.models.signals import post_save
from django.dispatch import receiver
from myapp.models import PurchaseSub, Item, ItemSub

@receiver(post_save, sender=PurchaseSub)
def update_item_sub(sender, instance, created, **kwargs):
    """
    Signal to sync PurchaseSub with ItemSub when a purchase is added or updated.
    """
    try:
        # ✅ Check if Item with name_of_item exists
        item = Item.objects.get(name=instance.name_of_item)

        # ✅ Check if a matching ItemSub exists with the same code
        item_sub, created = ItemSub.objects.get_or_create(
            item_id=item,
            item_code=instance.code,
            defaults={
                'company': '',
                'fund': '',  # Default fund
                'condition': 'working',  # Default condition
                'price': instance.rate,  # ✅ Use rate as price
            }
        )

        if not created:
            # ✅ Update existing ItemSub if not newly created
            item_sub.company =  ''
            item_sub.fund = ''
            item_sub.price = instance.rate
            item_sub.save()

        # ✅ Update quantity in Item after adding/updating ItemSub
        item.update_quantity()

    except Item.DoesNotExist:
        # ✅ Skip if no matching Item found
        pass


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import DailyUsagePending, ChemicalSub, DailyUsage

from django.shortcuts import render, redirect, get_object_or_404
from .models import DailyUsagePending, DailyUsage
from .forms import DailyUsagePendingForm
from django.contrib import messages

def add_daily_usage(request):
    if request.method == 'POST':
        form = DailyUsagePendingForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Daily usage added successfully!")
            return redirect('pending_usages_store')
    else:
        form = DailyUsagePendingForm()
    
    return render(request, 'create_daily_usage.html', {'form': form})

def pending_usages_list(request):
    pending_usages = DailyUsagePending.objects.all()
    return render(request, 'pending_usages_list.html', {'pending_usages': pending_usages})
def pending_usages_store(request):
    pending_usages = DailyUsagePending.objects.all()
    return render(request, 'pending_usages_store.html', {'pending_usages': pending_usages})

# ========== Approve Daily Usage ==========

def approve_daily_usage(request, usage_id):
    pending_usage = get_object_or_404(DailyUsagePending, usage_id=usage_id)
    chemical_sub = get_object_or_404(ChemicalSub, id=pending_usage.item.id)
    
    # Check if there's enough stock
    if chemical_sub.total_quantity >= pending_usage.quantity:
        # Reduce the quantity in ChemicalSub
        chemical_sub.total_quantity -= pending_usage.quantity
        chemical_sub.save()  # Save the updated ChemicalSub
        
        # Create a new DailyUsage record
        DailyUsage.objects.create(
            date=pending_usage.date,
            time=pending_usage.time,
            item=pending_usage.item,
            quantity=pending_usage.quantity,
            batch=pending_usage.batch
        )
        
        # Delete the pending usage
        pending_usage.delete()
        
        # Update the total quantity in the Chemical model
        chemical_sub.chem_id.update_total_quantity()

        messages.success(request, "Usage approved and deducted from stock successfully!")
    else:
        messages.error(request, "Not enough stock available to approve this usage!")

    return redirect('pending_usages_list')

def discard_daily_usage(request, usage_id):
    # This will be used when accessing the view through the URL
    if request.method == "POST":
        # Get the usage_id from the POST data (hidden input)
        usage_id = request.POST.get('usage_id')

        # Make sure the usage_id is valid
        if usage_id:
            # Now fetch the pending usage object
            pending_usage = get_object_or_404(DailyUsagePending, usage_id=usage_id)
            pending_usage.delete()

            # Show success message
            messages.warning(request, "Usage discarded successfully!")

            # Redirect to the pending usages list
            return redirect('pending_usages_list')
        else:
            messages.error(request, "Invalid usage ID.")
            return redirect('pending_usages_list')
        
        
from django.http import JsonResponse
from django.shortcuts import render
from django.db.models import Count
from myapp.models import ItemSub


# ✅ Correct API Endpoint to Fetch Status from ItemSub
def lab_item_status(request):
    categories = ['Glassware', 'Equipment', 'Furniture']
    status_labels = ['working', 'repair', 'damaged']

    # ✅ Initialize the data dictionary
    status_data = {status: [0] * len(categories) for status in status_labels}

    # ✅ Loop through categories and conditions to get counts
    for category in categories:
        for status in status_labels:
            count = ItemSub.objects.filter(
                item_id__category__name__iexact=category,  # Corrected field lookup
                condition__iexact=status
            ).count()
            status_data[status][categories.index(category)] = count

    # ✅ Prepare and return data for Chart.js
    data = {
        'labels': categories,
        'working': status_data['working'],
        'repair': status_data['repair'],
        'damaged': status_data['damaged'],
    }

    return JsonResponse(data)


# ✅ Render home_hod.html correctly
def home_view(request):
    return render(request, 'myapp/home_hod.html')



from django.http import FileResponse
import os
from django.conf import settings
def download_excel_template(request):
    file_path = os.path.join(settings.BASE_DIR, 'myapp/static/excel/import_asset_template.xlsx')
    return FileResponse(open(file_path, 'rb'), as_attachment=True, filename='import_asset_template.xlsx') 


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .forms import ChemicalForm
from .models import Chemical

def chemical_edit(request, pk):
    chemical = get_object_or_404(Chemical, pk=pk)
    if request.method == 'POST':
        form = ChemicalForm(request.POST, instance=chemical)
        if form.is_valid():
            form.save()
            messages.success(request, 'Chemical updated successfully!')
            return redirect('chemical_list')
    else:
        form = ChemicalForm(instance=chemical)
    return render(request, 'chemical_form.html', {'form': form})


from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import Chemical

def chemical_delete(request, pk):
    chemical = get_object_or_404(Chemical, pk=pk)
    chemical.delete()
    messages.success(request, f'{chemical.name} has been deleted successfully.')
    return redirect('chemical_list')

def item_edit(request, pk):
    item = get_object_or_404(Item, pk=pk)
    if request.method == 'POST':
        form = ItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect('item_list')
    else:
        form = ItemForm(instance=item)
    return render(request, 'item_edit.html', {'form': form, 'item': item})

# Item Delete View
def item_delete(request, pk):
    item = get_object_or_404(Item, pk=pk)
    if request.method == 'POST':
        item.delete()
        return redirect('item_list')
    return render(request, 'item_confirm_delete.html', {'item': item})


import pandas as pd
from django.shortcuts import render
from django.http import JsonResponse
from .models import Student, Department, CourseType

def upload_students(request):
    if request.method == "POST" and request.FILES.get("excelFile"):
        excel_file = request.FILES["excelFile"]

        try:
            # Read Excel File
            df = pd.read_excel(excel_file)

            for _, row in df.iterrows():
                department, _ = Department.objects.get_or_create(name=row["Department"])
                course_type, _ = CourseType.objects.get_or_create(name=row["Course Type"])

                # Create Student Entry
                Student.objects.create(
                    admission_no=row["Admission No"],
                    roll_no=row["Roll No"],
                    name=row["Name"],
                    department=department,
                    year=row["Year"],
                    course_type=course_type,
                    status=row["Status"].lower(),
                    batch=row["Batch"]
                )

            return JsonResponse({"success": True, "message": "Students uploaded successfully!"})
        
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})

    return JsonResponse({"success": False, "message": "Invalid request"})


def usage_edit(request, pk):
    usage = get_object_or_404(DailyUsage, pk=pk)

    if request.method == "POST":
        form = DailyUsageForm(request.POST, instance=usage)
        if form.is_valid():
            form.save()
            messages.success(request, "DailyUsage updated successfully!")
            return redirect("dailyusage_list")
    else:
        form = DailyUsageForm(instance=usage)
    return render(request, "edit_usage.html", {"form": form})


def usage_add(request):
    if request.method == "POST":
        form = DailyUsageForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, " Dailyusage added successfully!")
            return redirect("dailyusage_list")
    else:
        form = DailyUsageForm()
    return render(request, "add_usage.html", {"form": form})


from .forms import SupplierForm 

def supplier_edit(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)

    if request.method == "POST":
        form =SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Student updated successfully!")
            return redirect("supplier_list")
    else:
        form = SupplierForm(instance=supplier)
    return render(request, "edit_supplier.html", {"form": form})

def supplier_delete(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    supplier.delete()
    messages.success(request, "❌ Supplier deleted successfully!")
    return redirect("supplier_list")

