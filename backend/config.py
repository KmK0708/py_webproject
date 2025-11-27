"""
환경 변수 및 설정 관리
"""
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()


class Config:
    """애플리케이션 설정 클래스"""

    # 데이터베이스 설정
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///crypto_dashboard.db')

    # Flask 설정
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'

    # API 키 (선택사항)
    BINANCE_API_KEY = os.getenv('BINANCE_API_KEY')
    BINANCE_API_SECRET = os.getenv('BINANCE_API_SECRET')

    @staticmethod
    def get_database_type():
        """현재 사용 중인 데이터베이스 타입 반환"""
        db_url = Config.DATABASE_URL
        if db_url.startswith('postgresql'):
            return 'postgresql'
        elif db_url.startswith('sqlite'):
            return 'sqlite'
        else:
            return 'unknown'

    @staticmethod
    def print_config():
        """현재 설정 출력 (디버깅용)"""
        print("=" * 60)
        print("현재 설정:")
        print("=" * 60)
        print(f"데이터베이스 타입: {Config.get_database_type()}")
        print(f"DATABASE_URL: {Config.DATABASE_URL[:50]}...")
        print(f"FLASK_ENV: {Config.FLASK_ENV}")
        print(f"FLASK_DEBUG: {Config.FLASK_DEBUG}")
        print("=" * 60)


if __name__ == "__main__":
    # 테스트
    Config.print_config()
