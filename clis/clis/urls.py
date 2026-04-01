"""
URL configuration for clis project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from myapp import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("home/hod/", views.hod_dashboard, name="hod_home"),
    path("home/assistant/", views.assistant_dashboard, name="assistant_home"),
    path("home/storekeeper/", views.storekeeper_dashboard, name="storekeeper_home"),

    path("purchase/", views.purchase_list, name="purchase_list"),
    path("purchase/add/", views.add_purchase, name="add_purchase"),
    path("purchase/edit/<int:purchase_id>/", views.edit_purchase, name="edit_purchase"),
    path("purchase/delete/<int:purchase_id>/", views.delete_purchase, name="delete_purchase"),
    
    path("purchase/<int:purchase_id>/", views.purchase_detail, name="purchase_detail"),
    path("purchase/<int:purchase_id>/add_sub/", views.add_purchase_sub, name="add_purchase_sub"),
    path("purchase/sub/edit/<int:sub_id>/", views.edit_purchase_sub, name="edit_purchase_sub"),
    path("purchase/sub/delete/<int:sub_id>/", views.delete_purchase_sub, name="delete_purchase_sub"),
    path("purchase/<int:purchase_id>/add_sub/", views.add_purchase_sub, name="add_purchase_sub"),

    path("suppliers/", views.supplier_list, name="supplier_list"),
    path("suppliers/add/", views.add_supplier, name="add_supplier"),
    path("supplier_edit/<int:pk>/", views.supplier_edit, name="supplier_edit"),
    path("suppliers/delete/<int:pk>/", views.supplier_delete, name="supplier_delete"),

    path("add/", views.student_add, name="student_add"),
    path("edit/<int:pk>/", views.student_edit, name="student_edit"),
    path("delete/<int:pk>/", views.student_delete, name="student_delete"),
    path("add/", views.student_add, name="student_add"),
    path("edit/<int:pk>/", views.student_edit, name="student_edit"),
    path('students/', views.student_list, name='student_list'),
    path("delete/<int:pk>/", views.student_delete, name="student_delete"),
    path("add_department/", views.add_department, name="add_department"),
    path("add_course_type/", views.add_course_type, name="add_course_type"),
    path("promote_students/", views.promote_students, name="promote_students"),

   path('fines/', views.fine_list, name='fine_list'), 
    path("fine/add/", views.add_fine, name="add_fine"),
    path("fine/edit/<int:fine_id>/", views.edit_fine, name="edit_fine"),
    path("fine/delete/<int:fine_id>/", views.delete_fine, name="delete_fine"),
    path("fine/<int:fine_id>/", views.fine_detail, name="fine_detail"),
    path("fine/<int:fine_id>/add_sub/", views.add_fine_sub, name="add_fine_sub"),
    path("fine/sub/edit/<int:sub_id>/", views.edit_fine_sub, name="edit_fine_sub"),
    path("fine/sub/delete/<int:sub_id>/", views.delete_fine_sub, name="delete_fine_sub"),
    path('fine/toggle_status/<int:fine_id>/', views.toggle_fine_status, name='toggle_fine_status'),

    path('create/', views.create_purchase, name='create_purchase'),
    path('pending/', views.pending_purchases, name='pending_purchases'),
    path('pending_assistant/', views.pending_purchase_assistant, name='pending_purchase_assistant'),
    path('pending/<int:pk>/', views.pending_purchase_detail, name='pending_purchase_detail'),
    path('pending/<int:pk>/approve/', views.approve_purchase, name='approve_purchase'),
    path('pending/<int:pk>/discard/', views.discard_purchase, name='discard_purchase'),

    path('purchase/<int:purchase_id>/upload_excel/', views.upload_excel, name='upload_excel'),
    path('purchase/<int:purchase_id>/', views.purchase_details, name='purchase_details'),
    path('purchase/<int:purchase_id>/upload_excel/', views.upload_excel, name='upload_excel'),
    path('purchase/sub/delete/<int:sub_id>/', views.delete_purchase_sub, name='delete_purchase_sub'),
    path('purchase/sub/edit/<int:purchase_sub_id>/', views.edit_purchase_sub, name='purchase_edit_sub'),  # ✅ Correct URL

    path('chemicals/', views.chemical_list, name='chemical_list'),
    path('chemical/<int:chem_id>/', views.chemical_detail, name='chemical_detail'),
     path('chemical/<int:pk>/', views.chemical_detail, name='chemical_detail'),
    path('chemical/add/', views.chemical_create, name='chemical_create'),
    path('chemical/<int:chem_id>/add-sub/', views.chemicalsub_create, name='chemicalsub_create'),
    path('chemicalsub/<int:pk>/edit/', views.chemicalsub_edit, name='chemicalsub_edit'),
    path('chemicalsub/<int:pk>/delete/', views.chemicalsub_delete, name='chemicalsub_delete'),
    
    path('dailyusage/', views.dailyusage_list, name='dailyusage_list'),
    path('dailyusage/new/', views.dailyusage_create, name='dailyusage_create'),
    
    path('dailyusage_update/<int:usage_id>/', views.dailyusage_edit, name='dailyusage_update'),


    path('dailyusage_delete/<int:usage_id>/', views.dailyusage_delete, name='dailyusage_delete'),


    path('item/add/', views.item_create, name='item_create'),
    path('item/<int:pk>/', views.item_detail, name='item_detail'),
    path('item/<int:pk>/edit/', views.item_edit, name='item_edit'),
    path('item/<int:pk>/delete/', views.item_delete, name='item_delete'),

    # ============================
    # ItemSub URLs
    # ============================
    path('item/<int:item_id>/subitem/add/', views.itemsub_create, name='itemsub_create'),
    path('subitem/<int:pk>/edit/', views.itemsub_edit, name='itemsub_edit'),
    path('subitem/<int:pk>/delete/', views.itemsub_delete, name='itemsub_delete'),

    path('items/', views.item_list, name='item_list'),  # Ensure this is defined

    # ============================
    # ItemSub URLs
    # ============================
    path('item/<int:item_id>/subitem/add/', views.itemsub_create, name='itemsub_create'),
    path('subitem/<int:pk>/edit/', views.itemsub_edit, name='itemsub_edit'),
    path('subitem/<int:pk>/delete/', views.itemsub_delete, name='itemsub_delete'),


    
    path('dashboard/hod/', views.home_view, name='dashboard_hod'),
    path('dashboard/assistant/', views.assistant_dashboard, name='dashboard_assistant'),
    path('dashboard/storekeeper/', views.storekeeper_dashboard, name='dashboard_storekeeper'),

    path('pending-usages/', views.pending_usages_list, name='pending_usages_list'),
    path('pending-usages-store/', views.pending_usages_store, name='pending_usages_store'),
    # path('approve-usage/<int:usage_id>/', views.approve_daily_usage, name='approve_daily_usage'),
    path('discard-usage/<int:usage_id>/', views.discard_daily_usage, name='discard_daily_usage'),
    

    path('add-daily-usage/', views.add_daily_usage, name='add_daily_usage'),


    path('api/lab-item-status/', views.lab_item_status, name='lab_item_status'),

    path('download-template/', views.download_excel_template, name='download_excel_template'),

     path('chemicals/edit/<int:pk>/', views.chemical_edit, name='chemical_edit'),
    path('chemicals/delete/<int:pk>/', views.chemical_delete, name='chemical_delete'),

     path('item/edit/<int:pk>/', views.item_edit, name='item_edit'),
    path('item/delete/<int:pk>/', views.item_delete, name='item_delete'),

   path('approve_daily_usage/<int:usage_id>/', views.approve_daily_usage, name='approve_daily_usage'),

   path("upload_students/", views.upload_students, name="upload_students"),

path("usage_edit/<int:pk>/", views.usage_edit, name="usage_edit"),

    path("add_usage/", views.usage_add, name="usage_add"),
]
