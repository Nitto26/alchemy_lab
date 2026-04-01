from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import PurchaseSub, Chemical, ChemicalSub


@receiver(post_save, sender=PurchaseSub)
def update_chemical_sub(sender, instance, created, **kwargs):
    """
    Signal to sync PurchaseSub with ChemicalSub when a purchase is added or updated.
    """

    try:
        # Check if Chemical with name_of_item exists
        chemical = Chemical.objects.get(name=instance.name_of_item)

        # Check if a matching ChemicalSub exists with the same code
        chemical_sub, created = ChemicalSub.objects.get_or_create(
            chem_id=chemical,
            code=instance.code,
            defaults={
                'company': 'Default Company',
                'fund': 'Default Fund',
                'exp_date': '2025-12-31',
                'quantity': instance.quantity,
                'nos': instance.nos,
                'total_quantity': int(instance.nos) * int(instance.quantity)
            }
        )

        if not created:
            # Update existing ChemicalSub if not newly created
            chemical_sub.nos += instance.nos
            chemical_sub.total_quantity = chemical_sub.nos * int(instance.quantity)
            chemical_sub.save()

        # Update the total quantity in Chemical
        chemical.update_total_quantity()

    except Chemical.DoesNotExist:
        # Skip if no matching Chemical found
        pass

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import DailyUsage, ChemicalSub


# ============================
# Update ChemicalSub after DailyUsage Save
# ============================
from django.db.models import Sum
from django.db.models import models

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import DailyUsage, ChemicalSub


# ============================
# Update ChemicalSub after DailyUsage Save
# ============================
@receiver(post_save, sender=DailyUsage)
def update_chemicalsub_after_usage(sender, instance, **kwargs):
    chemical_sub = instance.item
    total_used_quantity = chemical_sub.daily_usages.aggregate(total=models.Sum('quantity'))['total'] or 0
    chemical_sub.total_quantity = (chemical_sub.nos * chemical_sub.quantity) - total_used_quantity
    chemical_sub.save(update_fields=['total_quantity'])


# ============================
# Update ChemicalSub after DailyUsage Delete
# ============================
@receiver(post_delete, sender=DailyUsage)
def update_chemicalsub_after_delete(sender, instance, **kwargs):
    chemical_sub = instance.item
    total_used_quantity = chemical_sub.daily_usages.aggregate(total=models.Sum('quantity'))['total'] or 0
    chemical_sub.total_quantity = (chemical_sub.nos * chemical_sub.quantity) - total_used_quantity
    chemical_sub.save(update_fields=['total_quantity'])



from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import ItemSub, Item

# ============================
# Update Item Quantity after ItemSub Save
# ============================
@receiver(post_save, sender=ItemSub)
def update_item_sub_count_on_save(sender, instance, **kwargs):
    """
    Updates the quantity of Item when an ItemSub is created or updated.
    """
    instance.item_id.update_quantity()


# ============================
# Update Item Quantity after ItemSub Delete
# ============================
@receiver(post_delete, sender=ItemSub)
def update_item_sub_count_on_delete(sender, instance, **kwargs):
    """
    Updates the quantity of Item when an ItemSub is deleted.
    """
    instance.item_id.update_quantity()

from django.db.models.signals import post_save
from django.dispatch import receiver
from myapp.models import PurchaseSub, Item, ItemSub


from django.db.models.signals import post_save
from django.dispatch import receiver
from myapp.models import PurchaseSub, Item, ItemSub


@receiver(post_save, sender=PurchaseSub)
def update_item_sub(sender, instance, created, **kwargs):
    """
    Signal to sync PurchaseSub with ItemSub when a purchase is added or updated.
    """
    print("✅ Signal Triggered!")  # ✅ Check if signal is triggered

    try:
        # ✅ Check if Item with name_of_item exists
        item = Item.objects.get(name=instance.name_of_item)
        print(f"✅ Item Found: {item.name}")  # ✅ Check if Item is found

        # ✅ Check if a matching ItemSub exists with the same code
        item_sub, created = ItemSub.objects.get_or_create(
            item_id=item,
            item_code=instance.code,
            defaults={
                'company': instance.purchase.supplier_code.name if instance.purchase.supplier_code else 'Default Company',
                'fund': 'Default Fund',
                'condition': 'working',  # Default condition
                'price': instance.rate,  # ✅ Assign rate as price
            }
        )

        if not created:
            print(f"✅ ItemSub Updated: {item_sub.item_code}")
            item_sub.company = instance.purchase.supplier_code.name if instance.purchase.supplier_code else 'Default Company'
            item_sub.fund = 'Default Fund'
            item_sub.price = instance.rate
            item_sub.save()
        else:
            print(f"✅ New ItemSub Created: {item_sub.item_code}")

        # ✅ Update the quantity in Item after adding/updating ItemSub
        item.update_quantity()
        print(f"✅ Quantity Updated for Item: {item.name}")

    except Item.DoesNotExist:
        print(f"❌ No matching Item found for: {instance.name_of_item}")
