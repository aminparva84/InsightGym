"""
Seed script to populate initial data for Raha Fitness
Run this after setting up the database to add sample tips and injury information
"""

from app import app, db, Tip, Injury
from datetime import datetime

def seed_tips():
    """Add sample fitness tips in both Farsi and English"""
    tips = [
        {
            'title_fa': 'اهمیت گرم کردن قبل از ورزش',
            'title_en': 'Importance of Warming Up Before Exercise',
            'content_fa': 'گرم کردن قبل از ورزش باعث افزایش جریان خون به عضلات می‌شود و خطر آسیب را کاهش می‌دهد. حداقل ۵-۱۰ دقیقه قبل از شروع تمرین اصلی، حرکات کششی و گرم کردن انجام دهید.',
            'content_en': 'Warming up before exercise increases blood flow to muscles and reduces the risk of injury. Do at least 5-10 minutes of stretching and warm-up before starting your main workout.',
            'category': 'Warm-up'
        },
        {
            'title_fa': 'اهمیت هیدراتاسیون',
            'title_en': 'Importance of Hydration',
            'content_fa': 'نوشیدن آب کافی در طول روز و به خصوص قبل، حین و بعد از ورزش بسیار مهم است. کمبود آب می‌تواند عملکرد شما را کاهش دهد و خطر آسیب را افزایش دهد.',
            'content_en': 'Drinking enough water throughout the day, especially before, during, and after exercise, is crucial. Dehydration can reduce your performance and increase injury risk.',
            'category': 'Hydration'
        },
        {
            'title_fa': 'تعادل در تمرینات',
            'title_en': 'Balance in Training',
            'content_fa': 'برای بهترین نتایج، ترکیبی از تمرینات قلبی-عروقی، تمرینات قدرتی و تمرینات انعطاف‌پذیری را در برنامه خود بگنجانید. این تعادل به شما کمک می‌کند تا به طور کامل تناسب اندام داشته باشید.',
            'content_en': 'For best results, include a combination of cardiovascular, strength, and flexibility training in your program. This balance helps you achieve overall fitness.',
            'category': 'Training'
        },
        {
            'title_fa': 'استراحت و ریکاوری',
            'title_en': 'Rest and Recovery',
            'content_fa': 'استراحت کافی به اندازه تمرین مهم است. عضلات شما در زمان استراحت ترمیم و قوی‌تر می‌شوند. حداقل یک روز استراحت در هفته داشته باشید.',
            'content_en': 'Adequate rest is as important as training. Your muscles repair and grow stronger during rest. Have at least one rest day per week.',
            'category': 'Recovery'
        },
        {
            'title_fa': 'تغذیه بعد از ورزش',
            'title_en': 'Post-Workout Nutrition',
            'content_fa': 'خوردن غذاهای غنی از پروتئین و کربوهیدرات در ۳۰ دقیقه تا ۲ ساعت بعد از ورزش به ریکاوری عضلات و بازسازی ذخایر انرژی کمک می‌کند.',
            'content_en': 'Eating protein and carbohydrate-rich foods within 30 minutes to 2 hours after exercise helps muscle recovery and energy replenishment.',
            'category': 'Nutrition'
        }
    ]
    
    for tip_data in tips:
        tip = Tip(**tip_data)
        db.session.add(tip)
    
    print(f'Added {len(tips)} tips')

def seed_injuries():
    """Add sample injury information in both Farsi and English"""
    injuries = [
        {
            'title_fa': 'کشیدگی عضله',
            'title_en': 'Muscle Strain',
            'description_fa': 'کشیدگی عضله زمانی رخ می‌دهد که عضله بیش از حد کشیده یا پاره شود. این آسیب معمولاً در عضلات بزرگ مانند همسترینگ، چهارسر و کمر رخ می‌دهد.',
            'description_en': 'A muscle strain occurs when a muscle is overstretched or torn. This injury commonly occurs in large muscles such as hamstrings, quadriceps, and back.',
            'prevention_fa': 'گرم کردن مناسب قبل از ورزش، انجام حرکات کششی منظم، و افزایش تدریجی شدت تمرینات می‌تواند از کشیدگی عضله جلوگیری کند.',
            'prevention_en': 'Proper warm-up before exercise, regular stretching, and gradual increase in training intensity can prevent muscle strains.',
            'treatment_fa': 'استراحت، استفاده از یخ، فشرده‌سازی و بالا بردن ناحیه آسیب دیده (RICE). در صورت درد شدید یا تداوم علائم، به پزشک مراجعه کنید.',
            'treatment_en': 'Rest, ice, compression, and elevation (RICE). Consult a doctor if pain is severe or symptoms persist.'
        },
        {
            'title_fa': 'درد زانو',
            'title_en': 'Knee Pain',
            'description_fa': 'درد زانو یکی از شایع‌ترین مشکلات در بین ورزشکاران است و می‌تواند ناشی از استفاده بیش از حد، آسیب مستقیم یا مشکلات ساختاری باشد.',
            'description_en': 'Knee pain is one of the most common issues among athletes and can result from overuse, direct injury, or structural problems.',
            'prevention_fa': 'تقویت عضلات اطراف زانو، استفاده از کفش مناسب، و اجتناب از افزایش ناگهانی شدت تمرینات.',
            'prevention_en': 'Strengthen muscles around the knee, wear proper footwear, and avoid sudden increases in training intensity.',
            'treatment_fa': 'استراحت، استفاده از یخ، و تمرینات تقویتی. در صورت تداوم درد، به متخصص ارتوپد مراجعه کنید.',
            'treatment_en': 'Rest, ice application, and strengthening exercises. Consult an orthopedic specialist if pain persists.'
        },
        {
            'title_fa': 'درد شانه',
            'title_en': 'Shoulder Pain',
            'description_fa': 'درد شانه می‌تواند ناشی از التهاب تاندون، آسیب روتاتور کاف، یا استفاده بیش از حد باشد.',
            'description_en': 'Shoulder pain can result from tendon inflammation, rotator cuff injury, or overuse.',
            'prevention_fa': 'تمرینات تقویتی برای عضلات شانه، گرم کردن مناسب، و اجتناب از حرکات تکراری بیش از حد.',
            'prevention_en': 'Strengthening exercises for shoulder muscles, proper warm-up, and avoiding excessive repetitive movements.',
            'treatment_fa': 'استراحت، استفاده از یخ، و تمرینات دامنه حرکتی. در صورت نیاز به فیزیوتراپی مراجعه کنید.',
            'treatment_en': 'Rest, ice application, and range of motion exercises. Consider physical therapy if needed.'
        }
    ]
    
    for injury_data in injuries:
        injury = Injury(**injury_data)
        db.session.add(injury)
    
    print(f'Added {len(injuries)} injury entries')

if __name__ == '__main__':
    with app.app_context():
        # Clear existing data (optional - comment out if you want to keep existing data)
        # Tip.query.delete()
        # Injury.query.delete()
        
        # Check if data already exists
        if Tip.query.count() == 0:
            seed_tips()
        else:
            print('Tips already exist, skipping...')
        
        if Injury.query.count() == 0:
            seed_injuries()
        else:
            print('Injuries already exist, skipping...')
        
        db.session.commit()
        print('Data seeding completed!')

