"""
Export Exercise Library info section to PDF for admin approval.
Run from project root: python scripts/export_exercise_library_docs.py
Output: docs/Exercise_Library_Info_Export.pdf
"""
import os
import sys

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'docs')
PDF_PATH = os.path.join(OUTPUT_DIR, 'Exercise_Library_Info_Export.pdf')
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
BACKEND_DIR = os.path.join(PROJECT_ROOT, 'backend')
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

EXERCISES_INFO = {
    'title_en': 'Exercises',
    'title_fa': 'تمرینات',
    'intro_en': 'This section defines how exercises are added to the library so the AI and training plans can use them safely and consistently.',
    'intro_fa': 'این بخش توضیح می‌دهد تمرین‌ها چگونه به کتابخانه اضافه شوند تا AI و برنامه‌های تمرینی با کیفیت و ایمنی استفاده کنند.',
    'sections': [
        {
            'title_en': 'Required fields',
            'title_fa': 'فیلدهای ضروری',
            'items_en': [
                'Name (FA/EN), Target muscle (FA/EN)',
                'Category, Level, Intensity, Gender suitability',
                'Execution tips & Breathing guide (recommended)',
            ],
            'items_fa': [
                'نام (فارسی/انگلیسی)، عضله هدف (فارسی/انگلیسی)',
                'دسته‌بندی، سطح، شدت، مناسب‌بودن برای جنسیت',
                'نکات اجرا و راهنمای تنفس (ترجیحاً تکمیل شود)',
            ],
        },
        {
            'title_en': 'Quality checklist',
            'title_fa': 'چک‌لیست کیفیت',
            'items_en': [
                'Write short, clear cues for form and breathing',
                'Match intensity to level; avoid advanced cues for beginners',
                'List injuries that should avoid this movement',
            ],
            'items_fa': [
                'راهنمای کوتاه و واضح برای فرم و تنفس بنویسید',
                'شدت را با سطح تمرینی هماهنگ کنید؛ برای مبتدی‌ها پیشرفته ننویسید',
                'آسیب‌هایی که این حرکت برایشان ممنوع است را مشخص کنید',
            ],
        },
        {
            'title_en': 'Media & notes',
            'title_fa': 'رسانه و یادداشت',
            'items_en': [
                'Optional video/image URLs help members perform correctly',
                'Trainer notes can be reused across programs',
            ],
            'items_fa': [
                'ویدیو/تصویر اختیاری برای اجرای صحیح اعضا مفید است',
                'یادداشت مربی می‌تواند در برنامه‌ها استفاده مجدد شود',
            ],
        },
    ],
}


def _rtl_reshape(text):
    """Reshape Persian text for proper RTL display if libs are available."""
    try:
        from arabic_reshaper import ArabicReshaper
        from bidi.algorithm import get_display
    except Exception:
        return text
    reshaper = ArabicReshaper({'use_unshaped_instead_of_isolated': True})
    reshaped = reshaper.reshape(text)
    return get_display(reshaped)


def _rtl_reshape_paragraph(s):
    """Apply reshape+bidi only to text segments, not HTML tags."""
    out = []
    buff = []
    in_tag = False
    for ch in s:
        if ch == '<':
            if buff:
                out.append(_rtl_reshape(''.join(buff)))
                buff = []
            in_tag = True
            out.append(ch)
            continue
        if ch == '>':
            in_tag = False
            out.append(ch)
            continue
        if in_tag:
            out.append(ch)
        else:
            buff.append(ch)
    if buff:
        out.append(_rtl_reshape(''.join(buff)))
    return ''.join(out)


def _load_exercises_from_db():
    try:
        from app import app, db
        from models import Exercise
    except Exception as e:
        print('DB import failed:', e)
        return []
    with app.app_context():
        try:
            rows = Exercise.query.order_by(Exercise.category, Exercise.name_en).all()
        except Exception as e:
            print('DB query failed:', e)
            return []
        out = []
        for ex in rows:
            out.append({
                'name_fa': ex.name_fa or '',
                'name_en': ex.name_en or '',
                'category': ex.category or '',
                'level': ex.level or '',
                'intensity': ex.intensity or '',
                'target_muscle_fa': ex.target_muscle_fa or '',
                'target_muscle_en': ex.target_muscle_en or '',
                'equipment_needed_fa': ex.equipment_needed_fa or '',
                'equipment_needed_en': ex.equipment_needed_en or '',
                'injury_contraindications': ex.injury_contraindications or '',
            })
        return out


def build_pdf():
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.enums import TA_RIGHT
        from reportlab.lib.units import inch
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    except ImportError:
        print('Install: pip install reportlab')
        raise

    vazir_path = os.path.join(PROJECT_ROOT, 'fonts', 'Vazir.ttf')
    if os.path.isfile(vazir_path):
        pdfmetrics.registerFont(TTFont('Vazir', vazir_path))
        pdf_font = 'Vazir'
    else:
        pdf_font = 'Helvetica'

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    doc = SimpleDocTemplate(PDF_PATH, pagesize=A4, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(name='Title', parent=styles['Heading1'], fontName=pdf_font, fontSize=16, spaceAfter=12, alignment=TA_RIGHT, wordWrap='RTL')
    heading_style = ParagraphStyle(name='Heading2', parent=styles['Heading2'], fontName=pdf_font, fontSize=12, spaceAfter=8, alignment=TA_RIGHT, wordWrap='RTL')
    body_style = ParagraphStyle(name='Body', parent=styles['Normal'], fontName=pdf_font, fontSize=9, spaceAfter=4, alignment=TA_RIGHT, wordWrap='RTL')

    story = []
    story.append(Paragraph(_rtl_reshape_paragraph(f"Exercise Library – Export for Confirmation | {EXERCISES_INFO['title_fa']}"), title_style))
    story.append(Spacer(1, 0.2 * inch))

    story.append(Paragraph(_rtl_reshape_paragraph(f"<b>{EXERCISES_INFO['title_en']} | {EXERCISES_INFO['title_fa']}</b>"), heading_style))
    story.append(Paragraph(_rtl_reshape_paragraph(f"EN: {EXERCISES_INFO['intro_en']}"), body_style))
    story.append(Paragraph(_rtl_reshape_paragraph(f"{EXERCISES_INFO['intro_fa']}"), body_style))
    story.append(Spacer(1, 0.12 * inch))

    for section in EXERCISES_INFO['sections']:
        story.append(Paragraph(_rtl_reshape_paragraph(f"<b>{section['title_en']} | {section['title_fa']}</b>"), heading_style))
        for item in section['items_en']:
            story.append(Paragraph(_rtl_reshape_paragraph(f"• {item}"), body_style))
        for item in section['items_fa']:
            story.append(Paragraph(_rtl_reshape_paragraph(f"• {item}"), body_style))
        story.append(Spacer(1, 0.1 * inch))

    exercises = _load_exercises_from_db()
    if exercises:
        story.append(Spacer(1, 0.15 * inch))
        story.append(Paragraph(_rtl_reshape_paragraph("Exercise List | لیست تمرینات"), heading_style))
        for ex in exercises:
            story.append(Paragraph(_rtl_reshape_paragraph(
                f"<b>{ex['name_en']} | {ex['name_fa']}</b>"
            ), body_style))
            story.append(Paragraph(_rtl_reshape_paragraph(
                f"Category: {ex['category']} | Level: {ex['level']} | Intensity: {ex['intensity']}"
            ), body_style))
            story.append(Paragraph(_rtl_reshape_paragraph(
                f"Target: {ex['target_muscle_en']} | {ex['target_muscle_fa']}"
            ), body_style))
            if ex['equipment_needed_en'] or ex['equipment_needed_fa']:
                story.append(Paragraph(_rtl_reshape_paragraph(
                    f"Equipment: {ex['equipment_needed_en']} | {ex['equipment_needed_fa']}"
                ), body_style))
            if ex['injury_contraindications']:
                story.append(Paragraph(_rtl_reshape_paragraph(
                    f"Injuries: {ex['injury_contraindications']}"
                ), body_style))
            story.append(Spacer(1, 0.08 * inch))

    doc.build(story)
    print('PDF saved:', PDF_PATH)


def main():
    build_pdf()


if __name__ == '__main__':
    main()
