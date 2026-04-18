from collections import defaultdict
import os, glob
from datetime import datetime

INPUT_FOLDER = "/Users/ggtcha/projectocr/data"

all_images = glob.glob(os.path.join(INPUT_FOLDER, "*.jpg"))

# หา unique mtime ทั้งหมด
unique_times = sorted(set(
    datetime.fromtimestamp(os.path.getmtime(p)).strftime("%H:%M")
    for p in all_images
))

print(f"พบ {len(unique_times)} sets: {unique_times}")

# แยกแต่ละ set
sets = defaultdict(list)
for path in all_images:
    hhmm = datetime.fromtimestamp(os.path.getmtime(path)).strftime("%H:%M")
    sets[hhmm].append(path)

for t, files in sorted(sets.items()):
    print(f"\nSet {t} — {len(files)} ภาพ")
    for f in sorted(files):
        print(f"  {os.path.basename(f)}")