"""
Parse Type 2 (functional/no-equipment) exercise list, export JSON and PDF.
Run from project root: python scripts/export_exercise_library_type2.py
Outputs:
  - frontend/src/data/exerciseLibraryType2.json
  - docs/Exercise_Library_Type2.pdf
"""
import os
import json
import re

PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
OUTPUT_JSON = os.path.join(PROJECT_ROOT, "frontend", "src", "data", "exerciseLibraryType2.json")
OUTPUT_PDF = os.path.join(PROJECT_ROOT, "docs", "Exercise_Library_Type2.pdf")

RAW_TEXT = r"""
حالت ۲ – حرکات بدون دستگاه / فانکشنال

🟥 ۱) عضلات سینه (Chest) – ۲۰ حرکت
	1.	Push-Up – سینه، مبتدی تا حرفه‌ای، بدن صاف، دم پایین، بازدم بالا، هر دو
	2.	Incline Push-Up – سینه بالا، مبتدی، پا روی سطح پایین، دم پایین، بازدم بالا، هر دو
	3.	Decline Push-Up – سینه پایین، متوسط، پا روی سطح بالا، دم پایین، بازدم فشار، هر دو
	4.	Diamond Push-Up – سینه وسط و پشت بازو، متوسط، دست‌ها نزدیک، دم پایین، بازدم فشار، هر دو
	5.	Wide Push-Up – سینه، متوسط، فاصله دست‌ها بیشتر از شانه، دم پایین، بازدم فشار، هر دو
	6.	Archer Push-Up – سینه، حرفه‌ای، یک دست کنترل بیشتر، دم پایین، بازدم فشار، هر دو
	7.	Clap Push-Up – سینه، حرفه‌ای، دم پایین، بازدم بالا، هر دو
	8.	Spiderman Push-Up – سینه و شکم، حرفه‌ای، دم پایین، بازدم بالا، هر دو
	9.	Explosive Push-Up – سینه، حرفه‌ای، دم پایین، بازدم فشار، هر دو
	10.	Staggered Hands Push-Up – سینه، متوسط، دست‌ها متفاوت، دم پایین، بازدم بالا، هر دو
	11.	Hindu Push-Up – سینه و شانه، متوسط، حرکت نرم و پیوسته، دم پایین، بازدم بالا، هر دو
	12.	One Arm Push-Up – سینه، حرفه‌ای، بدن صاف، دم پایین، بازدم فشار، هر دو
	13.	Planche Push-Up (سطح پیشرفته) – سینه و شانه، حرفه‌ای، بدن کاملاً افقی، دم پایین، بازدم فشار، هر دو
	14.	T Push-Up – سینه و شانه، متوسط، تبدیل به T در هر تکرار، دم پایین، بازدم بالا، هر دو
	15.	Incline Diamond Push-Up – سینه بالا، متوسط، دست‌ها نزدیک، دم پایین، بازدم فشار، هر دو
	16.	Decline Diamond Push-Up – سینه پایین، متوسط، پا روی سطح بالا، دم پایین، بازدم فشار، هر دو
	17.	Wide Archer Push-Up – سینه و شانه، حرفه‌ای، دم پایین، بازدم فشار، هر دو
	18.	Plyometric Push-Up – سینه، حرفه‌ای، پرش از زمین، دم پایین، بازدم فشار، هر دو
	19.	Push-Up to Side Plank – سینه و شکم، متوسط، دم پایین، بازدم بالا، هر دو
	20.	Ring Push-Up (در صورت داشتن رینگ) – سینه، متوسط تا حرفه‌ای، دم پایین، بازدم فشار، هر دو

۲) عضلات پشت (Back) – ۲۰ حرکت
	21.	Pull-Up (بارفیکس) – پشت، متوسط تا حرفه‌ای، دم پایین، بازدم بالا، هر دو
	22.	Chin-Up – پشت و جلو بازو، متوسط، دم پایین، بازدم بالا، هر دو
	23.	Wide Grip Pull-Up – پشت بالا، متوسط تا حرفه‌ای، دم پایین، بازدم بالا، هر دو
	24.	Close Grip Pull-Up – پشت وسط، متوسط، دم پایین، بازدم بالا، هر دو
	25.	Inverted Row (روی میله پایین) – پشت، مبتدی تا متوسط، بدن صاف، دم پایین، بازدم بالا، هر دو
	26.	Bodyweight Row – پشت، متوسط، دم پایین، بازدم بالا، هر دو
	27.	Superman Hold – پشت پایین و شکم، مبتدی، دم پایین، بازدم فشار، هر دو
	28.	Towel Row (با حوله و میله) – پشت، متوسط، دم پایین، بازدم بالا، هر دو
	29.	Horizontal Pull-Up – پشت، متوسط تا حرفه‌ای، دم پایین، بازدم بالا، هر دو
	30.	One Arm Inverted Row – پشت، حرفه‌ای، دم پایین، بازدم فشار، هر دو
	31.	Archer Pull-Up – پشت، حرفه‌ای، دم پایین، بازدم بالا، هر دو
	32.	Assisted Pull-Up (با کش) – پشت، مبتدی، دم پایین، بازدم فشار، هر دو
	33.	Jumping Pull-Up – پشت، متوسط تا حرفه‌ای، دم پایین، بازدم فشار، هر دو
	34.	Scapular Pull-Up – پشت بالا، مبتدی، حرکت شانه، دم پایین، بازدم بالا، هر دو
	35.	L-Sit Pull-Up – پشت و شکم، حرفه‌ای، دم پایین، بازدم فشار، هر دو
	36.	Ring Row – پشت، متوسط، دم پایین، بازدم بالا، هر دو
	37.	Inverted Row Drop Set – پشت، حرفه‌ای، دم پایین، بازدم بالا، هر دو
	38.	Wide Grip Inverted Row – پشت بالا، متوسط، دم پایین، بازدم بالا، هر دو
	39.	Bodyweight Row Single Arm – پشت، حرفه‌ای، دم پایین، بازدم بالا، هر دو
	40.	Horizontal Pull-Up with Pause – پشت، حرفه‌ای، توقف ۲ ثانیه، دم پایین، بازدم بالا، هر دو

۳) شانه (Shoulders) – ۲۰ حرکت
	41.	Pike Push-Up – شانه، مبتدی تا متوسط، بدن V شکل، دم پایین، بازدم فشار، هر دو
	42.	Handstand Push-Up – شانه، حرفه‌ای، بدن عمودی، دم پایین، بازدم فشار، هر دو
	43.	Plank to Shoulder Tap – شانه و شکم، مبتدی تا متوسط، بدن صاف، دم پایین، بازدم بالا، هر دو
	44.	Dumbbell-Free Lateral Raise Simulation (با کش یا وزنه بدن) – شانه جانبی، متوسط، دم پایین، بازدم بالا، هر دو
	45.	Hindu Push-Up – شانه و سینه، متوسط، حرکت پیوسته، دم پایین، بازدم بالا، هر دو
	46.	Elevated Pike Push-Up – شانه، متوسط، پا روی سطح بالاتر، دم پایین، بازدم فشار، هر دو
	47.	Side Plank Reach Under – شانه جانبی و شکم، متوسط، دم پایین، بازدم بالا، هر دو
	48.	T-Push-Up – شانه، متوسط، تبدیل به T در پایان هر حرکت، دم پایین، بازدم بالا، هر دو
	49.	Wall Walk – شانه، حرفه‌ای، دم پایین، بازدم فشار، هر دو
	50.	Plank to Downward Dog – شانه، مبتدی تا متوسط، دم پایین، بازدم بالا، هر دو
	51.	Arm Circles – شانه، مبتدی، گرم‌کننده، دم پایین، بازدم آزاد، هر دو
	52.	Shoulder Taps on Knees – شانه، مبتدی، دم پایین، بازدم بالا، هر دو
	53.	Plank Reach – شانه و شکم، متوسط، دم پایین، بازدم بالا، هر دو
	54.	Scapular Push-Up – شانه و پشت، مبتدی، حرکت شانه بدون آرنج، دم پایین، بازدم فشار، هر دو
	55.	Side Plank Arm Lift – شانه جانبی و شکم، متوسط، دم پایین، بازدم بالا، هر دو
	56.	Reverse Plank Leg Lift – شانه و پشت، متوسط، دم پایین، بازدم فشار، هر دو
	57.	Handstand Wall Walk Hold – شانه، حرفه‌ای، دم پایین، بازدم فشار، هر دو
	58.	Y-T Raises (با وزن بدن یا کش) – شانه پشت، متوسط، دم پایین، بازدم بالا، هر دو
	59.	Plank to Side Arm Raise – شانه، متوسط، دم پایین، بازدم بالا، هر دو
	60.	Shoulder Shrugs (با وزن بدن یا کش) – شانه فوقانی، مبتدی، دم پایین، بازدم فشار، هر دو

۴) پایین‌تنه / پاها (Legs) – ۳۰ حرکت
	61.	Bodyweight Squat – چهارسر، باسن، مبتدی تا متوسط، کمر صاف، دم پایین، بازدم بالا، هر دو
	62.	Jump Squat – چهارسر، باسن، متوسط تا حرفه‌ای، دم پایین، بازدم بالا، هر دو
	63.	Lunge Forward – چهارسر، باسن، مبتدی تا متوسط، دم پایین، بازدم بالا، هر دو
	64.	Reverse Lunge – چهارسر، باسن، مبتدی تا متوسط، دم پایین، بازدم بالا، هر دو
	65.	Side Lunge – چهارسر، باسن، متوسط، دم پایین، بازدم بالا، هر دو
	66.	Curtsy Lunge – باسن و چهارسر، متوسط، دم پایین، بازدم بالا، هر دو
	67.	Split Squat – چهارسر و باسن، متوسط، دم پایین، بازدم بالا، هر دو
	68.	Bulgarian Split Squat – چهارسر و باسن، متوسط تا حرفه‌ای، دم پایین، بازدم بالا، هر دو
	69.	Step-Up (روی سطح ثابت) – چهارسر و باسن، مبتدی تا متوسط، دم پایین، بازدم بالا، هر دو
	70.	Step-Up with Knee Raise – چهارسر و شکم، متوسط، دم پایین، بازدم بالا، هر دو
	71.	Single Leg Squat (Pistol Squat) – چهارسر، حرفه‌ای، دم پایین، بازدم فشار، هر دو
	72.	Wall Sit – چهارسر، مبتدی، دم پایین، بازدم کنترل‌شده، هر دو
	73.	Calf Raise – ساق، مبتدی، دم پایین، بازدم فشار، هر دو
	74.	Single Leg Calf Raise – ساق، متوسط، دم پایین، بازدم فشار، هر دو
	75.	Jumping Lunge – چهارسر و باسن، حرفه‌ای، دم پایین، بازدم بالا، هر دو
	76.	Side Step Squat – باسن و چهارسر، متوسط، دم پایین، بازدم بالا، هر دو
	77.	Frog Jump – چهارسر و باسن، متوسط تا حرفه‌ای، دم پایین، بازدم فشار، هر دو
	78.	Glute Bridge – باسن، مبتدی تا متوسط، توقف ۲ ثانیه، دم پایین، بازدم فشار، هر دو
	79.	Single Leg Glute Bridge – باسن، متوسط، دم پایین، بازدم فشار، هر دو
	80.	Donkey Kick – باسن، مبتدی تا متوسط، دم پایین، بازدم فشار، هر دو
	81.	Fire Hydrant – باسن، مبتدی، دم پایین، بازدم بالا، هر دو
	82.	Side-Lying Leg Lift – باسن و پاها، مبتدی، دم پایین، بازدم بالا، هر دو
	83.	Clamshell – باسن جانبی، مبتدی، دم پایین، بازدم بالا، هر دو
	84.	Sumo Squat – باسن و داخل ران، متوسط، دم پایین، بازدم بالا، هر دو
	85.	Broad Jump – چهارسر و باسن، حرفه‌ای، دم پایین، بازدم فشار، هر دو
	86.	Skater Squat – باسن و چهارسر، متوسط تا حرفه‌ای، دم پایین، بازدم بالا، هر دو
	87.	Lateral Step-Up – باسن و چهارسر، متوسط، دم پایین، بازدم بالا، هر دو
	88.	Curtsy Lunge Jump – باسن و چهارسر، حرفه‌ای، دم پایین، بازدم فشار، هر دو
	89.	Wall Sit with Arm Raise – چهارسر و شانه، مبتدی تا متوسط، دم پایین، بازدم بالا، هر دو
	90.	Squat Hold with Pulse – چهارسر و باسن، متوسط، دم پایین، بازدم فشار، هر دو

۵) جلو بازو (Biceps) – ۱۰ حرکت
	91.	Bodyweight Biceps Curl (با کش یا حوله) – جلو بازو، مبتدی تا متوسط، آرنج ثابت، دم پایین، بازدم بالا، هر دو
	92.	Chin-Up Narrow Grip – جلو بازو و پشت، متوسط، دم پایین، بازدم بالا، هر دو
	93.	Commando Pull-Up – جلو بازو و پشت، حرفه‌ای، دم پایین، بازدم فشار، هر دو
	94.	Inverted Row Underhand Grip – جلو بازو و پشت، متوسط، دم پایین، بازدم بالا، هر دو
	95.	Isometric Curl Hold (با کش) – جلو بازو، متوسط، نگه داشتن ۵ ثانیه، دم پایین، بازدم فشار، هر دو
	96.	Towel Curl (با حوله و میله) – جلو بازو، متوسط، کنترل کشش، دم پایین، بازدم بالا، هر دو
	97.	One Arm Chin-Up – جلو بازو و پشت، حرفه‌ای، دم پایین، بازدم فشار، هر دو
	98.	Bodyweight Hammer Curl Simulation – جلو بازو و ساعد، متوسط، دم پایین، بازدم بالا، هر دو
	99.	Pull-Up + Hold – جلو بازو و پشت، حرفه‌ای، توقف بالا ۲ ثانیه، دم پایین، بازدم فشار، هر دو
	100.	Inverted Row Single Arm – جلو بازو و پشت، حرفه‌ای، دم پایین، بازدم بالا، هر دو

⬛ ۶) پشت بازو (Triceps) – ۱۰ حرکت
	101.	Diamond Push-Up – پشت بازو و سینه، متوسط، دست‌ها نزدیک، دم پایین، بازدم فشار، هر دو
	102.	Triceps Dips (روی صندلی یا سطح ثابت) – پشت بازو، مبتدی تا متوسط، دم پایین، بازدم فشار، هر دو
	103.	Bench Dip – پشت بازو، متوسط، آرنج نزدیک بدن، دم پایین، بازدم فشار، هر دو
	104.	Close Grip Push-Up – پشت بازو، متوسط، دم پایین، بازدم فشار، هر دو
	105.	Overhead Triceps Extension (با کش) – پشت بازو، متوسط، دم پایین، بازدم فشار، هر دو
	106.	Bodyweight Kickback – پشت بازو، متوسط، دم پایین، بازدم فشار، هر دو
	107.	Triceps Push-Up on Knees – پشت بازو، مبتدی، دم پایین، بازدم فشار، هر دو
	108.	Elevated Triceps Dip – پشت بازو، متوسط، پا روی سطح بالاتر، دم پایین، بازدم فشار، هر دو
	109.	Close Grip Elevated Push-Up – پشت بازو و سینه، متوسط تا حرفه‌ای، دم پایین، بازدم فشار، هر دو
	110.	Bodyweight Triceps Hold – پشت بازو، حرفه‌ای، نگه داشتن ۵–۱۰ ثانیه، دم پایین، بازدم فشار، هر دو

🟨 ۷) شکم و پهلو (Core/Abs) – ۲۰ حرکت
	111.	Plank – شکم، مبتدی، بدن صاف، دم پایین، بازدم آزاد، هر دو
	112.	Side Plank – شکم و پهلو، مبتدی، دم پایین، بازدم آزاد، هر دو
	113.	Plank with Shoulder Tap – شکم و شانه، متوسط، دم پایین، بازدم بالا، هر دو
	114.	Plank with Leg Lift – شکم و باسن، متوسط، دم پایین، بازدم بالا، هر دو
	115.	Mountain Climbers – شکم، متوسط، دم پایین، بازدم بالا، هر دو
	116.	Bicycle Crunch – شکم و مایل‌ها، متوسط، دم پایین، بازدم بالا، هر دو
	117.	Reverse Crunch – شکم پایین، متوسط، دم پایین، بازدم بالا، هر دو
	118.	Flutter Kicks – شکم پایین، مبتدی تا متوسط، دم پایین، بازدم آزاد، هر دو
	119.	Leg Raise – شکم پایین، متوسط، دم پایین، بازدم بالا، هر دو
	120.	V-Up – شکم، متوسط تا حرفه‌ای، دم پایین، بازدم بالا، هر دو
	121.	Russian Twist – شکم و مایل‌ها، متوسط، دم پایین، بازدم بالا، هر دو
	122.	Side Plank Hip Dip – پهلو، متوسط، دم پایین، بازدم بالا، هر دو
	123.	Plank with Arm Reach – شکم، متوسط، دم پایین، بازدم بالا، هر دو
	124.	Plank with Knee to Elbow – شکم و پهلو، متوسط، دم پایین، بازدم بالا، هر دو
	125.	Spider Plank – شکم و پهلو، متوسط، دم پایین، بازدم بالا، هر دو
	126.	Hollow Body Hold – شکم، حرفه‌ای، دم پایین، بازدم بالا، هر دو
	127.	Side Crunch – پهلو، متوسط، دم پایین، بازدم بالا، هر دو
	128.	Toe Touch – شکم بالا، مبتدی تا متوسط، دم پایین، بازدم بالا، هر دو
	129.	Standing Oblique Crunch – پهلو، مبتدی، دم پایین، بازدم بالا، هر دو
	130.	Plank to Side Plank – شکم و پهلو، متوسط، دم پایین، بازدم بالا، هر دو

۸) باسن و همسترینگ (Glutes/Hamstrings) – ۲۰ حرکت
	131.	Glute Bridge – باسن، مبتدی تا متوسط، توقف ۲ ثانیه، دم پایین، بازدم فشار، هر دو
	132.	Single Leg Glute Bridge – باسن، متوسط، دم پایین، بازدم فشار، هر دو
	133.	Donkey Kick – باسن، مبتدی تا متوسط، دم پایین، بازدم فشار، هر دو
	134.	Fire Hydrant – باسن، مبتدی، دم پایین، بازدم بالا، هر دو
	135.	Side-Lying Leg Lift – باسن جانبی، مبتدی، دم پایین، بازدم بالا، هر دو
	136.	Clamshell – باسن جانبی، مبتدی، دم پایین، بازدم بالا، هر دو
	137.	Sumo Squat – باسن و داخل ران، متوسط، دم پایین، بازدم بالا، هر دو
	138.	Frog Jump – باسن و چهارسر، متوسط تا حرفه‌ای، دم پایین، بازدم فشار، هر دو
	139.	Broad Jump – باسن و چهارسر، حرفه‌ای، دم پایین، بازدم فشار، هر دو
	140.	Lateral Step-Out Squat – باسن و چهارسر، متوسط، دم پایین، بازدم بالا، هر دو
	141.	Curtsy Lunge – باسن و چهارسر، متوسط، دم پایین، بازدم بالا، هر دو
	142.	Bulgarian Split Squat – باسن و چهارسر، متوسط تا حرفه‌ای، دم پایین، بازدم بالا، هر دو
	143.	Jumping Lunge – باسن و چهارسر، حرفه‌ای، دم پایین، بازدم بالا، هر دو
	144.	Step-Up (بدون وزنه) – باسن و چهارسر، مبتدی تا متوسط، دم پایین، بازدم بالا، هر دو
	145.	Step-Up with Knee Raise – باسن و شکم، متوسط، دم پایین، بازدم بالا، هر دو
	146.	Skater Squat – باسن و چهارسر، متوسط تا حرفه‌ای، دم پایین، بازدم بالا، هر دو
	147.	Wall Sit – باسن و چهارسر، مبتدی، دم پایین، بازدم آزاد، هر دو
	148.	Squat Hold with Pulse – باسن و چهارسر، متوسط، دم پایین، بازدم فشار، هر دو
	149.	Side Step Squat – باسن و چهارسر، متوسط، دم پایین، بازدم بالا، هر دو
	150.	Glute Bridge March – باسن، متوسط، حرکت پاها متناوب، دم پایین، بازدم فشار، هر دو

⸻

⬛ ۹) حرکات ترکیبی / پیشرفته فانکشنال – ۲۰ حرکت
	151.	Burpee – کل بدن، مبتدی تا حرفه‌ای، دم پایین، بازدم فشار، هر دو
	152.	Burpee Pull-Up – کل بدن، حرفه‌ای، دم پایین، بازدم فشار، هر دو
	153.	Mountain Climber to Push-Up – کل بدن، متوسط تا حرفه‌ای، دم پایین، بازدم بالا، هر دو
	154.	Jump Squat + Push-Up Combo – کل بدن، حرفه‌ای، دم پایین، بازدم فشار، هر دو
	155.	Plank to Push-Up – کل بدن، متوسط، دم پایین، بازدم بالا، هر دو
	156.	Lunge to Knee Raise – پایین‌تنه و شکم، متوسط، دم پایین، بازدم بالا، هر دو
	157.	Spiderman Plank to Push-Up – کل بدن، حرفه‌ای، دم پایین، بازدم فشار، هر دو
	158.	Tuck Jump – پایین‌تنه و شکم، حرفه‌ای، دم پایین، بازدم فشار، هر دو
	159.	Skater Jump – باسن و چهارسر، متوسط تا حرفه‌ای، دم پایین، بازدم بالا، هر دو
	160.	Lunge Jump + Twist – پایین‌تنه و شکم، حرفه‌ای، دم پایین، بازدم بالا، هر دو
	161.	Bear Crawl – کل بدن، متوسط، دم پایین، بازدم بالا، هر دو
	162.	Crab Walk – کل بدن، متوسط، دم پایین، بازدم بالا، هر دو
	163.	Side Lunge to Reach – پایین‌تنه و شکم، متوسط، دم پایین، بازدم بالا، هر دو
	164.	Plank Jacks – شکم و شانه، متوسط، دم پایین، بازدم بالا، هر دو
	165.	Push-Up to Side Plank – کل بدن، متوسط، دم پایین، بازدم بالا، هر دو
	166.	Jumping Jack to Squat – کل بدن، مبتدی تا متوسط، دم پایین، بازدم بالا، هر دو
	167.	Broad Jump + Backward Walk – باسن و چهارسر، متوسط، دم پایین، بازدم بالا، هر دو
	168.	Single-Leg Burpee – کل بدن، حرفه‌ای، دم پایین، بازدم فشار، هر دو
	169.	Lunge Matrix – پایین‌تنه، متوسط تا حرفه‌ای، دم پایین، بازدم بالا، هر دو
	170.	Push-Up + Mountain Climber Superset – کل بدن، حرفه‌ای، دم پایین، بازدم فشار، هر دو

جلوبازو – تکمیل ۱۰ حرکت دیگر (حرکات بدون دستگاه / فانکشنال)
	171.	Bodyweight Biceps Curl with Towel Hold – جلو بازو، متوسط، دم پایین، بازدم بالا، هر دو
	172.	Isometric Chin-Up Hold – جلو بازو و پشت، حرفه‌ای، توقف ۳–۵ ثانیه، دم پایین، بازدم فشار، هر دو
	173.	Wide Grip Chin-Up – جلو بازو و پشت، متوسط، دم پایین، بازدم بالا، هر دو
	174.	Close Grip Chin-Up – جلو بازو و پشت، متوسط، دم پایین، بازدم بالا، هر دو
	175.	Commando Pull-Up Hold – جلو بازو و پشت، حرفه‌ای، توقف بالا ۲ ثانیه، دم پایین، بازدم فشار، هر دو
	176.	Towel Curl + Hold – جلو بازو، متوسط، دم پایین، بازدم فشار، هر دو
	177.	Bodyweight Hammer Curl – جلو بازو و ساعد، متوسط، دم پایین، بازدم بالا، هر دو
	178.	One Arm Chin-Up Hold – جلو بازو و پشت، حرفه‌ای، دم پایین، بازدم فشار، هر دو
	179.	Inverted Row with Biceps Focus – جلو بازو، متوسط، دم پایین، بازدم بالا، هر دو
	180.	Chin-Up to Hold – جلو بازو و پشت، حرفه‌ای، توقف بالا، دم پایین، بازدم فشار، هر دو
"""

GROUP_RE = re.compile(r'^[🟥🟦🟩🟧🟪🟫⬛🟨]?\s*\d+\)\s*(.*?)\s*–\s*\d+\s*حرکت', re.M)
ITEM_RE = re.compile(r'^\s*(\d+)\.\s*([A-Za-z0-9\-\(\)\/\+\s°]+)', re.M)

NAME_FA = {
    "Push-Up": "شنا سوئدی",
    "Incline Push-Up": "شنا سوئدی شیب مثبت",
    "Decline Push-Up": "شنا سوئدی شیب منفی",
    "Diamond Push-Up": "شنا سوئدی الماسی",
    "Wide Push-Up": "شنا سوئدی دست باز",
    "Archer Push-Up": "شنا سوئدی کماندار",
    "Clap Push-Up": "شنا سوئدی انفجاری با کف‌زنی",
    "Spiderman Push-Up": "شنا سوئدی اسپایدرمن",
    "Explosive Push-Up": "شنا سوئدی انفجاری",
    "Staggered Hands Push-Up": "شنا سوئدی دست‌های نامتقارن",
    "Hindu Push-Up": "شنا هندو",
    "One Arm Push-Up": "شنا سوئدی تک‌دست",
    "Planche Push-Up (سطح پیشرفته)": "شنا پلانچ",
    "Planche Push-Up": "شنا پلانچ",
    "T Push-Up": "شنا سوئدی تی",
    "Incline Diamond Push-Up": "شنا سوئدی الماسی شیب مثبت",
    "Decline Diamond Push-Up": "شنا سوئدی الماسی شیب منفی",
    "Wide Archer Push-Up": "شنا سوئدی کماندار دست باز",
    "Plyometric Push-Up": "شنا سوئدی پلیومتریک",
    "Push-Up to Side Plank": "شنا سوئدی به پلانک پهلو",
    "Ring Push-Up (در صورت داشتن رینگ)": "شنا سوئدی با رینگ",
    "Ring Push-Up": "شنا سوئدی با رینگ",
    "Pull-Up": "بارفیکس",
    "Pull-Up (بارفیکس)": "بارفیکس",
    "Chin-Up": "چین‌آپ",
    "Wide Grip Pull-Up": "بارفیکس دست باز",
    "Close Grip Pull-Up": "بارفیکس دست جمع",
    "Inverted Row (روی میله پایین)": "روئینگ معکوس",
    "Inverted Row": "روئینگ معکوس",
    "Bodyweight Row": "روئینگ وزن بدن",
    "Superman Hold": "نگه‌داشتن سوپرمن",
    "Towel Row (با حوله و میله)": "روئینگ با حوله",
    "Towel Row": "روئینگ با حوله",
    "Horizontal Pull-Up": "بارفیکس افقی",
    "One Arm Inverted Row": "روئینگ معکوس تک‌دست",
    "Archer Pull-Up": "بارفیکس کماندار",
    "Assisted Pull-Up (با کش)": "بارفیکس کمکی (با کش)",
    "Assisted Pull-Up": "بارفیکس کمکی (با کش)",
    "Jumping Pull-Up": "بارفیکس پرشی",
    "Scapular Pull-Up": "بارفیکس کتف‌محور",
    "L-Sit Pull-Up": "بارفیکس ال-سیت",
    "Ring Row": "روئینگ با رینگ",
    "Inverted Row Drop Set": "روئینگ معکوس دراپ‌ست",
    "Wide Grip Inverted Row": "روئینگ معکوس دست باز",
    "Bodyweight Row Single Arm": "روئینگ وزن بدن تک‌دست",
    "Horizontal Pull-Up with Pause": "بارفیکس افقی با توقف",
    "Pike Push-Up": "شنا پایک",
    "Handstand Push-Up": "شنا هندستند",
    "Plank to Shoulder Tap": "پلانک با تاچ شانه",
    "Dumbbell-Free Lateral Raise Simulation (با کش یا وزنه بدن)": "شبیه‌سازی نشر جانب بدون دمبل",
    "Dumbbell-Free Lateral Raise Simulation": "شبیه‌سازی نشر جانب بدون دمبل",
    "Elevated Pike Push-Up": "شنا پایک با پا روی ارتفاع",
    "Side Plank Reach Under": "پلانک پهلو با دست زیر بدن",
    "T-Push-Up": "شنا سوئدی تی",
    "Wall Walk": "راه رفتن روی دیوار",
    "Plank to Downward Dog": "پلانک به داون‌داگ",
    "Arm Circles": "چرخش دست‌ها",
    "Shoulder Taps on Knees": "تاچ شانه روی زانو",
    "Plank Reach": "پلانک با دست دراز",
    "Scapular Push-Up": "شنا کتف‌محور",
    "Side Plank Arm Lift": "پلانک پهلو با بالا بردن دست",
    "Reverse Plank Leg Lift": "پلانک معکوس با بالا بردن پا",
    "Handstand Wall Walk Hold": "نگه‌داشتن هندستند دیوار",
    "Y-T Raises (با وزن بدن یا کش)": "حرکات Y-T با وزن بدن/کش",
    "Y-T Raises": "حرکات وای-تی",
    "Plank to Side Arm Raise": "پلانک با بالا بردن دست به پهلو",
    "Shoulder Shrugs (با وزن بدن یا کش)": "شراگ شانه با وزن بدن/کش",
    "Shoulder Shrugs": "شراگ شانه",
    "Bodyweight Squat": "اسکوات وزن بدن",
    "Jump Squat": "اسکوات پرشی",
    "Lunge Forward": "لانج جلو",
    "Reverse Lunge": "لانج عقب",
    "Side Lunge": "لانج جانبی",
    "Curtsy Lunge": "لانج ضربدری",
    "Split Squat": "اسکوات اسپلیت",
    "Bulgarian Split Squat": "اسکوات اسپلیت بلغاری",
    "Step-Up (روی سطح ثابت)": "استپ‌آپ",
    "Step-Up": "استپ‌آپ",
    "Step-Up with Knee Raise": "استپ‌آپ با بالا آوردن زانو",
    "Single Leg Squat (Pistol Squat)": "اسکوات تک‌پا (پیستول)",
    "Wall Sit": "وال‌سیت",
    "Calf Raise": "ساق پا ایستاده",
    "Single Leg Calf Raise": "ساق تک‌پا",
    "Jumping Lunge": "لانج پرشی",
    "Side Step Squat": "اسکوات گام جانبی",
    "Frog Jump": "پرش قورباغه‌ای",
    "Glute Bridge": "پل باسن",
    "Single Leg Glute Bridge": "پل باسن تک‌پا",
    "Donkey Kick": "دانکی کیک",
    "Fire Hydrant": "فایر هایدرنت",
    "Side-Lying Leg Lift": "بالا بردن پای خوابیده به پهلو",
    "Clamshell": "کلَم‌شِل",
    "Sumo Squat": "اسکوات سومو",
    "Broad Jump": "پرش طول",
    "Skater Squat": "اسکوات اسکیتری",
    "Lateral Step-Up": "استپ‌آپ جانبی",
    "Curtsy Lunge Jump": "لانج ضربدری پرشی",
    "Wall Sit with Arm Raise": "وال‌سیت با بالا بردن دست",
    "Squat Hold with Pulse": "اسکوات ایزومتریک با پالس",
    "Bodyweight Biceps Curl (با کش یا حوله)": "جلو بازو وزن بدن (با کش/حوله)",
    "Bodyweight Biceps Curl": "جلو بازو وزن بدن",
    "Chin-Up Narrow Grip": "چین‌آپ دست جمع",
    "Commando Pull-Up": "بارفیکس کماندویی",
    "Inverted Row Underhand Grip": "روئینگ معکوس دست برعکس",
    "Isometric Curl Hold (با کش)": "نگه‌داشتن ایزومتریک جلو بازو (کش)",
    "Isometric Curl Hold": "نگه‌داشتن ایزومتریک جلو بازو",
    "Towel Curl (با حوله و میله)": "جلو بازو با حوله",
    "Towel Curl": "جلو بازو با حوله",
    "One Arm Chin-Up": "چین‌آپ تک‌دست",
    "Bodyweight Hammer Curl Simulation": "شبیه‌سازی جلو بازو چکشی با وزن بدن",
    "Pull-Up + Hold": "بارفیکس با نگه‌داشتن بالا",
    "Inverted Row Single Arm": "روئینگ معکوس تک‌دست",
    "Triceps Dips (روی صندلی یا سطح ثابت)": "دیپ پشت بازو روی صندلی",
    "Triceps Dips": "دیپ پشت بازو",
    "Bench Dip": "دیپ پشت بازو روی نیمکت",
    "Close Grip Push-Up": "شنا سوئدی دست جمع",
    "Overhead Triceps Extension (با کش)": "پشت بازو بالای سر با کش",
    "Overhead Triceps Extension": "پشت بازو بالای سر",
    "Bodyweight Kickback": "کیک‌بک پشت بازو با وزن بدن",
    "Triceps Push-Up on Knees": "شنا پشت بازو روی زانو",
    "Elevated Triceps Dip": "دیپ پشت بازو روی سطح بلند",
    "Close Grip Elevated Push-Up": "شنا سوئدی دست جمع روی ارتفاع",
    "Bodyweight Triceps Hold": "نگه‌داشتن ایزومتریک پشت بازو با وزن بدن",
    "Plank": "پلانک",
    "Side Plank": "پلانک پهلو",
    "Plank with Shoulder Tap": "پلانک با تاچ شانه",
    "Plank with Leg Lift": "پلانک با بالا بردن پا",
    "Mountain Climbers": "کوه‌نوردی",
    "Bicycle Crunch": "کرانچ دوچرخه‌ای",
    "Reverse Crunch": "کرانچ معکوس",
    "Flutter Kicks": "ضربه قیچی",
    "Leg Raise": "بالا آوردن پا",
    "V-Up": "وی-آپ",
    "Russian Twist": "چرخش روسی",
    "Side Plank Hip Dip": "پلانک پهلو با افت لگن",
    "Plank with Arm Reach": "پلانک با دست دراز",
    "Plank with Knee to Elbow": "پلانک زانو به آرنج",
    "Spider Plank": "پلانک عنکبوتی",
    "Hollow Body Hold": "هالو بادی هولد",
    "Side Crunch": "کرانچ پهلو",
    "Toe Touch": "لمس پنجه پا",
    "Standing Oblique Crunch": "کرانچ مورب ایستاده",
    "Plank to Side Plank": "پلانک به پلانک پهلو",
    "Lateral Step-Out Squat": "اسکوات گام به بیرون",
    "Glute Bridge March": "پل باسن مارچ",
    "Burpee": "برپی",
    "Burpee Pull-Up": "برپی بارفیکس",
    "Mountain Climber to Push-Up": "کوه‌نوردی به شنا سوئدی",
    "Jump Squat + Push-Up Combo": "اسکوات پرشی + شنا سوئدی",
    "Plank to Push-Up": "پلانک به شنا سوئدی",
    "Lunge to Knee Raise": "لانج به بالا آوردن زانو",
    "Spiderman Plank to Push-Up": "پلانک اسپایدرمن به شنا",
    "Tuck Jump": "پرش تاک",
    "Skater Jump": "پرش اسکیتری",
    "Lunge Jump + Twist": "لانج پرشی با چرخش",
    "Bear Crawl": "خزیدن خرسی",
    "Crab Walk": "راه رفتن خرچنگی",
    "Side Lunge to Reach": "لانج جانبی با دست‌درازی",
    "Plank Jacks": "جک پلانک",
    "Jumping Jack to Squat": "جامپینگ جک به اسکوات",
    "Broad Jump + Backward Walk": "پرش طول + راه رفتن عقب",
    "Single-Leg Burpee": "برپی تک‌پا",
    "Lunge Matrix": "ماتریس لانج",
    "Push-Up + Mountain Climber Superset": "شنا سوئدی + کوه‌نوردی (سوپرست)",
    "Bodyweight Biceps Curl with Towel Hold": "جلو بازو وزن بدن با نگه‌داشتن حوله",
    "Isometric Chin-Up Hold": "نگه‌داشتن ایزومتریک چین‌آپ",
    "Wide Grip Chin-Up": "چین‌آپ دست باز",
    "Close Grip Chin-Up": "چین‌آپ دست جمع",
    "Commando Pull-Up Hold": "نگه‌داشتن بارفیکس کماندویی",
    "Towel Curl + Hold": "جلو بازو با حوله + نگه‌داشتن",
    "Bodyweight Hammer Curl": "جلو بازو چکشی با وزن بدن",
    "One Arm Chin-Up Hold": "نگه‌داشتن چین‌آپ تک‌دست",
    "Inverted Row with Biceps Focus": "روئینگ معکوس با تاکید جلو بازو",
    "Chin-Up to Hold": "چین‌آپ با نگه‌داشتن بالا",
}

TARGET_KEYWORDS = [
    ("سینه بالا", "سینه بالا"),
    ("سینه پایین", "سینه پایین"),
    ("سینه وسط", "سینه میانی"),
    ("سینه", "سینه"),
    ("میان‌پشت", "میان پشت"),
    ("میان پشت", "میان پشت"),
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
    parts = [p.strip() for p in re.split(r'[،\-]\s*', text) if p.strip()]
    breath = [p for p in parts if 'دم' in p or 'بازدم' in p]
    return '، '.join(breath[:2]) if breath else ''


def _extract_fa_name_and_notes(text: str):
    if '–' in text:
        left, right = text.split('–', 1)
    elif '-' in text:
        left, right = text.split('-', 1)
    else:
        return text.strip(), ''
    return left.strip(), right.strip()

def _extract_target_detail_fa(detail: str, fa_hint: str, title: str) -> str:
    candidate = (fa_hint or '').strip()
    if candidate and all(x not in candidate for x in ['مبتدی', 'متوسط', 'حرفه‌ای']):
        return candidate
    chunk = detail.replace('،', ',').split(',', 1)[0].strip()
    if chunk and all(x not in chunk for x in ['مبتدی', 'متوسط', 'حرفه‌ای']):
        return chunk
    for key, value in TARGET_KEYWORDS:
        if key in (fa_hint or ''):
            return value
    title_fa = title.split('(')[0].replace('عضلات', '').strip()
    return title_fa

def _target_fa_to_en(text: str) -> str:
    if not text:
        return ''
    parts = [p.strip() for p in text.split(' و ') if p.strip()]
    mapped = [TARGET_FA_TO_EN.get(p, p) for p in parts]
    return ' & '.join(mapped)

def _translate_name_fa(name_en: str) -> str:
    key = name_en.strip()
    if key.endswith('('):
        key = key[:-1].strip()
    return NAME_FA.get(key, NAME_FA.get(name_en, name_en))


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
            name_en = match.group(2).strip()
            span_start = match.end()
            next_match = ITEM_RE.search(section, span_start)
            span_end = next_match.start() if next_match else len(section)
            detail = section[span_start:span_end].strip()
            detail = detail.replace('\n', ' ').replace('  ', ' ')
            fa_name_hint, notes = _extract_fa_name_and_notes(detail)
            level = _extract_level(detail)
            gender = _extract_gender(detail)
            breathing = _extract_breathing(detail)
            name_fa = _translate_name_fa(name_en)
            target_detail_fa = _extract_target_detail_fa(detail, fa_name_hint, title)
            target_detail_en = _target_fa_to_en(target_detail_fa)
            key = _normalize_name(name_en)
            if key in seen:
                continue
            seen.add(key)
            items.append({
                "index": int(idx),
                "name_en": name_en,
                "name_fa": name_fa,
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
    story.append(Paragraph(_rtl_reshape("Exercise Library – Type 2 (Functional) | کتابخانه تمرینات – حالت ۲ (فانکشنال)"), title_style))
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
        story.append(Paragraph(_rtl_reshape(group["title"]), heading_style))
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
