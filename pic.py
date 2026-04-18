from PIL import Image
import os, glob
from collections import defaultdict
from datetime import datetime

INPUT_FOLDER  = "/Users/ggtcha/projectocr/data"
OUTPUT_FOLDER = "/Users/ggtcha/projectocr/strips"
GAP = 2

# สร้าง output folder ถ้ายังไม่มี
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# หาไฟล์ .jpg ทั้งหมดใน input folder
all_images = glob.glob(os.path.join(INPUT_FOLDER, "*.jpg"))

# แยกไฟล์เป็นกลุ่มตาม modified time (HH:MM)
# ไฟล์ที่กล้องบันทึกเวลาเดียวกัน = set เดียวกัน
sets = defaultdict(list)
for path in all_images:
    hhmm = datetime.fromtimestamp(os.path.getmtime(path)).strftime("%H:%M")
    sets[hhmm].append(path)

def make_strips(images, prefix):
    # เรียงภาพตาม parts[2] (ลำดับ 01, 02, 03...)
    images = sorted(images, key=lambda p: os.path.splitext(os.path.basename(p))[0].split("_")[2])

    # หา strip ที่ทำไปแล้ว เพื่อ resume ได้
    done_indices = set()
    for f in glob.glob(os.path.join(OUTPUT_FOLDER, f"{prefix}_*.jpg")):
        idx = int(os.path.splitext(os.path.basename(f))[0].split("_")[1])
        done_indices.add(idx)

    saved = skipped = 0
    for i in range(0, len(images), 5):
        batch = images[i:i+5]
        if len(batch) == 0:
            break

        strip_idx = i // 5

        # ถ้า strip นี้ทำไปแล้วข้ามได้เลย
        if strip_idx in done_indices:
            skipped += 1
            continue

        # เปิดภาพและแปลงเป็น RGB
        try:
            imgs = [Image.open(p).convert('RGB') for p in batch]
        except Exception as e:
            print(f"  ข้าม {prefix}_{strip_idx:04d}: {e}")
            continue

        # รองรับทั้ง 5 ภาพ และ 4 ภาพ (ชุดสุดท้ายที่ไม่ครบ)
        w, h = imgs[0].size
        strip = Image.new('RGB', (w*len(imgs) + GAP*(len(imgs)-1), h), (0, 0, 0))

        # วางภาพแต่ละรูปเรียงแนวนอน โดยมี gap 2px คั่น
        for j, img in enumerate(imgs):
            strip.paste(img, (j*(w+GAP), 0))

        # บันทึกไฟล์ เช่น set1_0000.jpg, set1_0001.jpg
        out = os.path.join(OUTPUT_FOLDER, f"{prefix}_{strip_idx:04d}.jpg")
        strip.save(out, quality=95)
        saved += 1
        print(f"  บันทึก {prefix}_{strip_idx:04d} ({len(imgs)} ภาพ)")

    print(f"  สรุป -- บันทึก {saved} | ข้าม {skipped}")

# วนทำ strip แต่ละ set ตามเวลา
# set1 = เวลาน้อยสุด, set2, set3 ตามลำดับ
for i, (hhmm, images) in enumerate(sorted(sets.items()), start=1):
    print(f"\nSet {i} ({hhmm}) -- {len(images)} ภาพ")
    make_strips(images, f"set{i}")

print("\nเสร็จแล้ว")