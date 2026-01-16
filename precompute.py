"""
연예인 히스토그램 미리 계산해서 저장
"""
import cv2
import numpy as np
import os
import json

CELEBRITY_FOLDER = os.path.join(os.path.dirname(__file__), 'celebrities')
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), 'celebrity_data.json')

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

def get_histogram(image_path):
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        return None

    # 크기 제한
    max_size = 300
    h, w = img.shape[:2]
    if max(h, w) > max_size:
        scale = max_size / max(h, w)
        img = cv2.resize(img, None, fx=scale, fy=scale)

    # 얼굴 검출
    faces = face_cascade.detectMultiScale(img, 1.1, 4)
    if len(faces) > 0:
        x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
        img = img[y:y+h, x:x+w]

    img = cv2.resize(img, (64, 64))
    hist = cv2.calcHist([img], [0], None, [32], [0, 256])
    hist = cv2.normalize(hist, hist).flatten()

    return hist.tolist()

def main():
    data = {}

    for filename in os.listdir(CELEBRITY_FOLDER):
        if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            filepath = os.path.join(CELEBRITY_FOLDER, filename)
            name = os.path.splitext(filename)[0]

            hist = get_histogram(filepath)
            if hist:
                data[name] = hist
                print(f"처리 완료: {name}")

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)

    print(f"\n총 {len(data)}명 저장됨: {OUTPUT_FILE}")

if __name__ == '__main__':
    main()
