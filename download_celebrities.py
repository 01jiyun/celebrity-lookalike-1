"""
유명인 사진 다운로드 스크립트
"""

from icrawler.builtin import BingImageCrawler
import os

# 다운로드할 유명인 목록
CELEBRITIES = [
    # 인플루언서/유튜버
    "침착맨 얼굴",
    "이사배 뷰티",
    "풍자 유튜버",
    "김계란 핏블리",
    "쯔양 먹방",
    "히밥 먹방",
    "햄연지 유튜버",
    "회사원A 유튜버",
    "곽튜브 유튜버",
    "빠니보틀 유튜버",

    # 정치인
    "윤석열 대통령",
    "이재명 대표",
    "한동훈 대표",
    "김건희 여사",
    "오바마 대통령",
    "트럼프 대통령",
    "일론머스크",

    # 개그맨/코미디언
    "유재석 MC",
    "강호동 MC",
    "신동엽 MC",
    "이경규 개그맨",
    "박명수 MC",
    "김구라 MC",
    "조세호 개그맨",
    "양세찬 개그맨",
    "이수근 개그맨",
    "김희철 MC",
    "전현무 MC",

    # 가수
    "아이유 가수",
    "임영웅 가수",
    "이찬원 가수",
    "박효신 가수",
    "성시경 가수",
    "태연 소녀시대",
    "아이린 레드벨벳",
    "제니 블랙핑크",
    "지수 블랙핑크",
    "로제 블랙핑크",
    "리사 블랙핑크",
    "지드래곤 빅뱅",
    "뷔 BTS",
    "정국 BTS",
    "지민 BTS",

    # 배우
    "마동석 배우",
    "황정민 배우",
    "송중기 배우",
    "이병헌 배우",
    "정우성 배우",
    "하정우 배우",
    "조인성 배우",
    "이민호 배우",
    "김수현 배우",
    "송혜교 배우",
    "전도연 배우",
    "김혜수 배우",
    "이영애 배우",
    "한가인 배우",

    # 스포츠
    "손흥민 축구",
    "김연아 피겨",
    "류현진 야구",
    "이강인 축구",
]

# 저장 경로
SAVE_PATH = os.path.join(os.path.dirname(__file__), 'celebrities')

def download_celebrity_images():
    for celeb in CELEBRITIES:
        print(f"\n{'='*50}")
        print(f"다운로드 중: {celeb}")
        print('='*50)

        # 임시 폴더에 다운로드
        temp_folder = os.path.join(SAVE_PATH, '_temp')
        os.makedirs(temp_folder, exist_ok=True)

        # Bing 크롤러 설정
        crawler = BingImageCrawler(
            storage={'root_dir': temp_folder},
            downloader_threads=2,
        )

        # 1장만 다운로드
        crawler.crawl(
            keyword=celeb,
            max_num=1,
            min_size=(200, 200),
        )

        # 다운로드된 파일 이름 변경
        for filename in os.listdir(temp_folder):
            old_path = os.path.join(temp_folder, filename)
            ext = os.path.splitext(filename)[1]
            if not ext:
                ext = '.jpg'

            # 이름 정리 (첫 단어만 사용)
            clean_name = celeb.split()[0]
            new_path = os.path.join(SAVE_PATH, f"{clean_name}{ext}")

            if os.path.exists(new_path):
                os.remove(new_path)

            os.rename(old_path, new_path)
            print(f"저장 완료: {clean_name}{ext}")

        try:
            os.rmdir(temp_folder)
        except:
            pass

    print(f"\n{'='*50}")
    print("모든 다운로드 완료!")
    print(f"총 {len(CELEBRITIES)}명 저장됨")
    print(f"저장 위치: {SAVE_PATH}")
    print('='*50)

if __name__ == '__main__':
    download_celebrity_images()
