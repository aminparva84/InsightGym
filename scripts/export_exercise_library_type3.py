"""
Parse Type 3 (combined machine + functional) exercise list, export JSON and PDF.
Run from project root: python scripts/export_exercise_library_type3.py
Outputs:
  - frontend/src/data/exerciseLibraryType3.json
  - docs/Exercise_Library_Type3.pdf
"""
import os
import json
import re

PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
OUTPUT_JSON = os.path.join(PROJECT_ROOT, "frontend", "src", "data", "exerciseLibraryType3.json")
OUTPUT_PDF = os.path.join(PROJECT_ROOT, "docs", "Exercise_Library_Type3.pdf")

RAW_TEXT = r"""
حالت ۳ – حرکات ترکیبی (دستگاه + فانکشنال)

🟥 ۱) عضلات سینه (Chest) – ۲۰ حرکت
	1.	Chest Press Machine + Push-Up – سینه، متوسط تا حرفه‌ای، دم پایین، بازدم بالا، هر دو
	2.	Incline Chest Press Machine + Incline Push-Up – سینه بالا، متوسط، دم پایین، بازدم بالا، هر دو
	3.	Cable Fly + Wide Push-Up – سینه، متوسط، دم پایین، بازدم بالا، هر دو
	4.	Pec Deck Machine + Diamond Push-Up – سینه و پشت بازو، متوسط، دم پایین، بازدم فشار، هر دو
	5.	Chest Press Machine + Clap Push-Up – سینه، حرفه‌ای، دم پایین، بازدم فشار، هر دو
	6.	Incline Cable Fly + Decline Push-Up – سینه بالا و پایین، متوسط، دم پایین، بازدم بالا، هر دو
	7.	Dumbbell-Free Chest Press Simulation (با کش) + Push-Up – سینه، متوسط، دم پایین، بازدم بالا، هر دو
	8.	Cable Crossover + Archer Push-Up – سینه و شانه، حرفه‌ای، دم پایین، بازدم فشار، هر دو
	9.	Machine Chest Press Drop Set + Push-Up Hold – سینه، حرفه‌ای، دم پایین، بازدم فشار، هر دو
	10.	Chest Press + Spiderman Push-Up – سینه و شکم، متوسط، دم پایین، بازدم بالا، هر دو
	11.	Incline Chest Press + Side Plank Push-Up – سینه بالا و شانه، متوسط، دم پایین، بازدم بالا، هر دو
	12.	Pec Deck Machine + T Push-Up – سینه و شانه، متوسط، دم پایین، بازدم بالا، هر دو
	13.	Cable Chest Press + Plyometric Push-Up – سینه، حرفه‌ای، دم پایین، بازدم فشار، هر دو
	14.	Chest Press + Plank to Push-Up – سینه و شکم، متوسط، دم پایین، بازدم بالا، هر دو
	15.	Cable Incline Press + Incline Diamond Push-Up – سینه بالا، متوسط، دم پایین، بازدم فشار، هر دو
	16.	Chest Press + Push-Up to Side Plank – سینه و پهلو، متوسط، دم پایین، بازدم بالا، هر دو
	17.	Pec Deck + Explosive Push-Up – سینه، حرفه‌ای، دم پایین، بازدم فشار، هر دو
	18.	Cable Fly + Side Plank Hip Dip – سینه و پهلو، متوسط، دم پایین، بازدم بالا، هر دو
	19.	Chest Press + Mountain Climber – سینه و شکم، متوسط، دم پایین، بازدم بالا، هر دو
	20.	Incline Chest Press + Push-Up + Jump – سینه بالا و پایین، حرفه‌ای، دم پایین، بازدم فشار، هر دو

۲) عضلات پشت (Back) – ۲۰ حرکت
	21.	Lat Pulldown Machine + Inverted Row – پشت، متوسط، دم پایین، بازدم بالا، هر دو
	22.	Seated Row Machine + Bodyweight Row – پشت، متوسط، دم پایین، بازدم بالا، هر دو
	23.	Cable Row + Pull-Up – پشت، حرفه‌ای، دم پایین، بازدم بالا، هر دو
	24.	Assisted Pull-Up Machine + Chin-Up – پشت و جلو بازو، متوسط، دم پایین، بازدم بالا، هر دو
	25.	Row Machine + Horizontal Pull-Up – پشت، متوسط، دم پایین، بازدم بالا، هر دو
	26.	Lat Pulldown + Archer Pull-Up – پشت، حرفه‌ای، دم پایین، بازدم فشار، هر دو
	27.	Cable Face Pull + Scapular Pull-Up – پشت بالا و شانه، متوسط، دم پایین، بازدم بالا، هر دو
	28.	T-Bar Row + Inverted Row Single Arm – پشت، حرفه‌ای، دم پایین، بازدم بالا، هر دو
	29.	Lat Pulldown Drop Set + Chin-Up Hold – پشت، حرفه‌ای، دم پایین، بازدم فشار، هر دو
	30.	Cable Row + Pull-Up + Hold – پشت، حرفه‌ای، دم پایین، بازدم فشار، هر دو
	31.	Machine Row + Bodyweight Kickback – پشت و پشت بازو، متوسط، دم پایین، بازدم بالا، هر دو
	32.	Assisted Pull-Up + Bear Crawl – پشت و کل بدن، متوسط، دم پایین، بازدم بالا، هر دو
	33.	Lat Pulldown + Plank to Arm Lift – پشت و شانه، متوسط، دم پایین، بازدم بالا، هر دو
	34.	Row Machine + Push-Up to Side Plank – پشت و سینه، متوسط، دم پایین، بازدم بالا، هر دو
	35.	Cable Row + Superman Hold – پشت پایین، متوسط، دم پایین، بازدم بالا، هر دو
	36.	Machine Assisted Pull-Up + Towel Curl – پشت و جلو بازو، متوسط، دم پایین، بازدم بالا، هر دو
	37.	Lat Pulldown + Side Plank Reach Under – پشت و پهلو، متوسط، دم پایین، بازدم بالا، هر دو
	38.	Row Machine + Mountain Climber – پشت و شکم، متوسط، دم پایین، بازدم بالا، هر دو
	39.	Lat Pulldown + Plank Jacks – پشت و شکم، متوسط، دم پایین، بازدم بالا، هر دو
	40.	Cable Row + Jumping Pull-Up – پشت، حرفه‌ای، دم پایین، بازدم فشار، هر دو

۳) شانه (Shoulders) – ۲۰ حرکت
	41.	Shoulder Press Machine + Pike Push-Up – شانه، متوسط تا حرفه‌ای، دم پایین، بازدم فشار، هر دو
	42.	Lateral Raise Machine + Side Plank Arm Lift – شانه جانبی و پهلو، متوسط، دم پایین، بازدم بالا، هر دو
	43.	Rear Delt Machine + Y-T Raises با وزن بدن – شانه عقب، متوسط، دم پایین، بازدم بالا، هر دو
	44.	Cable Lateral Raise + Arm Circles – شانه جانبی، مبتدی تا متوسط، دم پایین، بازدم آزاد، هر دو
	45.	Shoulder Press Machine + Elevated Pike Push-Up – شانه، متوسط، دم پایین، بازدم فشار، هر دو
	46.	Dumbbell-Free Shoulder Press Simulation (با کش) + Handstand Wall Walk – شانه، حرفه‌ای، دم پایین، بازدم فشار، هر دو
	47.	Lateral Raise Machine + Side Plank Reach Under – شانه جانبی و پهلو، متوسط، دم پایین، بازدم بالا، هر دو
	48.	Rear Delt Machine + Plank to Side Arm Raise – شانه عقب، متوسط، دم پایین، بازدم بالا، هر دو
	49.	Cable Shoulder Press + Shoulder Taps on Knees – شانه و شکم، مبتدی تا متوسط، دم پایین، بازدم بالا، هر دو
	50.	Shoulder Press Machine Drop Set + Wall Walk Hold – شانه، حرفه‌ای، دم پایین، بازدم فشار، هر دو
	51.	Lateral Raise Machine + T-Push-Up – شانه جانبی، متوسط، دم پایین، بازدم بالا، هر دو
	52.	Rear Delt Machine + Plank to Downward Dog – شانه عقب و شکم، متوسط، دم پایین، بازدم بالا، هر دو
	53.	Cable Lateral Raise + Reverse Plank Leg Lift – شانه جانبی، متوسط، دم پایین، بازدم فشار، هر دو
	54.	Shoulder Press Machine + Plank Reach – شانه، متوسط، دم پایین، بازدم بالا، هر دو
	55.	Lateral Raise Machine + Hollow Body Hold – شانه جانبی، حرفه‌ای، دم پایین، بازدم بالا، هر دو
	56.	Rear Delt Machine + Side Crunch – شانه عقب و پهلو، متوسط، دم پایین، بازدم بالا، هر دو
	57.	Cable Shoulder Press + Arm Circles – شانه، مبتدی، دم پایین، بازدم آزاد، هر دو
	58.	Shoulder Press Machine + Plank to Side Plank Rotation – شانه و شکم، متوسط، دم پایین، بازدم بالا، هر دو
	59.	Lateral Raise Machine + Shoulder Shrugs با وزن بدن – شانه فوقانی، مبتدی، دم پایین، بازدم فشار، هر دو
	60.	Rear Delt Machine + Plank Jacks – شانه عقب و شکم، متوسط، دم پایین، بازدم بالا، هر دو

🟧 ۴) پایین‌تنه / پاها (Legs) – ۳۰ حرکت
	61.	Leg Press Machine + Bodyweight Squat – چهارسر و باسن، مبتدی تا متوسط، دم پایین، بازدم بالا، هر دو
	62.	Leg Press + Jump Squat – چهارسر و باسن، متوسط تا حرفه‌ای، دم پایین، بازدم بالا، هر دو
	63.	Leg Press + Forward Lunge – چهارسر و باسن، مبتدی تا متوسط، دم پایین، بازدم بالا، هر دو
	64.	Leg Press + Reverse Lunge – چهارسر و باسن، مبتدی تا متوسط، دم پایین، بازدم بالا، هر دو
	65.	Leg Extension + Side Lunge – چهارسر، متوسط، دم پایین، بازدم بالا، هر دو
	66.	Leg Curl + Curtsy Lunge – همسترینگ و باسن، متوسط، دم پایین، بازدم بالا، هر دو
	67.	Smith Machine Squat + Split Squat – چهارسر و باسن، متوسط، دم پایین، بازدم بالا، هر دو
	68.	Smith Machine Lunge + Step-Up بدون وزنه – پایین‌تنه و باسن، متوسط، دم پایین، بازدم بالا، هر دو
	69.	Leg Press + Bulgarian Split Squat – پایین‌تنه و باسن، متوسط تا حرفه‌ای، دم پایین، بازدم بالا، هر دو
	70.	Calf Raise Machine + Single Leg Calf Raise بدون وزنه – ساق، مبتدی تا متوسط، دم پایین، بازدم فشار، هر دو
	71.	Leg Press + Side Step Squat – باسن و چهارسر، متوسط، دم پایین، بازدم بالا، هر دو
	72.	Smith Machine Squat + Frog Jump – باسن و چهارسر، متوسط تا حرفه‌ای، دم پایین، بازدم فشار، هر دو
	73.	Leg Press + Broad Jump – باسن و چهارسر، حرفه‌ای، دم پایین، بازدم فشار، هر دو
	74.	Leg Curl + Glute Bridge – همسترینگ و باسن، متوسط، دم پایین، بازدم فشار، هر دو
	75.	Leg Extension + Step-Up with Knee Raise – چهارسر و شکم، متوسط، دم پایین، بازدم بالا، هر دو
	76.	Smith Machine Hip Thrust + Donkey Kick – باسن، متوسط، دم پایین، بازدم فشار، هر دو
	77.	Leg Press + Curtsy Lunge Jump – باسن و چهارسر، حرفه‌ای، دم پایین، بازدم فشار، هر دو
	78.	Leg Press + Skater Squat – باسن و چهارسر، متوسط تا حرفه‌ای، دم پایین، بازدم بالا، هر دو
	79.	Smith Machine Lunge + Wall Sit – چهارسر و باسن، مبتدی، دم پایین، بازدم آزاد، هر دو
	80.	Leg Press + Squat Hold with Pulse – باسن و چهارسر، متوسط، دم پایین، بازدم فشار، هر دو
	81.	Leg Curl + Glute Bridge March – باسن و همسترینگ، متوسط، دم پایین، بازدم فشار، هر دو
	82.	Leg Extension + Side-Lying Leg Lift – چهارسر و باسن جانبی، مبتدی، دم پایین، بازدم بالا، هر دو
	83.	Smith Machine Split Squat + Fire Hydrant – پایین‌تنه و باسن، مبتدی تا متوسط، دم پایین، بازدم فشار، هر دو
	84.	Leg Press + Clamshell – باسن جانبی، مبتدی، دم پایین، بازدم بالا، هر دو
	85.	Smith Machine Squat + Lateral Step-Out Squat – پایین‌تنه و باسن، متوسط، دم پایین، بازدم بالا، هر دو
	86.	Leg Curl + Broad Jump + Backward Walk – همسترینگ و باسن، متوسط، دم پایین، بازدم بالا، هر دو
	87.	Leg Press + Jumping Lunge – باسن و چهارسر، حرفه‌ای، دم پایین، بازدم بالا، هر دو
	88.	Smith Machine Hip Thrust + Side Step Squat – باسن و چهارسر، متوسط، دم پایین، بازدم بالا، هر دو
	89.	Leg Press + Curtsy Lunge – باسن و چهارسر، متوسط، دم پایین، بازدم بالا، هر دو
	90.	Smith Machine Squat + Glute Bridge – باسن و چهارسر، متوسط، دم پایین، بازدم فشار، هر دو

۵) جلو بازو (Biceps) – ۱۰ حرکت
	91.	Cable Biceps Curl + Bodyweight Biceps Curl – جلو بازو، متوسط، دم پایین، بازدم بالا، هر دو
	92.	Dumbbell-Free Curl Simulation (با کش) + Chin-Up – جلو بازو و پشت، متوسط تا حرفه‌ای، دم پایین، بازدم بالا، هر دو
	93.	Preacher Curl Machine + Towel Curl – جلو بازو، متوسط، دم پایین، بازدم بالا، هر دو
	94.	Cable Hammer Curl + Bodyweight Hammer Curl – جلو بازو و ساعد، متوسط، دم پایین، بازدم بالا، هر دو
	95.	Biceps Curl Machine + Pull-Up Narrow Grip – جلو بازو و پشت، متوسط تا حرفه‌ای، دم پایین، بازدم فشار، هر دو
	96.	Cable Curl + Chin-Up Hold – جلو بازو، حرفه‌ای، توقف ۲–۳ ثانیه، دم پایین، بازدم فشار، هر دو
	97.	Dumbbell-Free Curl + Commando Pull-Up – جلو بازو و پشت، حرفه‌ای، دم پایین، بازدم فشار، هر دو
	98.	Cable Curl Drop Set + Inverted Row – جلو بازو، متوسط تا حرفه‌ای، دم پایین، بازدم بالا، هر دو
	99.	Preacher Curl Machine + Pull-Up Superset – جلو بازو و پشت، حرفه‌ای، دم پایین، بازدم فشار، هر دو
	100.	Cable Biceps Curl + Chin-Up + Hold – جلو بازو و پشت، حرفه‌ای، دم پایین، بازدم فشار، هر دو

⸻

⬛ ۶) پشت بازو (Triceps) – ۱۰ حرکت
	101.	Triceps Pushdown (Cable) + Diamond Push-Up – پشت بازو و سینه، متوسط، دم پایین، بازدم فشار، هر دو
	102.	Overhead Triceps Extension + Triceps Dips روی صندلی – پشت بازو، متوسط، دم پایین، بازدم فشار، هر دو
	103.	Triceps Kickback + Close Grip Push-Up – پشت بازو، متوسط، دم پایین، بازدم فشار، هر دو
	104.	Cable Overhead Triceps Extension + Elevated Triceps Dip – پشت بازو، متوسط، دم پایین، بازدم فشار، هر دو
	105.	Triceps Rope Pushdown + Bodyweight Triceps Hold – پشت بازو، حرفه‌ای، نگه داشتن ۵–۱۰ ثانیه، دم پایین، بازدم فشار، هر دو
	106.	Cable Pushdown + Push-Up + Shoulder Tap – پشت بازو و شانه، متوسط، دم پایین، بازدم فشار، هر دو
	107.	Overhead Triceps Extension + Close Grip Elevated Push-Up – پشت بازو، متوسط، دم پایین، بازدم فشار، هر دو
	108.	Triceps Dips Machine + Diamond Push-Up – پشت بازو، متوسط، دم پایین، بازدم فشار، هر دو
	109.	Cable Rope Pushdown Drop Set + Triceps Kickback – پشت بازو، حرفه‌ای، دم پایین، بازدم فشار، هر دو
	110.	Overhead Extension + Push-Up to Side Plank – پشت بازو و پهلو، متوسط تا حرفه‌ای، دم پایین، بازدم فشار، هر دو

۷) شکم و پهلو (Core/Abs) – ۲۰ حرکت
	111.	Cable Crunch + Plank – شکم، مبتدی تا متوسط، دم پایین، بازدم بالا، هر دو
	112.	Ab Crunch Machine + Side Plank – شکم و پهلو، مبتدی تا متوسط، دم پایین، بازدم بالا، هر دو
	113.	Cable Woodchopper + Plank with Shoulder Tap – شکم و شانه، متوسط، دم پایین، بازدم بالا، هر دو
	114.	Decline Sit-Up + Mountain Climber – شکم، متوسط، دم پایین، بازدم بالا، هر دو
	115.	Cable Side Bend + Bicycle Crunch – پهلو، متوسط، دم پایین، بازدم بالا، هر دو
	116.	Ab Roller + Reverse Crunch – شکم پایین، متوسط تا حرفه‌ای، دم پایین، بازدم بالا، هر دو
	117.	Hanging Leg Raise + Flutter Kicks – شکم پایین، متوسط تا حرفه‌ای، دم پایین، بازدم بالا، هر دو
	118.	Cable Twist + Leg Raise – شکم و پهلو، متوسط، دم پایین، بازدم بالا، هر دو
	119.	Ab Crunch Machine + V-Up – شکم، متوسط، دم پایین، بازدم بالا، هر دو
	120.	Cable Oblique Crunch + Russian Twist – پهلو، متوسط، دم پایین، بازدم بالا، هر دو
	121.	Side Plank Hip Dip + Cable Woodchopper – پهلو، متوسط، دم پایین، بازدم بالا، هر دو
	122.	Plank with Arm Reach + Cable Twist – شکم و پهلو، متوسط، دم پایین، بازدم بالا، هر دو
	123.	Mountain Climber + Cable Crunch – شکم و شانه، متوسط، دم پایین، بازدم بالا، هر دو
	124.	Side Plank + Oblique Crunch Machine – پهلو، متوسط، دم پایین، بازدم بالا، هر دو
	125.	Hanging Knee Raise + Plank to Side Plank – شکم و پهلو، متوسط، دم پایین، بازدم بالا، هر دو
	126.	Cable Reverse Crunch + Hollow Body Hold – شکم، حرفه‌ای، دم پایین، بازدم بالا، هر دو
	127.	Side Plank Reach + Cable Side Bend – پهلو، متوسط، دم پایین، بازدم بالا، هر دو
	128.	Ab Roller + Side Crunch – شکم و پهلو، متوسط، دم پایین، بازدم بالا، هر دو
	129.	Decline Sit-Up + Standing Oblique Crunch – شکم و پهلو، متوسط، دم پایین، بازدم بالا، هر دو
	130.	Plank to Side Plank + Cable Twist – شکم و پهلو، متوسط، دم پایین، بازدم بالا، هر دو

⸻

🟪 ۸) باسن و همسترینگ (Glutes/Hamstrings) – ۲۰ حرکت
	131.	Glute Bridge + Leg Curl Machine – باسن و همسترینگ، متوسط، دم پایین، بازدم فشار، هر دو
	132.	Single Leg Glute Bridge + Leg Press – باسن و چهارسر، متوسط، دم پایین، بازدم فشار، هر دو
	133.	Donkey Kick + Smith Machine Hip Thrust – باسن، متوسط، دم پایین، بازدم فشار، هر دو
	134.	Fire Hydrant + Leg Press Lateral Step – باسن جانبی، متوسط، دم پایین، بازدم بالا، هر دو
	135.	Side-Lying Leg Lift + Cable Kickback – باسن جانبی، متوسط، دم پایین، بازدم بالا، هر دو
	136.	Clamshell + Smith Machine Squat – باسن جانبی و چهارسر، متوسط، دم پایین، بازدم بالا، هر دو
	137.	Sumo Squat + Leg Press – باسن و داخل ران، متوسط، دم پایین، بازدم بالا، هر دو
	138.	Frog Jump + Leg Curl Machine – باسن و چهارسر، متوسط، دم پایین، بازدم فشار، هر دو
	139.	Broad Jump + Glute Bridge – باسن و چهارسر، حرفه‌ای، دم پایین، بازدم فشار، هر دو
	140.	Lateral Step-Out Squat + Smith Machine Split Squat – باسن و چهارسر، متوسط، دم پایین، بازدم بالا، هر دو
	141.	Curtsy Lunge + Leg Press – باسن و چهارسر، متوسط، دم پایین، بازدم بالا، هر دو
	142.	Bulgarian Split Squat + Leg Curl Machine – باسن و همسترینگ، متوسط تا حرفه‌ای، دم پایین، بازدم بالا، هر دو
	143.	Jumping Lunge + Glute Bridge March – باسن و چهارسر، حرفه‌ای، دم پایین، بازدم فشار، هر دو
	144.	Step-Up + Smith Machine Squat – باسن و چهارسر، متوسط، دم پایین، بازدم بالا، هر دو
	145.	Skater Squat + Leg Press – باسن و چهارسر، متوسط تا حرفه‌ای، دم پایین، بازدم بالا، هر دو
	146.	Wall Sit + Glute Bridge – باسن و چهارسر، مبتدی، دم پایین، بازدم آزاد، هر دو
	147.	Squat Hold with Pulse + Leg Press – باسن و چهارسر، متوسط، دم پایین، بازدم فشار، هر دو
	148.	Glute Bridge March + Cable Kickback – باسن و همسترینگ، متوسط، دم پایین، بازدم فشار، هر دو
	149.	Side Step Squat + Leg Curl Machine – باسن و چهارسر، متوسط، دم پایین، بازدم بالا، هر دو
	150.	Glute Bridge + Fire Hydrant – باسن و همسترینگ، مبتدی تا متوسط، دم پایین، بازدم فشار، هر دو

۹) حرکات پیشرفته کل بدن – ۵۰ حرکت
	151.	Burpee + Chest Press Machine – کل بدن، حرفه‌ای، دم پایین، بازدم فشار، هر دو
	152.	Mountain Climber + Cable Row – کل بدن، متوسط تا حرفه‌ای، دم پایین، بازدم بالا، هر دو
	153.	Jump Squat + Leg Press – پایین‌تنه و باسن، حرفه‌ای، دم پایین، بازدم فشار، هر دو
	154.	Push-Up + Pec Deck Machine – سینه و پشت بازو، متوسط تا حرفه‌ای، دم پایین، بازدم فشار، هر دو
	155.	Lunge + Smith Machine Squat – پایین‌تنه و باسن، متوسط تا حرفه‌ای، دم پایین، بازدم بالا، هر دو
	156.	Plank + Cable Woodchopper – شکم و پهلو، متوسط، دم پایین، بازدم بالا، هر دو
	157.	Side Plank + Lateral Raise Machine – شانه و پهلو، متوسط، دم پایین، بازدم بالا، هر دو
	158.	Jumping Lunge + Leg Curl Machine – باسن و همسترینگ، حرفه‌ای، دم پایین، بازدم فشار، هر دو
	159.	Burpee + Cable Biceps Curl – جلو بازو و کل بدن، متوسط تا حرفه‌ای، دم پایین، بازدم بالا، هر دو
	160.	Push-Up + Overhead Triceps Extension – پشت بازو و سینه، متوسط، دم پایین، بازدم فشار، هر دو
	161.	Squat + Cable Lateral Raise – شانه و پایین‌تنه، متوسط، دم پایین، بازدم بالا، هر دو
	162.	Plank to Push-Up + Leg Press – کل بدن، متوسط، دم پایین، بازدم بالا، هر دو
	163.	Cable Row + Inverted Row + Mountain Climber – پشت و شکم، متوسط، دم پایین، بازدم بالا، هر دو
	164.	Chest Press + Push-Up + Jump – سینه و کل بدن، حرفه‌ای، دم پایین، بازدم فشار، هر دو
	165.	Leg Press + Jumping Lunge + Glute Bridge – پایین‌تنه و باسن، حرفه‌ای، دم پایین، بازدم فشار، هر دو
	166.	Cable Woodchopper + Plank with Arm Reach – شکم و پهلو، متوسط، دم پایین، بازدم بالا، هر دو
	167.	Push-Up + Cable Triceps Pushdown – پشت بازو و سینه، متوسط، دم پایین، بازدم فشار، هر دو
	168.	Burpee + Pull-Up + Leg Press – کل بدن، حرفه‌ای، دم پایین، بازدم فشار، هر دو
	169.	Side Lunge + Cable Kickback – باسن و چهارسر، متوسط، دم پایین، بازدم بالا، هر دو
	170.	Plank + Push-Up + Mountain Climber – شکم، شانه، سینه، متوسط، دم پایین، بازدم بالا، هر دو
	171.	Jump Squat + Side Plank Reach Under – پایین‌تنه و پهلو، متوسط، دم پایین، بازدم بالا، هر دو
	172.	Cable Chest Press + Push-Up + Side Plank – سینه و شکم، متوسط، دم پایین، بازدم بالا، هر دو
	173.	Leg Press + Glute Bridge March – پایین‌تنه و باسن، متوسط، دم پایین، بازدم فشار، هر دو
	174.	Dumbbell-Free Shoulder Press Simulation (کش) + Plank to Shoulder Tap – شانه و شکم، متوسط، دم پایین، بازدم بالا، هر دو
	175.	Burpee + Cable Side Bend – کل بدن، متوسط، دم پایین، بازدم بالا، هر دو
	176.	Mountain Climber + Cable Crunch + Plank – شکم و کل بدن، متوسط، دم پایین، بازدم بالا، هر دو
	177.	Jumping Lunge + T-Push-Up – پایین‌تنه و شانه، متوسط، دم پایین، بازدم بالا، هر دو
	178.	Side Step Squat + Cable Biceps Curl – پایین‌تنه و جلو بازو، متوسط، دم پایین، بازدم بالا، هر دو
	179.	Smith Machine Squat + Burpee + Push-Up – پایین‌تنه و کل بدن، حرفه‌ای، دم پایین، بازدم فشار، هر دو
	180.	Plank to Side Plank + Cable Row – شکم، پهلو، پشت، متوسط، دم پایین، بازدم بالا، هر دو
	181.	Jump Squat + Overhead Triceps Extension – باسن و پشت بازو، متوسط، دم پایین، بازدم فشار، هر دو
	182.	Lunge + Push-Up + Cable Lateral Raise – پایین‌تنه، شانه، سینه، متوسط، دم پایین، بازدم بالا، هر دو
	183.	Plank + Mountain Climber + Leg Press – شکم و پایین‌تنه، متوسط، دم پایین، بازدم بالا، هر دو
	184.	Cable Woodchopper + Side Plank Hip Dip – شکم و پهلو، متوسط، دم پایین، بازدم بالا، هر دو
	185.	Burpee + Dumbbell-Free Curl Simulation – کل بدن و جلو بازو، متوسط، دم پایین، بازدم بالا، هر دو
	186.	Push-Up + Cable Triceps Pushdown + Plank – پشت بازو، سینه و شکم، متوسط، دم پایین، بازدم بالا، هر دو
	187.	Squat + Jumping Lunge + Side Step Squat – پایین‌تنه و باسن، حرفه‌ای، دم پایین، بازدم فشار، هر دو
	188.	Plank + Cable Row + Shoulder Taps – شکم و پشت، متوسط، دم پایین، بازدم بالا، هر دو
	189.	Jump Squat + Side Plank + Cable Kickback – پایین‌تنه، باسن و پهلو، متوسط، دم پایین، بازدم بالا، هر دو
	190.	Burpee + Leg Press + Glute Bridge – کل بدن و باسن، حرفه‌ای، دم پایین، بازدم فشار، هر دو
	191.	Mountain Climber + Plank with Arm/Leg Lift – شکم و شانه، متوسط، دم پایین، بازدم بالا، هر دو
	192.	Push-Up + Cable Fly + Side Plank – سینه و پهلو، متوسط، دم پایین، بازدم بالا، هر دو
	193.	Squat + Jumping Lunge + Cable Side Bend – پایین‌تنه و شکم، متوسط، دم پایین، بازدم بالا، هر دو
	194.	Plank to Push-Up + Cable Woodchopper – شکم و کل بدن، متوسط، دم پایین، بازدم بالا، هر دو
	195.	Jumping Lunge + Shoulder Press Machine – پایین‌تنه و شانه، متوسط، دم پایین، بازدم بالا، هر دو
	196.	Side Plank + Cable Chest Press + Push-Up – پهلو و سینه، متوسط، دم پایین، بازدم بالا، هر دو
	197.	Leg Press + Burpee + Tuck Jump – پایین‌تنه و باسن، حرفه‌ای، دم پایین، بازدم فشار، هر دو
	198.	Plank + Side Plank Hip Dip + Cable Twist – شکم و پهلو، متوسط، دم پایین، بازدم بالا، هر دو
	199.	Jump Squat + Burpee + Mountain Climber – پایین‌تنه و کل بدن، حرفه‌ای، دم پایین، بازدم فشار، هر دو
	200.	Push-Up + Cable Row + Side Plank Reach – سینه، پشت و پهلو، متوسط، دم پایین، بازدم بالا، هر دو
"""

GROUP_RE = re.compile(r'^[🟥🟦🟩🟧🟪🟫⬛🟨]?\s*\d+\)\s*(.*?)\s*–\s*\d+\s*حرکت', re.M)
ITEM_RE = re.compile(r'^\s*(\d+)\.\s*([A-Za-z0-9\-\(\)\/\+\s°]+)', re.M)

NAME_FA_COMPONENTS = {
    "Chest Press Machine": "پرس سینه دستگاه",
    "Incline Chest Press Machine": "پرس بالاسینه دستگاه",
    "Incline Push-Up": "شنا سوئدی شیب مثبت",
    "Cable Fly": "فلای سیمکش",
    "Wide Push-Up": "شنا سوئدی دست باز",
    "Pec Deck Machine": "پک‌دک دستگاه",
    "Diamond Push-Up": "شنا سوئدی الماسی",
    "Clap Push-Up": "شنا سوئدی انفجاری با کف‌زنی",
    "Incline Cable Fly": "فلای سیمکش بالا سینه",
    "Decline Push-Up": "شنا سوئدی شیب منفی",
    "Dumbbell-Free Chest Press Simulation (با کش)": "پرس سینه با کش",
    "Dumbbell-Free Chest Press Simulation": "پرس سینه با کش",
    "Cable Crossover": "کراس‌اوور سیمکش",
    "Archer Push-Up": "شنا سوئدی کماندار",
    "Machine Chest Press Drop Set": "پرس سینه دستگاه دراپ‌ست",
    "Push-Up Hold": "نگه‌داشتن شنا سوئدی",
    "Chest Press": "پرس سینه",
    "Incline Chest Press": "پرس بالاسینه",
    "Spiderman Push-Up": "شنا سوئدی اسپایدرمن",
    "Side Plank Push-Up": "شنا سوئدی پلانک پهلو",
    "T Push-Up": "شنا سوئدی تی",
    "T-Push-Up": "شنا سوئدی تی",
    "Cable Chest Press": "پرس سینه سیمکش",
    "Plyometric Push-Up": "شنا سوئدی پلیومتریک",
    "Plank to Push-Up": "پلانک به شنا سوئدی",
    "Cable Incline Press": "پرس بالا سینه سیمکش",
    "Incline Diamond Push-Up": "شنا سوئدی الماسی شیب مثبت",
    "Push-Up to Side Plank": "شنا سوئدی به پلانک پهلو",
    "Pec Deck": "پک‌دک",
    "Explosive Push-Up": "شنا سوئدی انفجاری",
    "Side Plank Hip Dip": "پلانک پهلو با افت لگن",
    "Mountain Climber": "کوه‌نوردی",
    "Push-Up": "شنا سوئدی",
    "Jump": "پرش",
    "Lat Pulldown Machine": "لت پول‌داون دستگاه",
    "Inverted Row": "روئینگ معکوس",
    "Seated Row Machine": "قایقی دستگاه نشسته",
    "Bodyweight Row": "روئینگ وزن بدن",
    "Cable Row": "روئینگ سیمکش",
    "Pull-Up": "بارفیکس",
    "Hold": "نگه‌داشتن",
    "Assisted Pull-Up": "بارفیکس کمکی",
    "Assisted Pull-Up Machine": "بارفیکس کمکی دستگاه",
    "Chin-Up": "چین‌آپ",
    "Row Machine": "روئینگ دستگاه",
    "Horizontal Pull-Up": "بارفیکس افقی",
    "Lat Pulldown": "لت پول‌داون",
    "Archer Pull-Up": "بارفیکس کماندار",
    "Cable Face Pull": "فیس‌پول سیمکش",
    "Scapular Pull-Up": "بارفیکس کتف‌محور",
    "T-Bar Row": "تی‌بار رو",
    "Inverted Row Single Arm": "روئینگ معکوس تک‌دست",
    "Lat Pulldown Drop Set": "لت پول‌داون دراپ‌ست",
    "Chin-Up Hold": "نگه‌داشتن چین‌آپ",
    "Pull-Up + Hold": "بارفیکس با نگه‌داشتن",
    "Machine Row": "روئینگ دستگاه",
    "Bodyweight Kickback": "کیک‌بک وزن بدن",
    "Bear Crawl": "خزیدن خرسی",
    "Plank to Arm Lift": "پلانک با بالا بردن دست",
    "Superman Hold": "نگه‌داشتن سوپرمن",
    "Machine Assisted Pull-Up": "بارفیکس کمکی دستگاه",
    "Towel Curl": "جلو بازو با حوله",
    "Side Plank Reach Under": "پلانک پهلو با دست زیر بدن",
    "Shoulder Tap": "تاچ شانه",
    "Shoulder Taps": "تاچ شانه",
    "Plank Jacks": "جک پلانک",
    "Jumping Pull-Up": "بارفیکس پرشی",
    "Shoulder Press Machine": "پرس شانه دستگاه",
    "Pike Push-Up": "شنا پایک",
    "Lateral Raise Machine": "نشر جانب دستگاه",
    "Side Plank Arm Lift": "پلانک پهلو با بالا بردن دست",
    "Rear Delt Machine": "دلتوئید خلفی دستگاه",
    "Y-T Raises با وزن بدن": "حرکات وای-تی با وزن بدن",
    "Y-T Raises": "حرکات وای-تی",
    "Cable Lateral Raise": "نشر جانب سیمکش",
    "Arm Circles": "چرخش دست‌ها",
    "Elevated Pike Push-Up": "شنا پایک با پا روی ارتفاع",
    "Dumbbell-Free Shoulder Press Simulation (با کش)": "پرس شانه با کش",
    "Dumbbell-Free Shoulder Press Simulation": "پرس شانه با کش",
    "Handstand Wall Walk": "راه رفتن هندستند روی دیوار",
    "Plank to Side Arm Raise": "پلانک با بالا بردن دست به پهلو",
    "Cable Shoulder Press": "پرس شانه سیمکش",
    "Shoulder Taps on Knees": "تاچ شانه روی زانو",
    "Shoulder Press Machine Drop Set": "پرس شانه دستگاه دراپ‌ست",
    "Wall Walk Hold": "نگه‌داشتن وال‌واک",
    "Plank to Downward Dog": "پلانک به داون‌داگ",
    "Plank to Side Plank": "پلانک به پلانک پهلو",
    "Reverse Plank Leg Lift": "پلانک معکوس با بالا بردن پا",
    "Plank Reach": "پلانک با دست دراز",
    "Hollow Body Hold": "هالو بادی هولد",
    "Side Crunch": "کرانچ پهلو",
    "Plank to Side Plank Rotation": "چرخش پلانک به پلانک پهلو",
    "Shoulder Shrugs با وزن بدن": "شراگ شانه با وزن بدن",
    "Shoulder Shrugs": "شراگ شانه",
    "Leg Press Machine": "پرس پا دستگاه",
    "Bodyweight Squat": "اسکوات وزن بدن",
    "Leg Press": "پرس پا",
    "Sumo Squat": "اسکوات سومو",
    "Jump Squat": "اسکوات پرشی",
    "Forward Lunge": "لانج جلو",
    "Reverse Lunge": "لانج عقب",
    "Leg Extension": "جلو پا دستگاه",
    "Side Lunge": "لانج جانبی",
    "Leg Curl": "پشت پا دستگاه",
    "Leg Curl Machine": "پشت پا دستگاه",
    "Curtsy Lunge": "لانج ضربدری",
    "Smith Machine Squat": "اسکوات اسمیت",
    "Split Squat": "اسکوات اسپلیت",
    "Smith Machine Lunge": "لانج اسمیت",
    "Step-Up بدون وزنه": "استپ‌آپ بدون وزنه",
    "Bulgarian Split Squat": "اسکوات اسپلیت بلغاری",
    "Calf Raise Machine": "ساق پا دستگاه",
    "Single Leg Calf Raise بدون وزنه": "ساق تک‌پا بدون وزنه",
    "Single Leg Calf Raise": "ساق تک‌پا",
    "Side Step Squat": "اسکوات گام جانبی",
    "Frog Jump": "پرش قورباغه‌ای",
    "Broad Jump": "پرش طول",
    "Glute Bridge": "پل باسن",
    "Step-Up with Knee Raise": "استپ‌آپ با بالا آوردن زانو",
    "Smith Machine Hip Thrust": "هیپ تراست اسمیت",
    "Donkey Kick": "دانکی کیک",
    "Curtsy Lunge Jump": "لانج ضربدری پرشی",
    "Skater Squat": "اسکوات اسکیتری",
    "Wall Sit": "وال‌سیت",
    "Squat Hold with Pulse": "اسکوات ایزومتریک با پالس",
    "Glute Bridge March": "پل باسن مارچ",
    "Side-Lying Leg Lift": "بالا بردن پای خوابیده به پهلو",
    "Fire Hydrant": "فایر هایدرنت",
    "Clamshell": "کلَم‌شِل",
    "Lateral Step-Out Squat": "اسکوات گام به بیرون",
    "Jumping Lunge": "لانج پرشی",
    "Cable Biceps Curl": "جلو بازو سیمکش",
    "Bodyweight Biceps Curl": "جلو بازو وزن بدن",
    "Dumbbell-Free Curl Simulation (با کش)": "جلو بازو با کش",
    "Dumbbell-Free Curl Simulation": "جلو بازو با کش",
    "Dumbbell-Free Curl": "جلو بازو با کش",
    "Preacher Curl Machine": "جلو بازو لاری دستگاه",
    "Cable Hammer Curl": "جلو بازو چکشی سیمکش",
    "Bodyweight Hammer Curl": "جلو بازو چکشی وزن بدن",
    "Biceps Curl Machine": "جلو بازو دستگاه",
    "Pull-Up Narrow Grip": "بارفیکس دست جمع",
    "Cable Curl": "جلو بازو سیمکش",
    "Chin-Up Hold": "نگه‌داشتن چین‌آپ",
    "Commando Pull-Up": "بارفیکس کماندویی",
    "Cable Curl Drop Set": "جلو بازو سیمکش دراپ‌ست",
    "Pull-Up Superset": "سوپرست بارفیکس",
    "Triceps Pushdown (Cable)": "پشت بازو سیمکش",
    "Overhead Triceps Extension": "پشت بازو بالای سر",
    "Triceps Dips روی صندلی": "دیپ پشت بازو روی صندلی",
    "Triceps Dips": "دیپ پشت بازو",
    "Triceps Kickback": "کیک‌بک پشت بازو",
    "Close Grip Push-Up": "شنا سوئدی دست جمع",
    "Cable Overhead Triceps Extension": "پشت بازو بالای سر سیمکش",
    "Elevated Triceps Dip": "دیپ پشت بازو روی سطح بلند",
    "Triceps Rope Pushdown": "پشت بازو طناب سیمکش",
    "Bodyweight Triceps Hold": "نگه‌داشتن پشت بازو با وزن بدن",
    "Cable Pushdown": "پشت بازو سیمکش",
    "Cable Triceps Pushdown": "پشت بازو سیمکش",
    "Push-Up + Shoulder Tap": "شنا سوئدی + تاچ شانه",
    "Close Grip Elevated Push-Up": "شنا سوئدی دست جمع روی ارتفاع",
    "Triceps Dips Machine": "دیپ پشت بازو دستگاه",
    "Cable Rope Pushdown Drop Set": "پشت بازو طناب سیمکش دراپ‌ست",
    "Overhead Extension": "پشت بازو بالای سر",
    "Cable Crunch": "کرانچ سیمکش",
    "Plank": "پلانک",
    "Ab Crunch Machine": "کرانچ دستگاه",
    "Side Plank": "پلانک پهلو",
    "Cable Woodchopper": "وودچاپر سیمکش",
    "Plank with Shoulder Tap": "پلانک با تاچ شانه",
    "Plank with Arm/Leg Lift": "پلانک با بالا بردن دست/پا",
    "Decline Sit-Up": "درازونشست شیب منفی",
    "Cable Side Bend": "خم جانب سیمکش",
    "Cable Reverse Crunch": "کرانچ معکوس سیمکش",
    "Bicycle Crunch": "کرانچ دوچرخه‌ای",
    "Ab Roller": "رول‌آوت شکم",
    "Reverse Crunch": "کرانچ معکوس",
    "Hanging Leg Raise": "بالا آوردن پا آویزان",
    "Flutter Kicks": "ضربه قیچی",
    "Cable Twist": "چرخش سیمکش",
    "Leg Raise": "بالا آوردن پا",
    "V-Up": "وی-آپ",
    "Cable Oblique Crunch": "کرانچ مورب سیمکش",
    "Russian Twist": "چرخش روسی",
    "Side Plank Hip Dip": "پلانک پهلو با افت لگن",
    "Plank with Arm Reach": "پلانک با دست دراز",
    "Oblique Crunch Machine": "کرانچ مورب دستگاه",
    "Hanging Knee Raise": "بالا آوردن زانو آویزان",
    "Hollow Body Hold": "هالو بادی هولد",
    "Side Plank Reach": "پلانک پهلو با دست دراز",
    "Side Crunch": "کرانچ پهلو",
    "Standing Oblique Crunch": "کرانچ مورب ایستاده",
    "Glute Bridge + Leg Curl Machine": "پل باسن + پشت پا دستگاه",
    "Glute Bridge March + Cable Kickback": "پل باسن مارچ + کیک‌بک سیمکش",
    "Leg Curl Machine": "پشت پا دستگاه",
    "Single Leg Glute Bridge": "پل باسن تک‌پا",
    "Donkey Kick": "دانکی کیک",
    "Leg Press Lateral Step": "پرس پا گام جانبی",
    "Cable Kickback": "کیک‌بک سیمکش",
    "Smith Machine Split Squat": "اسکوات اسپلیت اسمیت",
    "Step-Up": "استپ‌آپ",
    "Skater Squat": "اسکوات اسکیتری",
    "Squat": "اسکوات",
    "Lunge": "لانج",
    "Backward Walk": "راه رفتن عقب",
    "Tuck Jump": "پرش تاک",
    "Burpee": "برپی",
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

def _translate_component(name_en: str) -> str:
    key = name_en.strip()
    if key.endswith('('):
        key = key[:-1].strip()
    return NAME_FA_COMPONENTS.get(key, NAME_FA_COMPONENTS.get(name_en, name_en))

def _translate_name_fa(name_en: str) -> str:
    parts = [p.strip() for p in name_en.split('+')]
    translated = [_translate_component(p) for p in parts]
    return " + ".join(translated)


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

    def _cell_fa(text: str) -> 'Paragraph':
        return Paragraph(_rtl_reshape(text or ''), body_style)

    def _cell_en_fa(en: str, fa: str) -> 'Paragraph':
        fa_rtl = _rtl_reshape(fa or '')
        combo = f"EN: {en or ''}<br/>FA: {fa_rtl}"
        return Paragraph(combo, body_style)

    story = []
    story.append(Paragraph(_rtl_reshape("Exercise Library – Type 3 (Hybrid) | کتابخانه تمرینات – حالت ۳ (ترکیبی)"), title_style))
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
