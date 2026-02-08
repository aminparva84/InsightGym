/**
 * Training level and corrective-movements content (matches Excel export).
 * Used as fallback when API returns empty and for landing page "website info".
 */
export const TRAINING_LEVELS_FALLBACK = {
  beginner: {
    label_en: 'Beginner',
    label_fa: 'مبتدی',
    description_en: 'Beginner user: 0–6 months training history; low control over movement form; little familiarity with breathing and mind–muscle coordination; fast recovery but injury-sensitive. Main goals: learn correct form, activate muscles, increase body awareness, build training habit, prevent injury. Design: choose simple, safe, controllable exercises; focus on form, breathing, correct range of motion. General program: 2–4 sessions/week; simple compound movements, machine or bodyweight; 2–3 sets, 10–15 reps; 60–90 sec rest; no advanced techniques (superset, drop set). Breathing & mindfulness: breathing cue per movement; inhale on negative phase, exhale on positive; short pause for body awareness.',
    description_fa: 'تعریف کاربر مبتدی: سابقه تمرین ۰ تا ۶ ماه؛ کنترل پایین روی فرم حرکات؛ آشنایی کم با تنفس و هماهنگی ذهن-عضله؛ ریکاوری سریع اما حساس به آسیب. اهداف اصلی: یادگیری فرم صحیح حرکات، فعال‌سازی عضلات، افزایش آگاهی بدنی، ایجاد عادت تمرینی، جلوگیری از آسیب. طراحی تمرین: تمرین‌ها را ساده، ایمن و قابل کنترل انتخاب کند؛ تمرکز روی فرم حرکت، تنفس، دامنه حرکتی صحیح. ویژگی کلی: ۲ تا ۴ جلسه در هفته؛ حرکات چندمفصلی ساده، دستگاه یا وزن بدن؛ ۲–۳ ست، ۱۰–۱۵ تکرار؛ استراحت ۶۰–۹۰ ثانیه؛ بدون تکنیک‌های پیشرفته (سوپرست، دراپ‌ست و…). تنفس و مایندفولنس: راهنمای تنفس در هر حرکت؛ تاکید روی دم در فاز منفی و بازدم در فاز مثبت؛ مکث کوتاه برای آگاهی بدن.',
    goals: [
      { en: 'Learn correct movement form', fa: 'یادگیری فرم صحیح حرکات' },
      { en: 'Activate muscles', fa: 'فعال‌سازی عضلات' },
      { en: 'Increase body awareness', fa: 'افزایش آگاهی بدنی' },
      { en: 'Build training habit', fa: 'ایجاد عادت تمرینی' },
      { en: 'Prevent injury', fa: 'جلوگیری از آسیب' },
    ],
  },
  intermediate: {
    label_en: 'Intermediate',
    label_fa: 'متوسط',
    description_en: 'Intermediate user: 6 months–2 years training; relative familiarity with form; ability to maintain focus; tolerance for volume; ready for variety. Main goals: increase relative strength, muscle shaping, improve nerve–muscle coordination, introduce training variety. Design: increase intensity, add movement variety, take body out of adaptation. General program: 3–5 sessions/week; bodybuilding + functional; 3–4 sets, 8–12 reps; 45–75 sec rest; limited use of superset, compound sets. Breathing & focus: mind–muscle connection, movement rhythm control, breathing in sync with effort.',
    description_fa: 'تعریف کاربر متوسط: سابقه تمرین ۶ ماه تا ۲ سال؛ آشنایی نسبی با فرم؛ توانایی حفظ تمرکز در تمرین؛ توان تحمل حجم تمرین؛ آمادگی برای تنوع. اهداف اصلی: افزایش قدرت نسبی، فرم‌دهی عضلانی، افزایش هماهنگی عصب-عضله، شروع تنوع تمرینی. منطق طراحی: شدت تمرین را افزایش دهد؛ تنوع حرکتی ایجاد کند؛ بدن را از حالت سازگاری خارج کند. ویژگی‌های کلی: ۳ تا ۵ جلسه در هفته؛ ترکیب بدنسازی + فانکشنال؛ ۳–۴ ست، ۸–۱۲ تکرار؛ استراحت ۴۵–۷۵ ثانیه؛ استفاده محدود از سوپرست، تمرینات ترکیبی. تنفس و تمرکز: تمرکز روی اتصال ذهن-عضله؛ کنترل ریتم حرکت؛ هماهنگی تنفس با فشار تمرین.',
    goals: [
      { en: 'Increase relative strength', fa: 'افزایش قدرت نسبی' },
      { en: 'Muscle shaping', fa: 'فرم‌دهی عضلانی' },
      { en: 'Improve nerve–muscle coordination', fa: 'افزایش هماهنگی عصب-عضله' },
      { en: 'Introduce training variety', fa: 'شروع تنوع تمرینی' },
    ],
  },
  advanced: {
    label_en: 'Advanced',
    label_fa: 'پیشرفته',
    description_en: 'Advanced user: over 2 years training; high mastery of form; high physical and mental readiness; high volume tolerance; breathing control; strong mind–muscle connection. Main goals: targeted hypertrophy or strength, advanced fat loss, neuromuscular challenge, performance improvement. Design: fully personalize training; use advanced techniques; intelligently manage intensity, volume, recovery. Program: 4–6 sessions/week; professional mix of bodybuilding, functional, neural training; variable sets/reps (6–15); rest 30–60 sec or variable; techniques: superset, drop set, time under tension, metabolic training. Breathing & mindfulness: breathing control under load; deep focus on body energy; mindful training.',
    description_fa: 'تعریف کاربر پیشرفته: سابقه تمرین بیش از ۲ سال؛ تسلط بالا روی فرم؛ آمادگی بدنی و ذهنی بالا؛ آمادگی حجم بالا؛ کنترل تنفس؛ اتصال ذهن و عضله قوی. اهداف اصلی: افزایش حجم یا قدرت هدفمند؛ چربی‌سوزی پیشرفته؛ چالش عصبی-عضلانی؛ بهبود عملکرد. منطق طراحی: تمرین‌ها را کاملاً شخصی‌سازی کند؛ از تکنیک‌های پیشرفته استفاده کند؛ شدت، حجم و ریکاوری را هوشمندانه تنظیم کند. ویژگی‌های برنامه: ۴ تا ۶ جلسه در هفته؛ ترکیب حرفه‌ای بدنسازی، فانکشنال، تمرینات عصبی؛ ست و تکرار متغیر (۶–۱۵)؛ استراحت ۳۰–۶۰ ثانیه یا متغیر؛ تکنیک‌ها: سوپرست، دراپ‌ست، تایم آندر تنشن، تمرینات متابولیک. تنفس و مایندفولنس: کنترل تنفس تحت فشار؛ تمرکز عمیق روی انرژی بدن؛ تمرین آگاهانه و حضور ذهن.',
    goals: [
      { en: 'Targeted hypertrophy or strength', fa: 'افزایش حجم یا قدرت هدفمند' },
      { en: 'Advanced fat loss', fa: 'چربی‌سوزی پیشرفته' },
      { en: 'Neuromuscular challenge', fa: 'چالش عصبی-عضلانی' },
      { en: 'Performance improvement', fa: 'بهبود عملکرد' },
    ],
  },
};

const INJURY_KEYS_ORDER = ['knee', 'shoulder', 'lower_back', 'neck', 'wrist', 'ankle'];

export const INJURIES_FALLBACK = {
  knee: {
    label_en: 'Knee',
    label_fa: 'زانو',
    purposes_en: 'Main goals during knee injury: 1. Reduce direct pressure on the knee joint. 2. Prevent further injury or worsening pain. 3. Strengthen supporting muscles (quadriceps, hamstrings, glutes). 4. Maintain safe range of motion. 5. Maintain body control and correct movement form.',
    purposes_fa: 'اهداف اصلی در هنگام آسیب زانو: 1. کاهش فشار مستقیم روی مفصل زانو. 2. جلوگیری از آسیب بیشتر یا تشدید درد. 3. تقویت عضلات حمایت‌کننده (کوادری‌سپس، همسترینگ، گلوت‌ها). 4. حفظ دامنه حرکتی امن. 5. حفظ کنترل بدن و فرم درست حرکت.',
    allowed_movements: [
      { en: 'Glute Bridge → strengthen glutes and hamstrings without knee load', fa: 'Glute Bridge → تقویت باسن و همسترینگ بدون فشار روی زانو' },
      { en: 'Hip Thrust → same as Glute Bridge, load on glutes', fa: 'Hip Thrust → همانند Glute Bridge، بار روی باسن' },
      { en: 'Hamstring Curl (machine or ball) → strengthen posterior thigh without front knee pressure', fa: 'Hamstring Curl (دستگاه یا توپ) → تقویت پشت ران بدون فشار جلو زانو' },
      { en: 'Step-back Lunge or short Reverse Lunge → limited range', fa: 'Step-back Lunge یا Reverse Lunge کوتاه → لنج به عقب با دامنه محدود' },
      { en: 'Short Wall Sit → stability without heavy load', fa: 'Wall Sit کوتاه → حفظ ثبات بدون فشار زیاد' },
      { en: 'Light Leg Press with limited ROM → if machine is adjustable', fa: 'Leg Press سبک با دامنه محدود → اگر دستگاه قابل تنظیم باشد' },
      { en: 'Isometric quad exercises → e.g. Quad Set', fa: 'تمرینات ایزومتریک برای کوادری‌سپس → مثل Quad Set' },
    ],
    forbidden_movements: [
      { en: 'Deep or fast Squat (Deep Squat)', fa: 'Squat عمیق یا سریع (Deep Squat)' },
      { en: 'Jump Squat / Plyometric / severe jumping', fa: 'Jump Squat / Plyometric / حرکات پرشی شدید' },
      { en: 'Long forward Lunge', fa: 'Lunge جلو بلند' },
      { en: 'Heavy Leg Extension', fa: 'Leg Extension سنگین' },
      { en: 'Rapid or sudden direction change', fa: 'تغییر جهت سریع و ناگهانی' },
      { en: 'Explosive and high-speed movements', fa: 'حرکات انفجاری و سرعت بالا' },
    ],
    important_notes_en: '1. If pain is moderate or severe → light leg work or substitute. 2. If user has multiple injuries → knee limitation takes priority. 3. Focus on movement control and breathing (calm inhale, exhale on effort phase). 4. Recovery time between sets should be slightly longer than usual. 5. In workout text state: "If pain worsens, stop the exercise and choose a substitute movement."',
    important_notes_fa: '1. اگر درد متوسط یا شدید باشد → حرکات پا سبک یا جایگزین شوند. 2. اگر کاربر چند آسیب همزمان دارد → محدودیت زانو اولویت می‌گیرد. 3. تمرکز روی کنترل حرکت و تنفس (دم آرام، بازدم در فاز فشار). 4. زمان ریکاوری بین ست‌ها باید کمی بیشتر از حالت معمول باشد. 5. در متن تمرینی ذکر شود: «اگر درد تشدید شد، تمرین متوقف شود و حرکت جایگزین انتخاب گردد.»',
  },
  shoulder: {
    label_en: 'Shoulder',
    label_fa: 'شانه',
    purposes_en: 'Main goals in shoulder injury: 1. Maintain scapular stability. 2. Avoid pressure on rotator cuff. 3. Strengthen shoulder stabilizers.',
    purposes_fa: 'اهداف اصلی در آسیب شانه: 1. حفظ ثبات کتف. 2. جلوگیری از فشار روی روتاتور کاف. 3. تقویت عضلات نگهدارنده شانه.',
    allowed_movements: [
      { en: 'Seated Row', fa: 'Seated Row' },
      { en: 'Lat Pulldown (front)', fa: 'Lat Pulldown جلو' },
      { en: 'Face Pull', fa: 'Face Pull' },
      { en: 'Light Lateral Raise', fa: 'Lateral Raise سبک' },
      { en: 'External Rotation', fa: 'External Rotation' },
      { en: 'Scapular control exercises', fa: 'تمرینات کنترل کتف' },
    ],
    forbidden_movements: [
      { en: 'Heavy Overhead Press', fa: 'Overhead Press سنگین' },
      { en: 'Upright Row', fa: 'Upright Row' },
      { en: 'Dips', fa: 'Dips' },
      { en: 'Behind-neck Pull-up', fa: 'Pull-up پشت گردن' },
      { en: 'Heavy Bench Press', fa: 'Bench Press سنگین' },
      { en: 'Explosive overhead movements', fa: 'حرکات انفجاری بالای سر' },
    ],
    important_notes_en: 'Limited range of motion. Focus on scapular stability. Exhale on effort, inhale on return.',
    important_notes_fa: 'دامنه حرکتی محدود. تمرکز روی ثبات کتف. بازدم هنگام فشار، دم هنگام برگشت.',
  },
  lower_back: {
    label_en: 'Lower back',
    label_fa: 'کمر',
    purposes_en: 'Main goals during lower back injury: 1. Reduce axial load. 2. Increase core stability. 3. Prevent worsening pain.',
    purposes_fa: 'اهداف اصلی در هنگام آسیب کمر: 1. کاهش فشار محوری. 2. افزایش ثبات مرکزی (Core Stability). 3. جلوگیری از تشدید درد.',
    allowed_movements: [
      { en: 'Bird Dog', fa: 'Bird Dog' },
      { en: 'Dead Bug', fa: 'Dead Bug' },
      { en: 'Glute Bridge', fa: 'Glute Bridge' },
      { en: 'Light Hip Hinge', fa: 'Hip Hinge سبک' },
      { en: 'Modified Plank', fa: 'Plank اصلاح‌شده' },
      { en: 'Light Cable Pull-through', fa: 'Cable Pull-through سبک' },
    ],
    forbidden_movements: [
      { en: 'Heavy Deadlift', fa: 'Deadlift سنگین' },
      { en: 'Good Morning', fa: 'Good Morning' },
      { en: 'Back Squat', fa: 'Back Squat' },
      { en: 'Russian Twist', fa: 'Russian Twist' },
      { en: 'Hyperextension', fa: 'Hyperextension' },
      { en: 'Sudden rotational movements', fa: 'حرکات چرخشی ناگهانی' },
    ],
    important_notes_en: 'Controlled breathing. Slow movement, precise form. Focus on core muscles.',
    important_notes_fa: 'تنفس کنترل‌شده. حرکت آرام، فرم دقیق. تمرکز روی عضلات مرکزی.',
  },
  neck: {
    label_en: 'Neck',
    label_fa: 'گردن',
    purposes_en: 'Main goals: 1. Remove tension. 2. Maintain neutral spine. 3. Avoid direct pressure.',
    purposes_fa: 'اهداف اصلی: 1. حذف تنش. 2. حفظ حالت خنثی ستون فقرات. 3. جلوگیری از فشار مستقیم.',
    allowed_movements: [
      { en: 'Chin Tuck', fa: 'Chin Tuck' },
      { en: 'Isometric neck exercises', fa: 'تمرینات ایزومتریک گردن' },
      { en: 'Upper-body work with neutral neck', fa: 'تمرینات بالاتنه با گردن خنثی' },
      { en: 'Light breathing exercises', fa: 'تمرینات سبک تنفسی' },
    ],
    forbidden_movements: [
      { en: 'Heavy Shrug', fa: 'Shrug سنگین' },
      { en: 'Explosive movements', fa: 'حرکات انفجاری' },
      { en: 'Direct pressure on head', fa: 'فشار مستقیم روی سر' },
      { en: 'Rapid neck rotation', fa: 'چرخش سریع گردن' },
    ],
    important_notes_en: 'Full neck control. Breathing in sync with movement. If pain → substitute movement.',
    important_notes_fa: 'کنترل کامل گردن. هماهنگی تنفس با حرکت. اگر درد باشد → جایگزین حرکات.',
  },
  wrist: {
    label_en: 'Wrist',
    label_fa: 'مچ دست',
    purposes_en: 'Main goals: 1. Reduce wrist flexion/extension load. 2. Maintain safe movement. 3. Strengthen forearm and prevent pain.',
    purposes_fa: 'اهداف اصلی: 1. کاهش فشار خم و باز شدن مچ. 2. حفظ حرکت امن. 3. تقویت ساعد و پیشگیری از درد.',
    allowed_movements: [
      { en: 'Dumbbell Neutral Grip Press', fa: 'Dumbbell Neutral Grip Press' },
      { en: 'Cable Push / Pull', fa: 'Cable Push / Pull' },
      { en: 'Resistance Band Exercises', fa: 'Resistance Band Exercises' },
      { en: 'Light forearm exercises', fa: 'تمرینات ساعد سبک' },
      { en: 'Exercises without weight on hands', fa: 'تمرینات بدون تحمل وزن روی دست' },
    ],
    forbidden_movements: [
      { en: 'Classic Push-up', fa: 'Push-up کلاسیک' },
      { en: 'Plank on hands', fa: 'Plank روی دست' },
      { en: 'Barbell Press', fa: 'Barbell Press' },
      { en: 'Heavy Hanging', fa: 'Hanging سنگین' },
      { en: 'Burpee', fa: 'Burpee' },
    ],
    important_notes_en: 'Limited range of motion. Use neutral grip. Control breathing under load.',
    important_notes_fa: 'دامنه حرکت محدود. استفاده از گریپ خنثی. کنترل تنفس در فشار.',
  },
  ankle: {
    label_en: 'Ankle',
    label_fa: 'مچ پا',
    purposes_en: 'Main goals: 1. Joint stability and control. 2. Prevent sprain or direct pressure.',
    purposes_fa: 'اهداف اصلی: 1. ثبات و کنترل مفصل. 2. جلوگیری از پیچ خوردگی یا فشار مستقیم.',
    allowed_movements: [
      { en: 'Seated Calf Raise', fa: 'Seated Calf Raise' },
      { en: 'Glute-focused movements', fa: 'Glute-focused movements' },
      { en: 'Short Step-up', fa: 'Step-up کوتاه' },
      { en: 'Simple balance exercises', fa: 'تمرینات تعادلی ساده' },
      { en: 'Controlled stretching', fa: 'تمرینات کششی کنترل‌شده' },
    ],
    forbidden_movements: [
      { en: 'Jumping / Plyometric', fa: 'Jumping / Plyometric' },
      { en: 'High-intensity Running', fa: 'Running با شدت' },
      { en: 'Box Jump', fa: 'Box Jump' },
      { en: 'Rapid direction change', fa: 'تغییر جهت سریع' },
      { en: 'Explosive single-leg exercises', fa: 'تمرینات تک‌پایی انفجاری' },
    ],
    important_notes_en: 'Control range of motion. Focus on form and balance. Use calm inhale and exhale.',
    important_notes_fa: 'کنترل دامنه حرکتی. تمرکز روی فرم و تعادل. استفاده از دم و بازدم آرام.',
  },
};

export const COMMON_INJURY_NOTE_FALLBACK = {
  en: 'Common note for all injuries: Always correct form + controlled breathing. If pain is severe → stop the movement and substitute. Safety first, then performance. Remove direct load on the injured joint. Substitute the movement, not remove the whole workout. Focus on: safe range of motion, control, breathing.',
  fa: 'نکته مشترک برای تمام آسیب‌ها: همیشه فرم صحیح + تنفس کنترل‌شده. اگر درد شدید بود → توقف حرکت و جایگزینی. اول ایمنی، بعد عملکرد. حذف فشار مستقیم روی مفصل آسیب‌دیده. جایگزینی حرکت، نه حذف کل تمرین. تمرکز روی: دامنه امن، کنترل، تنفس.',
};

export const INJURY_KEYS_ORDER_LIST = INJURY_KEYS_ORDER;
