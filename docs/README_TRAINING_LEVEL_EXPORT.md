# Training Level Info – Excel & PDF Export

These files document the **Training Level Info** tab content from the Admin Dashboard for your review and confirmation.

## Files

| File | Description |
|------|--------------|
| `Training_Level_Info_Export.xlsx` | Excel workbook with two sheets: **Training Level Info** and **Corrective Movements (Injuries)** |
| `Training_Level_Info_Export.pdf` | PDF report with the same content |

## Content structure (filled with sample data)

### 1. Training Level Information
- **Levels:** Beginner (مبتدی), Intermediate (متوسط), Advanced (پیشرفته)
- **Sub-sections per level:**
  - **Description** (EN/FA)
  - **Goals** (list)
  - **Features for each training purpose** (Lose weight, Gain weight, Gain muscle, Shape fitting):
    - Sessions per week, Sets per action, Reps per action  
    - Training focus (where & tools)  
    - Break between sets  

### 2. Corrective movements for each injury
- **Injuries:** Knee, Shoulder, Lower back, Neck, Wrist, Ankle (EN/FA labels)
- **Sub-sections per injury:**
  - **Purposes / Description** (EN/FA)
  - **Allowed movements** (list)
  - **Forbidden movements** (list)

## Regenerating after changes

1. Edit the sample data in:  
   `scripts/export_training_levels_docs.py`  
   (constants `TRAINING_LEVELS_DATA` and `INJURIES_DATA`).

2. Install dependencies (if needed):  
   `pip install -r scripts/requirements-export.txt`

3. Run:  
   `python scripts/export_training_levels_docs.py`

New Excel and PDF files will be written to this `docs/` folder.
