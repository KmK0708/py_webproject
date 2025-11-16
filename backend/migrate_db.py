"""
데이터베이스 마이그레이션 스크립트
기존 news 테이블에 related_coins 컬럼을 추가합니다.
"""
import sqlite3
import os

DB_PATH = 'crypto_dashboard.db'

def migrate_database():
    """뉴스 테이블에 related_coins 컬럼 추가"""

    if not os.path.exists(DB_PATH):
        print(f"❌ 데이터베이스 파일을 찾을 수 없습니다: {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # 테이블 정보 확인
        cursor.execute("PRAGMA table_info(news)")
        columns = [row[1] for row in cursor.fetchall()]

        print("현재 news 테이블 컬럼:", columns)

        # related_coins 컬럼이 없으면 추가
        if 'related_coins' not in columns:
            print("\n✅ related_coins 컬럼 추가 중...")
            cursor.execute("ALTER TABLE news ADD COLUMN related_coins VARCHAR(200)")
            conn.commit()
            print("✅ related_coins 컬럼 추가 완료!")
        else:
            print("\n✓ related_coins 컬럼이 이미 존재합니다.")

        # URL에 인덱스 추가 (이미 있으면 무시됨)
        try:
            cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_news_url ON news(url)")
            conn.commit()
            print("✅ URL 인덱스 추가 완료!")
        except Exception as e:
            print(f"⚠️ 인덱스 추가 건너뛰기: {e}")

        # 마이그레이션 후 컬럼 확인
        cursor.execute("PRAGMA table_info(news)")
        columns = [row[1] for row in cursor.fetchall()]
        print("\n마이그레이션 후 컬럼:", columns)

        print("\n" + "=" * 60)
        print("✅ 데이터베이스 마이그레이션 완료!")
        print("=" * 60)

    except Exception as e:
        print(f"❌ 마이그레이션 오류: {e}")
        conn.rollback()

    finally:
        conn.close()

if __name__ == "__main__":
    print("=" * 60)
    print("데이터베이스 마이그레이션 시작")
    print("=" * 60)
    migrate_database()
