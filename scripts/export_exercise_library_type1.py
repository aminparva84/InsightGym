"""
Parse Type 1 (machine) exercise list, export JSON and PDF.
Run from project root: python scripts/export_exercise_library_type1.py
Outputs:
  - frontend/src/data/exerciseLibraryType1.json
  - docs/Exercise_Library_Type1.pdf
"""
import os
import json
import re
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
OUTPUT_JSON = os.path.join(PROJECT_ROOT, "frontend", "src", "data", "exerciseLibraryType1.json")
OUTPUT_PDF = os.path.join(PROJECT_ROOT, "docs", "Exercise_Library_Type1.pdf")

RAW_TEXT = r"""
🟥 ۱) عضلات سینه (Chest) – 25 حرکت
	1.	Chest Press Machine– 
پرس سینه دستگاه -مبتدی تا حرفه‌ای، کمر صاف، دم پایین، بازدم فشار، هر دو
	2.	Incline Chest Press Machine
پرس بالاسینه -مبتدی تا حرفه‌ای، زاویه نیمکت ۴۵درجه، دم پایین، بازدم بالا، هر دو
	3.	Decline Chest Press Machine 
پرس زیرسینه -مبتدی تا حرفه‌ای، مراقب گردن، 
شیب منفی،دم پایین، بازدم بالا، هر دو

	4.	Pec Deck (Butterfly)– 
قفسه سینه دستگاه -متوسط، بازو کمی خم، 
تمرکز روی سینه، دم بازدم کنترل‌شده، هر دو

	5.	Cable Crossover (High to low)– زیر سینه سیم کش -متوسط، کشش کامل، دم پایین، بازدم بالا، هر دو
	6.	Cable Crossover (Mid) – 
قفسه سینه سیم کش -وسط، متوسط، حرکت صاف، دم پایین، بازدم بالا، هر دو
	7.	Cable Crossover (Low to high)– بالا سینه سیم کش -متوسط، زاویه مناسب، دم پایین، بازدم بالا، هر دو
	8.	Standing Cable Chest Press – 
پرس سینه سیم کش ایستاده -متوسط، پاها کمی جلو،آرنج خم ،دم پایین، بازدم بالا، هر دو
	9.	Iso-Lateral Chest Press machin

– پرس سینه دستگاه وزنه آزاد، متوسط، کنترل یک دست، دم پایین، بازدم بالا،هردو
.
10.Cable Incline Fly 
– بالاسینه قفسه سیم کش،زاویه نیمکت ۴۵ درجه، متوسط، آرنج کمی خم، دم پایین، بازدم بالا، هر دو

11.	Cable Flat Fly 
– قفسه سینه سیم کش ،متوسط،میز صاف ،وسط، آرنج خم، دم پایین، بازدم بالا، هر دو

	12.	Cable Decline Fly – 
زیرسینه سیم کش ، متوسط، تمرکز روی زیرسینه، شیب منفی ،دم پایین، بازدم بالا، هر دو
	
	14.	Cable Single Arm Fly 
– قفسه سینه سیم کش تک دست، متوسط، یک دست، دم پایین، بازدم بالا، هر دو
	
	15.	Pec Deck Iso-Lateral – 
قفسه سینه دستگاه تک دست، متوسط تا حرفه‌ای، تمرکز روی سینه، دم پایین، بازدم بالا، هر دو
	
	16.	Cable Press + Fly Superset – 
پرس سینه سیم کش +فلای سیم کش ،حرفه‌ای، ترکیبی، دم پایین، بازدم بالا، هر دو
17.chest press dumbbell
پرس سینه دمبل ،مبتدی تا حرفه‌ای، کمر صاف، میز صاف،دم پایین،بازدم فشار، هر دو

18.incline chest press dumbbell
پرس بالاسینه دمبل، مبتدی تا حرفه‌ای، زاویه نیمکت ۳۰–۴۵ درجه، دم پایین، بازدم بالا، هر دو
	
19.	Decline Chest Press dumbbell
پرس زیر سینه دمبل ،مبتدی تا حرفه‌ای، میزشیب منفی ،مراقب گردن، 
دم پایین، بازدم بالا، هر دو

17.chest press barbell
پرس سینه هالتر ،مبتدی تا حرفه‌ای، کمر صاف، دم پایین،بازدم فشار، هر دو

18.incline chest press barbell
سینه بالا، مبتدی تا حرفه‌ای، زاویه نیمکت ۳۰–۴۵ درجه، دم پایین، بازدم بالا، هر دو
	
19.	Decline Chest Press barbell
سینه پایین، مبتدی تا حرفه‌ای، مراقب گردن، 
دم پایین، بازدم بالا، هر دو

🟦 ۲) عضلات پشت (Back) – 25 حرکت
	26.	Lat Pulldown Front – پشت، مبتدی تا حرفه‌ای، دم پایین، بازدم کشش، هر دو
	27.	Close-Grip Lat Pulldown – پشت وسط ، متوسط، دم پایین، بازدم بالا، هر دو
	28.	Reverse-Grip Lat Pulldown – پشت پایین، متوسط، آرنج نزدیک بدن، دم پایین، بازدم بالا، هر دو
	29.	Hammer Strength Row – میان‌پشت، متوسط تا حرفه‌ای، کنترل کامل، دم پایین، بازدم بالا، هر دو
	30.	Seated Row Machine – پشت، مبتدی تا حرفه‌ای، کمر صاف، دم پایین، بازدم بالا، هر دو
	31.	T-Bar Row Machine – میان‌پشت، متوسط تا حرفه‌ای، دم پایین، بازدم بالا، هر دو
	32.	Iso-Lateral High Row – پشت بالایی، متوسط تا حرفه‌ای، دم پایین، بازدم بالا، هر دو
	33.	Iso-Lateral Low Row – پشت پایین، متوسط تا حرفه‌ای، دم پایین، بازدم بالا، هر دو
	34.	Cable Row Wide Grip – پشت، متوسط، آرنج به طرفین، دم پایین، بازدم بالا، هر دو
	35.	Cable Row Close Grip – پشت، متوسط، آرنج نزدیک بدن، دم پایین، بازدم بالا، هر دو
	36.	Pull-over Machine – پشت و سینه، متوسط، دم پایین، بازدم بالا، هر دو
	37.	Back Extension Machine – پایین پشت، مبتدی تا متوسط، حرکت کنترل‌شده، دم پایین، بازدم بالا، هر دو
	38.	Lat Pulldown Behind Neck – پشت بالا، حرفه‌ای، توجه: آسیب‌زا، نیاز به فرم حرفه‌ای، دم پایین، بازدم بالا، هر دو
	39.	Iso-Lateral Row Single Arm – پشت، متوسط تا حرفه‌ای، کنترل یک دست، دم پایین، بازدم بالا، هر دو
	40.	Row Machine One Arm – میان‌پشت، متوسط، دم پایین، بازدم بالا، هر دو
	41.	Chest Supported Row – میان‌پشت، متوسط، دم پایین، بازدم بالا، هر دو
	42.	Standing Cable Row – پشت، متوسط، پاها کمی جلو، دم پایین، بازدم بالا، هر دو
	43.	T-Bar Row Drop Set – میان‌پشت، حرفه‌ای، دم پایین، بازدم بالا، هر دو
	44.	Seated Cable Pull – پشت، متوسط، آرنج نزدیک بدن، دم پایین، بازدم بالا، هر دو
	45.	Cable Shrug – فوقانی پشت، مبتدی، دم پایین، بازدم بالا، هر دو
	46.	Machine Shrug – فوقانی پشت، متوسط، دم پایین، بازدم بالا، هر دو
	47.	Hammer Strength Pullover – پشت، حرفه‌ای، دم پایین، بازدم بالا، هر دو
	48.	Assisted Pull-Up Machine – پشت، مبتدی، دم پایین، بازدم بالا، هر دو
	49.	Cable Lat Row Superset – پشت، حرفه‌ای، ترکیبی، دم پایین، بازدم بالا، هر دو
	50.	Iso-Lateral High Row Drop Set – پشت، حرفه‌ای، دم پایین، بازدم بالا، هر دو

🟩 ۳) شانه (Shoulders) – ۲۰ حرکت
	51.	Shoulder Press Machine – شانه جلو و میانی، مبتدی تا حرفه‌ای، کمر صاف، دم پایین، بازدم بالا، هر دو
	52.	Iso-Lateral Shoulder Press – شانه، متوسط، کنترل یک دست، دم پایین، بازدم بالا، هر دو
	53.	Lateral Raise Machine – دلتوئید جانبی، متوسط، آرنج کمی خم، دم پایین، بازدم بالا، هر دو
	54.	Rear Delt Machine (Reverse Fly) – شانه پشت، متوسط، آرنج خم، دم پایین، بازدم بالا، هر دو
	55.	Cable Lateral Raise – شانه جانبی، متوسط، حرکت کنترل‌شده، دم پایین، بازدم بالا، هر دو
	56.	Cable Front Raise – شانه جلو، متوسط، صاف نگه داشتن کمر، دم پایین، بازدم بالا، هر دو
	57.	Cable Rear Delt Extension – شانه پشت، متوسط، دم پایین، بازدم بالا، هر دو
	58.	Plate-Loaded Shoulder Press – شانه، متوسط تا حرفه‌ای، دم پایین، بازدم فشار، هر دو
	59.	Dumbbell Shoulder Press Machine – شانه، متوسط، کنترل وزنه، دم پایین، بازدم بالا، هر دو
	60.	Shoulder Press Drop Set – شانه، حرفه‌ای، افزایش شدت، دم پایین، بازدم بالا، هر دو
	61.	Lateral Raise Drop Set – شانه جانبی، حرفه‌ای، دم پایین، بازدم بالا، هر دو
	62.	Rear Delt Cable Fly – شانه پشت، متوسط، دم پایین، بازدم بالا، هر دو
	63.	Shoulder Press Iso-Lateral Single Arm – شانه، متوسط، کنترل یک دست، دم پایین، بازدم بالا، هر دو
	64.	Hammer Strength Shoulder Press – شانه، متوسط تا حرفه‌ای، دم پایین، بازدم بالا، هر دو
	65.	Seated Rear Delt Machine – شانه پشت، متوسط، دم پایین، بازدم بالا، هر دو
	66.	Incline Lateral Raise Machine – شانه جانبی، متوسط، دم پایین، بازدم بالا، هر دو
	67.	Front Raise Machine – شانه جلو، متوسط، دم پایین، بازدم بالا، هر دو
	68.	Iso-Lateral Lateral Raise – شانه جانبی، متوسط، دم پایین، بازدم بالا، هر دو
	69.	Cable Shoulder Press – شانه، متوسط، پاها کمی جلو، دم پایین، بازدم بالا، هر دو
	70.	Shoulder Shrug Machine – شانه فوقانی، مبتدی، دم پایین، بازدم بالا، هر دو

🟧 ۴) پایین‌تنه / پاها (Legs) – ۳۰ حرکت
	71.	Leg Press 45° – چهارسر، باسن، مبتدی تا حرفه‌ای، زانو قفل نشود، دم پایین، بازدم بالا، هر دو
	72.	Horizontal Leg Press Machine – چهارسر، باسن، متوسط، دم پایین، بازدم بالا، هر دو
	73.	Hack Squat Machine – چهارسر، باسن، متوسط، کمر صاف، دم پایین، بازدم بالا، هر دو
	74.	Smith Machine Squat – چهارسر، باسن، متوسط تا حرفه‌ای، پاها درست، دم پایین، بازدم بالا، هر دو
	75.	Leg Extension Machine – چهارسر، مبتدی، زانو کنترل‌شده، دم پایین، بازدم بالا، هر دو
	76.	Leg Curl Machine Lying – همسترینگ، متوسط، دم پایین، بازدم بالا، هر دو
	77.	Leg Curl Machine Seated – همسترینگ، متوسط، دم پایین، بازدم بالا، هر دو
	78.	Hip Abductor Machine – اداکتور جانبی، مبتدی، دم پایین، بازدم بالا، هر دو
	79.	Hip Adductor Machine – اداکتور داخلی، مبتدی، دم پایین، بازدم بالا، هر دو
	80.	Glute Kickback Machine – باسن، متوسط، دم پایین، بازدم بالا، هر دو
	81.	Glute Bridge Machine – باسن، متوسط، توقف بالا ۲ ثانیه، دم پایین، بازدم بالا، هر دو
	82.	Standing Calf Raise Machine – ساق، مبتدی، دم پایین، بازدم بالا، هر دو
	83.	Seated Calf Raise Machine – ساق، متوسط، دم پایین، بازدم بالا، هر دو
	84.	Belt Squat Machine – چهارسر، باسن، متوسط تا حرفه‌ای، دم پایین، بازدم بالا، هر دو
	85.	Leg Press Single Leg – چهارسر، متوسط، دم پایین، بازدم بالا، هر دو
	86.	Hack Squat Single Leg – چهارسر، متوسط، دم پایین، بازدم بالا، هر دو
	87.	Leg Extension Drop Set – چهارسر، حرفه‌ای، دم پایین، بازدم بالا، هر دو
	88.	Leg Curl Drop Set – همسترینگ، حرفه‌ای، دم پایین، بازدم بالا، هر دو
	89.	Glute Drive Machine – باسن، متوسط، دم پایین، بازدم بالا، هر دو
	90.	Standing Hip Extension Cable – باسن، متوسط، دم پایین، بازدم بالا، هر دو
	91.	Cable Glute Kickback – باسن، متوسط، دم پایین، بازدم بالا، هر دو
	92.	Iso-Lateral Leg Press – چهارسر، باسن، متوسط، دم پایین، بازدم بالا، هر دو
	93.	Pendulum Squat Machine – چهارسر، باسن، متوسط تا حرفه‌ای، دم پایین، بازدم بالا، هر دو
	94.	Smith Machine Split Squat – چهارسر، باسن، متوسط، دم پایین، بازدم بالا، هر دو
	95.	Leg Press Calf Raise Superset – چهارسر + ساق، متوسط، دم پایین، بازدم بالا، هر دو
	96.	Iso-Lateral Hack Squat – چهارسر، باسن، متوسط، دم پایین، بازدم بالا، هر دو
	97.	Cable Step-Up Machine – چهارسر، باسن، متوسط، دم پایین، بازدم بالا، هر دو
	98.	Machine Lunges – چهارسر، باسن، متوسط، دم پایین، بازدم بالا، هر دو
	99.	Leg Press High Step – چهارسر، باسن، متوسط، دم پایین، بازدم بالا، هر دو
	100.	Seated Leg Curl Single Leg – همسترینگ، متوسط، دم پایین، بازدم بالا، هر دو
	101.	Lying Leg Curl Single Leg – همسترینگ، متوسط، دم پایین، بازدم بالا، هر دو
	102.	Glute Bridge Iso-Lateral – باسن، متوسط، دم پایین، بازدم بالا، هر دو
	103.	Hip Thrust Iso-Lateral Machine – باسن، حرفه‌ای، دم پایین، بازدم بالا، هر دو
	104.	Inner Thigh Machine Drop Set – اداکتور داخلی، حرفه‌ای، دم پایین، بازدم بالا، هر دو
	105.	Outer Thigh Machine Drop Set – اداکتور جانبی، حرفه‌ای، دم پایین، بازدم بالا، هر دو
	106.	Standing Calf Raise Drop Set – ساق، حرفه‌ای، دم پایین، بازدم بالا، هر دو
	107.	Seated Calf Raise Drop Set – ساق، حرفه‌ای، دم پایین، بازدم بالا، هر دو
	108.	Belt Squat Drop Set – چهارسر، باسن، حرفه‌ای، دم پایین، بازدم بالا، هر دو
	109.	Cable Pull-Through – همسترینگ و باسن، متوسط، دم پایین، بازدم بالا، هر دو
	110.	Glute Kickback Drop Set – باسن، حرفه‌ای، دم پایین، بازدم بالا، هر دو

🟪 ۵) جلو بازو (Biceps) – ۱۵ حرکت
	111.	Biceps Curl Machine – جلو بازو، مبتدی تا حرفه‌ای، آرنج ثابت، دم پایین، بازدم بالا، هر دو
	112.	Preacher Curl Machine – جلو بازو، متوسط، پشت بازو روی نیمکت، دم پایین، بازدم بالا، هر دو
	113.	Cable Biceps Curl – جلو بازو، متوسط، حرکت صاف، دم پایین، بازدم بالا، هر دو
	114.	Cable Hammer Curl – جلو بازو و ساعد، متوسط، دست‌ها صاف، دم پایین، بازدم بالا، هر دو
	115.	Single Arm Cable Curl – جلو بازو، متوسط، کنترل یک دست، دم پایین، بازدم بالا، هر دو
	116.	Iso-Lateral Biceps Curl – جلو بازو، متوسط تا حرفه‌ای، دم پایین، بازدم بالا، هر دو
	117.	Biceps Curl Drop Set – جلو بازو، حرفه‌ای، دم پایین، بازدم بالا، هر دو
	118.	Preacher Curl Drop Set – جلو بازو، حرفه‌ای، دم پایین، بازدم بالا، هر دو
	119.	Cable Incline Curl – جلو بازو، متوسط، دم پایین، بازدم بالا، هر دو
	120.	Hammer Strength Biceps Curl – جلو بازو، متوسط تا حرفه‌ای، دم پایین، بازدم بالا، هر دو
	121.	Alternating Biceps Curl Machine – جلو بازو، متوسط، دم پایین، بازدم بالا، هر دو
	122.	Concentration Curl Machine – جلو بازو، متوسط، تمرکز روی عضله، دم پایین، بازدم بالا، هر دو
	123.	Cable Spider Curl – جلو بازو، حرفه‌ای، دم پایین، بازدم بالا، هر دو
	124.	Seated Biceps Curl Machine – جلو بازو، متوسط، آرنج ثابت، دم پایین، بازدم بالا، هر دو
	125.	Cable Preacher Curl – جلو بازو، متوسط تا حرفه‌ای، دم پایین، بازدم بالا، هر دو

🟫 ۶) پشت بازو (Triceps) – ۱۵ حرکت
	126.	Triceps Extension Machine – پشت بازو، مبتدی تا متوسط، آرنج ثابت، دم پایین، بازدم فشار، هر دو
	127.	Cable Rope Pushdown – پشت بازو، متوسط، کنترل آرنج، دم پایین، بازدم فشار، هر دو
	128.	Cable Bar Pushdown – پشت بازو، متوسط، دم پایین، بازدم بالا، هر دو
	129.	Overhead Cable Triceps Extension – پشت بازو، متوسط، آرنج بالا، دم پایین، بازدم فشار، هر دو
	130.	Single Arm Cable Triceps – پشت بازو، متوسط، کنترل یک دست، دم پایین، بازدم فشار، هر دو
	131.	Iso-Lateral Triceps Extension – پشت بازو، متوسط تا حرفه‌ای، دم پایین، بازدم بالا، هر دو
	132.	Triceps Extension Drop Set – پشت بازو، حرفه‌ای، دم پایین، بازدم فشار، هر دو
	133.	Cable Overhead Drop Set – پشت بازو، حرفه‌ای، دم پایین، بازدم فشار، هر دو
	134.	Hammer Strength Triceps Press – پشت بازو، متوسط، دم پایین، بازدم فشار، هر دو
	135.	Seated Triceps Press Machine – پشت بازو، متوسط، دم پایین، بازدم فشار، هر دو
	136.	Cable Kickback – پشت بازو، متوسط، آرنج ثابت، دم پایین، بازدم فشار، هر دو
	137.	Close Grip Triceps Press Machine – پشت بازو، متوسط، دم پایین، بازدم فشار، هر دو
	138.	Triceps Pushdown Drop Set – پشت بازو، حرفه‌ای، دم پایین، بازدم فشار، هر دو
	139.	Cable Reverse Grip Pushdown – پشت بازو، متوسط، دم پایین، بازدم فشار، هر دو
	140.	Assisted Dip Machine – پشت بازو، مبتدی، دم پایین، بازدم فشار، هر دو

⬛ ۷) شکم و پهلو (Core/Abs) – ۲۰ حرکت
	141.	Ab Crunch Machine – شکم، مبتدی تا متوسط، پشت صاف، دم پایین، بازدم بالا، هر دو
	142.	Ab Coaster Machine – شکم، متوسط، حرکت کنترل‌شده، دم پایین، بازدم بالا، هر دو
	143.	Cable Wood Chop High – شکم و مایل‌ها، متوسط، دم پایین، بازدم بالا، هر دو
	144.	Cable Wood Chop Low – شکم و مایل‌ها، متوسط، دم پایین، بازدم بالا، هر دو
	145.	Cable Side Bend – پهلو، متوسط، حرکت صاف، دم پایین، بازدم بالا، هر دو
	146.	Rotational Cable Twist – شکم، متوسط، دم پایین، بازدم بالا، هر دو
	147.	Hanging Leg Raise (Machine Assist) – شکم پایین، متوسط، حرکت کنترل‌شده، دم پایین، بازدم بالا، هر دو
	148.	Decline Sit-Up Bench (با وزنه) – شکم، متوسط، دم پایین، بازدم بالا، هر دو
	149.	Cable Crunch – شکم، متوسط تا حرفه‌ای، دم پایین، بازدم بالا، هر دو
	150.	Incline Ab Crunch Machine – شکم، متوسط، دم پایین، بازدم بالا، هر دو
	151.	Ab Coaster Drop Set – شکم، حرفه‌ای، دم پایین، بازدم بالا، هر دو
	152.	Cable Oblique Crunch – پهلو، متوسط، دم پایین، بازدم بالا، هر دو
	153.	Iso-Lateral Crunch – شکم، متوسط، دم پایین، بازدم بالا، هر دو
	154.	Cable Seated Twist – شکم و مایل‌ها، متوسط، دم پایین، بازدم بالا، هر دو
	155.	Ab Roller Machine – شکم، متوسط، حرکت کنترل‌شده، دم پایین، بازدم بالا، هر دو
	156.	Cable Hanging Side Crunch – پهلو، متوسط، دم پایین، بازدم بالا، هر دو
	157.	Machine Oblique Crunch – پهلو، متوسط، دم پایین، بازدم بالا، هر دو
	158.	Weighted Cable Twist – شکم و مایل‌ها، حرفه‌ای، دم پایین، بازدم بالا، هر دو
	159.	Incline Weighted Sit-Up – شکم، حرفه‌ای، دم پایین، بازدم بالا، هر دو
	160.	Hanging Knee Raise (Machine Assist) – شکم پایین، مبتدی تا متوسط، دم پایین، بازدم بالا، هر دو

🟨 ۸) باسن و همسترینگ (Glutes/Hamstrings) – ۲۰ حرکت
	161.	Hip Thrust Machine – باسن، متوسط تا حرفه‌ای، توقف ۲ ثانیه بالا، دم پایین، بازدم فشار، هر دو
	162.	Glute Drive Machine – باسن، متوسط، حرکت کنترل‌شده، دم پایین، بازدم بالا، هر دو
	163.	Standing Hip Extension Cable – باسن، متوسط، دم پایین، بازدم فشار، هر دو
	164.	Cable Glute Kickback – باسن، متوسط، آرنج و زانو صاف، دم پایین، بازدم فشار، هر دو
	165.	Seated Leg Curl – همسترینگ، متوسط، دم پایین، بازدم بالا، هر دو
	166.	Lying Leg Curl – همسترینگ، متوسط، دم پایین، بازدم بالا، هر دو
	167.	Glute Bridge Machine – باسن، متوسط، توقف ۲ ثانیه بالا، دم پایین، بازدم بالا، هر دو
	168.	Iso-Lateral Hip Thrust – باسن، حرفه‌ای، دم پایین، بازدم فشار، هر دو
	169.	Cable Pull-Through – باسن و همسترینگ، متوسط، دم پایین، بازدم فشار، هر دو
	170.	Glute Kickback Drop Set – باسن، حرفه‌ای، دم پایین، بازدم فشار، هر دو
	171.	Lying Leg Curl Drop Set – همسترینگ، حرفه‌ای، دم پایین، بازدم بالا، هر دو
	172.	Seated Leg Curl Drop Set – همسترینگ، حرفه‌ای، دم پایین، بازدم بالا، هر دو
	173.	Standing Glute Kickback Single Leg – باسن، متوسط، دم پایین، بازدم بالا، هر دو
	174.	Hip Thrust Single Leg – باسن، متوسط، دم پایین، بازدم فشار، هر دو
	175.	Glute Bridge Iso-Lateral – باسن، متوسط، دم پایین، بازدم فشار، هر دو
	176.	Cable Glute Kickback Single Leg – باسن، متوسط، دم پایین، بازدم فشار، هر دو
	177.	Machine Romanian Deadlift – همسترینگ، متوسط تا حرفه‌ای، کمر صاف، دم پایین، بازدم بالا، هر دو
	178.	Pendulum Squat – چهارسر و باسن، متوسط، دم پایین، بازدم بالا، هر دو
	179.	Smith Machine Hip Thrust – باسن، متوسط تا حرفه‌ای، دم پایین، بازدم فشار، هر دو
	180.	Iso-Lateral Leg Curl – همسترینگ، حرفه‌ای، دم پایین، بازدم بالا، هر دو

⬛ ۹) ساعد و مچ (Forearms/Wrists) – ۱۰ حرکت
	181.	Wrist Curl Machine – ساعد، مبتدی، دم پایین، بازدم بالا، هر دو
	182.	Reverse Wrist Curl Machine – ساعد، متوسط، دم پایین، بازدم بالا، هر دو
	183.	Cable Wrist Curl – ساعد، متوسط، حرکت کنترل‌شده، دم پایین، بازدم بالا، هر دو
	184.	Hammer Strength Wrist Curl – ساعد، متوسط، دم پایین، بازدم بالا، هر دو
	185.	Seated Wrist Curl Machine – ساعد، متوسط، دم پایین، بازدم بالا، هر دو
	186.	Reverse Preacher Wrist Curl – ساعد، متوسط، دم پایین، بازدم بالا، هر دو
	187.	Cable Reverse Curl Drop Set – ساعد، حرفه‌ای، دم پایین، بازدم بالا، هر دو
	188.	Iso-Lateral Wrist Curl – ساعد، متوسط، دم پایین، بازدم بالا، هر دو
	189.	Barbell Wrist Curl (Machine Assisted) – ساعد، متوسط، دم پایین، بازدم بالا، هر دو
	190.	Cable Hammer Wrist Curl – ساعد، متوسط، دم پایین، بازدم بالا، هر دو

🟪 ۱۰) حرکات ترکیبی / پیشرفته (Compound / Advanced Machine) – ۲۰ حرکت
	191.	Cable Squat to Row – کل بدن، حرفه‌ای، حرکت کنترل‌شده، دم پایین، بازدم فشار، هر دو
	192.	Cable Deadlift – کل بدن، حرفه‌ای، کمر صاف، دم پایین، بازدم فشار، هر دو
	193.	Cable Split Squat – پایین‌تنه، حرفه‌ای، دم پایین، بازدم بالا، هر دو
	194.	Machine Chest + Cable Fly Superset – سینه، حرفه‌ای، دم پایین، بازدم بالا، هر دو
	195.	Back Row + Lat Pulldown Superset – پشت، حرفه‌ای، دم پایین، بازدم بالا، هر دو
	196.	Leg Press + Calf Raise Superset – پا و ساق، حرفه‌ای، دم پایین، بازدم بالا، هر دو
	197.	Iso-Lateral Chest Press Single Arm – سینه، حرفه‌ای، دم پایین، بازدم فشار، هر دو
	198.	Lat Pulldown Drop Set Machine – پشت، حرفه‌ای، دم پایین، بازدم بالا، هر دو
	199.	Assisted Pull-Up + Dip Combo – پشت و پشت بازو، حرفه‌ای، دم پایین، بازدم فشار، هر دو
	200.	Cable Row + Biceps Curl Superset – پشت و جلو بازو، حرفه‌ای، دم پایین، بازدم بالا، هر دو
"""

GROUP_RE = re.compile(r'^[🟥🟦🟩🟧🟪🟫⬛🟨]?\s*\d+\)\s*(.*?)\s*–\s*\d+\s*حرکت', re.M)
ITEM_RE = re.compile(r'^\s*(\d+)\.\s*([A-Za-z0-9\-\(\)\/\+\s°]+)', re.M)

TARGET_KEYWORDS = [
    ("بالاسینه", "سینه بالا"),
    ("زیرسینه", "سینه پایین"),
    ("سینه بالا", "سینه بالا"),
    ("سینه پایین", "سینه پایین"),
    ("سینه", "سینه"),
    ("میان‌پشت", "میان پشت"),
    ("میان پشت", "میان پشت"),
    ("پشت بالایی", "پشت بالا"),
    ("پشت بالا", "پشت بالا"),
    ("پشت پایین", "پشت پایین"),
    ("پشت", "پشت"),
    ("دلتوئید جانبی", "شانه جانبی"),
    ("شانه جانبی", "شانه جانبی"),
    ("شانه جلو", "شانه جلو"),
    ("شانه عقب", "شانه عقب"),
    ("شانه پشت", "شانه عقب"),
    ("شانه فوقانی", "شانه فوقانی"),
    ("شانه", "شانه"),
    ("چهارسر", "چهارسر"),
    ("همسترینگ", "همسترینگ"),
    ("باسن", "باسن"),
    ("ساق", "ساق"),
    ("داخل ران", "داخل ران"),
    ("اداکتور داخلی", "داخل ران"),
    ("اداکتور جانبی", "خارج ران"),
    ("خارج ران", "خارج ران"),
    ("جلو بازو", "جلو بازو"),
    ("پشت بازو", "پشت بازو"),
    ("شکم", "شکم"),
    ("پهلو", "پهلو"),
    ("مایل", "پهلو"),
    ("ساعد", "ساعد"),
    ("کل بدن", "کل بدن"),
]

TARGET_FA_TO_EN = {
    "سینه": "Chest",
    "سینه بالا": "Upper chest",
    "سینه پایین": "Lower chest",
    "سینه میانی": "Mid chest",
    "میان پشت": "Mid back",
    "پشت": "Back",
    "پشت بالا": "Upper back",
    "پشت پایین": "Lower back",
    "شانه": "Shoulders",
    "شانه جانبی": "Lateral deltoid",
    "شانه جلو": "Front deltoid",
    "شانه عقب": "Rear deltoid",
    "شانه فوقانی": "Upper traps",
    "چهارسر": "Quadriceps",
    "همسترینگ": "Hamstrings",
    "باسن": "Glutes",
    "ساق": "Calves",
    "داخل ران": "Inner thigh (adductors)",
    "خارج ران": "Outer thigh (abductors)",
    "جلو بازو": "Biceps",
    "پشت بازو": "Triceps",
    "شکم": "Abs",
    "پهلو": "Obliques",
    "ساعد": "Forearms",
    "کل بدن": "Full body",
}


def _normalize_name(name: str) -> str:
    return re.sub(r'\s+', ' ', name.strip().lower())


def _extract_level(text: str) -> str:
    if 'مبتدی تا حرفه' in text:
        return 'مبتدی تا حرفه‌ای'
    if 'متوسط تا حرفه' in text:
        return 'متوسط تا حرفه‌ای'
    if 'مبتدی تا متوسط' in text:
        return 'مبتدی تا متوسط'
    if 'حرفه‌ای' in text:
        return 'حرفه‌ای'
    if 'متوسط' in text:
        return 'متوسط'
    if 'مبتدی' in text:
        return 'مبتدی'
    return ''


def _extract_gender(text: str) -> str:
    if 'هر دو' in text or 'هردو' in text:
        return 'هر دو'
    if 'آقایان' in text:
        return 'آقایان'
    if 'خانم' in text:
        return 'خانم‌ها'
    return ''


def _extract_breathing(text: str) -> str:
    # Take sentence fragment containing دم/بازدم
    parts = [p.strip() for p in re.split(r'[،\-]\s*', text) if p.strip()]
    breath = [p for p in parts if 'دم' in p or 'بازدم' in p]
    return '، '.join(breath[:2]) if breath else ''


def _extract_fa_name_and_notes(text: str):
    # Split on dash to separate Persian name and notes
    if '–' in text:
        left, right = text.split('–', 1)
    elif '-' in text:
        left, right = text.split('-', 1)
    else:
        return text.strip(), ''
    return left.strip(), right.strip()

def _extract_target_detail_fa(detail: str, fa_name: str, title: str) -> str:
    chunk = detail.replace('،', ',').split(',', 1)[0].strip()
    if chunk and all(x not in chunk for x in ['مبتدی', 'متوسط', 'حرفه‌ای']):
        return chunk
    for key, value in TARGET_KEYWORDS:
        if key in (fa_name or ''):
            return value
    title_fa = title.split('(')[0].replace('عضلات', '').strip()
    return title_fa

def _target_fa_to_en(text: str) -> str:
    if not text:
        return ''
    parts = [p.strip() for p in text.split(' و ') if p.strip()]
    mapped = [TARGET_FA_TO_EN.get(p, p) for p in parts]
    return ' & '.join(mapped)


def parse_raw():
    groups = []
    positions = []
    for m in GROUP_RE.finditer(RAW_TEXT):
        positions.append((m.start(), m.end(), m.group(1).strip()))
    positions.append((len(RAW_TEXT), len(RAW_TEXT), None))
    for i in range(len(positions) - 1):
        start = positions[i][1]
        end = positions[i + 1][0]
        title = positions[i][2]
        section = RAW_TEXT[start:end].strip()
        if not title:
            continue
        groups.append((title, section))
    parsed_groups = []
    seen = set()
    for title, section in groups:
        items = []
        for match in ITEM_RE.finditer(section):
            idx = match.group(1)
            name_en = match.group(2).strip().replace('machin', 'machine')
            span_start = match.end()
            # find next item or end
            next_match = ITEM_RE.search(section, span_start)
            span_end = next_match.start() if next_match else len(section)
            detail = section[span_start:span_end].strip()
            detail = detail.replace('\n', ' ').replace('  ', ' ')
            fa_name, notes = _extract_fa_name_and_notes(detail)
            level = _extract_level(detail)
            gender = _extract_gender(detail)
            breathing = _extract_breathing(detail)
            target_detail_fa = _extract_target_detail_fa(detail, fa_name, title)
            target_detail_en = _target_fa_to_en(target_detail_fa)
            key = _normalize_name(name_en)
            if key in seen:
                continue
            seen.add(key)
            items.append({
                "index": int(idx),
                "name_en": name_en,
                "name_fa": fa_name,
                "target_group_fa": target_detail_fa,
                "target_group_en": target_detail_en,
                "level_fa": level,
                "tips_fa": notes,
                "breathing_fa": breathing,
                "gender_fa": gender,
            })
        parsed_groups.append({"title": title, "items": items})
    return parsed_groups


def export_json(groups):
    os.makedirs(os.path.dirname(OUTPUT_JSON), exist_ok=True)
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(groups, f, ensure_ascii=False, indent=2)
    print("JSON saved:", OUTPUT_JSON)


def _rtl_reshape(text):
    try:
        from arabic_reshaper import ArabicReshaper
        from bidi.algorithm import get_display
    except Exception:
        return text
    reshaper = ArabicReshaper({'use_unshaped_instead_of_isolated': True})
    reshaped = reshaper.reshape(text)
    return get_display(reshaped)


def _rtl_reshape_paragraph(s):
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


def export_pdf(groups):
    try:
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.enums import TA_RIGHT
        from reportlab.lib.units import inch
        from reportlab.lib import colors
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
    except ImportError:
        print('Install: pip install reportlab')
        raise

    vazir_path = os.path.join(PROJECT_ROOT, 'fonts', 'Vazir.ttf')
    if os.path.isfile(vazir_path):
        pdfmetrics.registerFont(TTFont('Vazir', vazir_path))
        pdf_font = 'Vazir'
    else:
        pdf_font = 'Helvetica'

    os.makedirs(os.path.dirname(OUTPUT_PDF), exist_ok=True)
    doc = SimpleDocTemplate(OUTPUT_PDF, pagesize=landscape(A4), rightMargin=28, leftMargin=28, topMargin=32, bottomMargin=32)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(name='Title', parent=styles['Heading1'], fontName=pdf_font, fontSize=14, spaceAfter=10, alignment=TA_RIGHT, wordWrap='RTL')
    heading_style = ParagraphStyle(name='Heading2', parent=styles['Heading2'], fontName=pdf_font, fontSize=11, spaceAfter=6, alignment=TA_RIGHT, wordWrap='RTL')
    body_style = ParagraphStyle(name='Body', parent=styles['Normal'], fontName=pdf_font, fontSize=8.2, spaceAfter=2, alignment=TA_RIGHT, wordWrap='RTL')

    def _cell_fa(text: str) -> Paragraph:
        return Paragraph(_rtl_reshape(text or ''), body_style)

    def _cell_en_fa(en: str, fa: str) -> Paragraph:
        fa_rtl = _rtl_reshape(fa or '')
        combo = f"EN: {en or ''}<br/>FA: {fa_rtl}"
        return Paragraph(combo, body_style)

    story = []
    story.append(Paragraph(_rtl_reshape_paragraph("Exercise Library – Type 1 (Machine) | کتابخانه تمرینات – حالت ۱ (دستگاهی)"), title_style))
    story.append(Spacer(1, 0.15 * inch))
    headers = [
        _rtl_reshape("نام حرکت (EN/FA)"),
        _rtl_reshape("عضله هدف"),
        _rtl_reshape("سطح"),
        _rtl_reshape("نکات اجرای صحیح"),
        _rtl_reshape("تنفس"),
        _rtl_reshape("مناسب"),
    ]
    for gi, group in enumerate(groups):
        story.append(Paragraph(_rtl_reshape_paragraph(group["title"]), heading_style))
        data = [headers]
        for item in group["items"]:
            data.append([
                _cell_en_fa(item['name_en'], item['name_fa']),
                _cell_en_fa(item['target_group_en'], item['target_group_fa']),
                _cell_fa(item['level_fa']),
                _cell_fa(item['tips_fa']),
                _cell_fa(item['breathing_fa']),
                _cell_fa(item['gender_fa']),
            ])
        table = Table(
            data,
            colWidths=[160, 110, 70, 260, 110, 70]
        )
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#eef2f7')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#1f2937')),
            ('FONTNAME', (0, 0), (-1, -1), pdf_font),
            ('FONTSIZE', (0, 0), (-1, 0), 8.5),
            ('FONTSIZE', (0, 1), (-1, -1), 7.8),
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('GRID', (0, 0), (-1, -1), 0.25, colors.HexColor('#cbd5e1')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        story.append(table)
        story.append(Spacer(1, 0.12 * inch))
        if gi < len(groups) - 1:
            story.append(PageBreak())
    doc.build(story)
    print("PDF saved:", OUTPUT_PDF)


def main():
    groups = parse_raw()
    export_json(groups)
    export_pdf(groups)


if __name__ == "__main__":
    main()
