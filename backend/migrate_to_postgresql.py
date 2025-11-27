"""
SQLite에서 PostgreSQL로 데이터 마이그레이션 스크립트

사용법:
1. .env 파일에서 PostgreSQL DATABASE_URL 설정
2. python migrate_to_postgresql.py 실행
"""
import sys
import os
from datetime import datetime

# 현재 디렉토리를 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.models import Database, CoinPrice, News
from config import Config


def migrate_data(source_db_url, target_db_url):
    """
    데이터를 한 데이터베이스에서 다른 데이터베이스로 마이그레이션합니다.

    Args:
        source_db_url (str): 소스 데이터베이스 URL (SQLite)
        target_db_url (str): 타겟 데이터베이스 URL (PostgreSQL)
    """
    print("=" * 80)
    print("데이터베이스 마이그레이션 시작")
    print("=" * 80)
    print(f"소스: {source_db_url}")
    print(f"타겟: {target_db_url[:50]}...")
    print("=" * 80)

    # 소스 데이터베이스 연결 (SQLite)
    print("\n[1] 소스 데이터베이스 연결 중...")
    source_db = Database(source_db_url)
    print("✅ 소스 연결 완료")

    # 타겟 데이터베이스 연결 (PostgreSQL)
    print("\n[2] 타겟 데이터베이스 연결 중...")
    target_db = Database(target_db_url)
    print("✅ 타겟 연결 완료")

    # 코인 가격 데이터 마이그레이션
    print("\n[3] 코인 가격 데이터 마이그레이션 중...")
    coin_prices = source_db.session.query(CoinPrice).all()
    print(f"  총 {len(coin_prices)}개의 코인 가격 레코드 발견")

    migrated_prices = 0
    failed_prices = 0

    for price in coin_prices:
        try:
            new_price = CoinPrice(
                symbol=price.symbol,
                current_price=price.current_price,
                high_price=price.high_price,
                low_price=price.low_price,
                volume=price.volume,
                price_change=price.price_change,
                price_change_percent=price.price_change_percent,
                timestamp=price.timestamp
            )
            target_db.session.add(new_price)
            migrated_prices += 1

            # 100개씩 커밋 (성능 향상)
            if migrated_prices % 100 == 0:
                target_db.session.commit()
                print(f"  진행 중... {migrated_prices}/{len(coin_prices)}")

        except Exception as e:
            failed_prices += 1
            print(f"  ⚠️  가격 데이터 마이그레이션 실패: {e}")
            target_db.session.rollback()

    # 최종 커밋
    target_db.session.commit()
    print(f"✅ 코인 가격 마이그레이션 완료: {migrated_prices}개 성공, {failed_prices}개 실패")

    # 뉴스 데이터 마이그레이션
    print("\n[4] 뉴스 데이터 마이그레이션 중...")
    news_list = source_db.session.query(News).all()
    print(f"  총 {len(news_list)}개의 뉴스 레코드 발견")

    migrated_news = 0
    failed_news = 0

    for news in news_list:
        try:
            new_news = News(
                title=news.title,
                url=news.url,
                source=news.source,
                published_at=news.published_at,
                related_coins=news.related_coins,
                timestamp=news.timestamp
            )
            target_db.session.add(new_news)
            migrated_news += 1

            # 50개씩 커밋
            if migrated_news % 50 == 0:
                target_db.session.commit()
                print(f"  진행 중... {migrated_news}/{len(news_list)}")

        except Exception as e:
            failed_news += 1
            print(f"  ⚠️  뉴스 데이터 마이그레이션 실패: {e}")
            target_db.session.rollback()

    # 최종 커밋
    target_db.session.commit()
    print(f"✅ 뉴스 마이그레이션 완료: {migrated_news}개 성공, {failed_news}개 실패")

    # 연결 종료
    source_db.close()
    target_db.close()

    # 최종 결과
    print("\n" + "=" * 80)
    print("마이그레이션 완료!")
    print("=" * 80)
    print(f"코인 가격: {migrated_prices}/{len(coin_prices)} 성공")
    print(f"뉴스: {migrated_news}/{len(news_list)} 성공")
    print("=" * 80)


def verify_migration(source_db_url, target_db_url):
    """
    마이그레이션 결과를 검증합니다.
    """
    print("\n" + "=" * 80)
    print("마이그레이션 검증 중...")
    print("=" * 80)

    source_db = Database(source_db_url)
    target_db = Database(target_db_url)

    # 코인 가격 레코드 수 비교
    source_price_count = source_db.session.query(CoinPrice).count()
    target_price_count = target_db.session.query(CoinPrice).count()

    print(f"\n[코인 가격]")
    print(f"  소스: {source_price_count}개")
    print(f"  타겟: {target_price_count}개")

    if source_price_count == target_price_count:
        print("  ✅ 레코드 수 일치")
    else:
        print(f"  ⚠️  레코드 수 불일치 (차이: {abs(source_price_count - target_price_count)}개)")

    # 뉴스 레코드 수 비교
    source_news_count = source_db.session.query(News).count()
    target_news_count = target_db.session.query(News).count()

    print(f"\n[뉴스]")
    print(f"  소스: {source_news_count}개")
    print(f"  타겟: {target_news_count}개")

    if source_news_count == target_news_count:
        print("  ✅ 레코드 수 일치")
    else:
        print(f"  ⚠️  레코드 수 불일치 (차이: {abs(source_news_count - target_news_count)}개)")

    source_db.close()
    target_db.close()

    print("\n" + "=" * 80)


if __name__ == "__main__":
    print("\n")
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 20 + "SQLite → PostgreSQL 마이그레이션" + " " * 25 + "║")
    print("╚" + "═" * 78 + "╝")
    print()

    # 현재 설정 출력
    Config.print_config()

    # 소스와 타겟 확인
    source_db_url = 'sqlite:///crypto_dashboard.db'
    target_db_url = Config.DATABASE_URL

    # SQLite에서 PostgreSQL로만 마이그레이션 가능
    if not target_db_url.startswith('postgresql'):
        print("\n❌ 오류: .env 파일의 DATABASE_URL이 PostgreSQL이 아닙니다.")
        print("\n다음 단계를 수행하세요:")
        print("1. .env 파일을 열기")
        print("2. PostgreSQL DATABASE_URL 주석 해제")
        print("3. postgres 비밀번호 입력")
        print("4. SQLite DATABASE_URL 주석 처리")
        print("\n예시:")
        print("  # DATABASE_URL=sqlite:///crypto_dashboard.db")
        print("  DATABASE_URL=postgresql://postgres:your_password@localhost:5432/crypto_db")
        sys.exit(1)

    # 사용자 확인
    print(f"\n📌 다음 마이그레이션을 진행하시겠습니까?")
    print(f"   {source_db_url}")
    print(f"   ↓")
    print(f"   {target_db_url[:60]}...")
    print()

    response = input("계속하려면 'yes'를 입력하세요: ")

    if response.lower() not in ['yes', 'y', '예']:
        print("❌ 마이그레이션이 취소되었습니다.")
        sys.exit(0)

    try:
        # 마이그레이션 실행
        migrate_data(source_db_url, target_db_url)

        # 검증
        verify_migration(source_db_url, target_db_url)

        print("\n✅ 모든 작업이 완료되었습니다!")
        print("\n다음 단계:")
        print("  1. app.py를 실행하여 PostgreSQL 연결 확인")
        print("  2. 프론트엔드에서 데이터가 정상적으로 표시되는지 확인")

    except Exception as e:
        print(f"\n❌ 마이그레이션 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
