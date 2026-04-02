import os
import django
import csv

# 1. Setup Django Environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clis.settings')
django.setup()

from myapp.models import Chemical, ChemicalSub, Item, ItemSub

def import_chemicals():
    print("--- Importing Chemicals ---")
    try:
        with open('legacy_data/chemicals.csv', 'r', encoding='latin1') as f:
            reader = list(csv.reader(f))
            name_idx, code_idx, kg_idx = -1, -1, -1

            # Step 1: Scan every row to find where the table actually starts
            for r_idx, row in enumerate(reader):
                clean_row = [str(c).strip().upper() for c in row]
                for c_idx, cell in enumerate(clean_row):
                    if 'PASSWORD123' in cell: name_idx = c_idx
                    if 'CHEMICAL NO' in cell: code_idx = c_idx
                    if 'BALANCE TOTAL' in cell or 'BALANCE' in cell: kg_idx = c_idx
                
                if name_idx != -1 and kg_idx != -1:
                    start_row = r_idx + 1
                    break
            else:
                print("❌ Error: Could not find 'PASSWORD123' or 'BALANCE' columns in chemicals.csv")
                return

            # Step 2: Process data from that point forward
            for row in reader[start_row:]:
                if len(row) > max(name_idx, kg_idx):
                    chem_name = row[name_idx].strip()
                    chem_code = row[code_idx].strip() if code_idx != -1 else ""
                    kg_val = row[kg_idx].strip()

                    if not chem_name or chem_name.upper() == 'NAN' or 'PASSWORD123' in chem_name.upper():
                        continue

                    category = 'Organic' if 'OR' in chem_code.upper() else 'Inorganic'
                    chemical, _ = Chemical.objects.get_or_create(
                        name=chem_name, 
                        defaults={'category': category, 'minimum_amount': 100}
                    )

                    try:
                        total_kg = float(kg_val) if kg_val else 0
                    except ValueError:
                        total_kg = 0

                    if total_kg > 0:
                        ChemicalSub.objects.create(
                            chemical=chemical, quantity=int(total_kg*1000),
                            available_amount=int(total_kg*1000), state='Solid',
                            company='Legacy Stock', fund='Legacy'
                        )
                        print(f"✅ Added {total_kg}kg of {chem_name}")

    except Exception as e:
        print(f"Error: {e}")

def import_glassware():
    print("\n--- Importing Glassware ---")
    try:
        with open('legacy_data/glassware.csv', 'r', encoding='latin1') as f:
            reader = list(csv.reader(f))
            name_idx, code_idx, stock_idx = -1, -1, -1

            for r_idx, row in enumerate(reader):
                clean_row = [str(c).strip().upper() for c in row]
                for c_idx, cell in enumerate(clean_row):
                    if 'PASSWORD123' in cell: name_idx = c_idx
                    if 'GLASS WARE NO' in cell: code_idx = c_idx
                    if 'BALANCE TOTAL' in cell or 'BALANCE' in cell: stock_idx = c_idx
                
                if name_idx != -1 and stock_idx != -1:
                    start_row = r_idx + 1
                    break
            else:
                print("❌ Error: Could not find columns in glassware.csv")
                return

            for row in reader[start_row:]:
                if len(row) > max(name_idx, stock_idx):
                    item_name = row[name_idx].strip()
                    item_code = row[code_idx].strip() if code_idx != -1 else "GL"
                    stock_val = row[stock_idx].strip()

                    if not item_name or item_name.upper() == 'NAN' or 'PASSWORD123' in item_name.upper():
                        continue

                    item, _ = Item.objects.get_or_create(name=item_name, defaults={'category': 'Glassware', 'type': 'Consumable'})
                    
                    try:
                        count = int(float(stock_val)) if stock_val else 0
                    except ValueError:
                        count = 0

                    for i in range(count):
                        ItemSub.objects.create(item=item, code=f"{item_code}-{i+1}", condition='Working')
                    if count > 0: print(f"✅ Added {count} units of {item_name}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    import_chemicals()
    import_glassware()
    print("\n🚀 All done!")