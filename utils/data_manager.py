import pandas as pd
import os
from datetime import datetime
import json

# 데이터 디렉토리 경로
DATA_DIR = "data"
PRODUCTS_FILE = os.path.join(DATA_DIR, "products.csv")
SALES_FILE = os.path.join(DATA_DIR, "sales.csv")
NOTIFICATIONS_FILE = os.path.join(DATA_DIR, "notifications.json")

def ensure_data_dir():
    """데이터 디렉토리가 없으면 생성"""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

def init_products_file():
    """상품 데이터 파일 초기화"""
    ensure_data_dir()
    if not os.path.exists(PRODUCTS_FILE):
        # 샘플 데이터 생성
        sample_data = {
            'id': [1, 2, 3, 4, 5],
            'name': ['새우깡', '초코파이', '오징어땅콩', '콜라', '사이다'],
            'category': ['과자', '과자', '과자', '음료', '음료'],
            'price': [1500, 2000, 1800, 1200, 1200],
            'stock': [10, 5, 0, 15, 20],
            'ingredients': [
                '밀가루, 새우, 식물성유지, 설탕, 소금',
                '밀가루, 설탕, 코코아, 식물성유지',
                '땅콩, 오징어, 설탕, 소금',
                '탄산수, 설탕, 카라멜색소',
                '탄산수, 설탕, 구연산'
            ],
            'allergens': [
                '밀, 새우',
                '밀, 우유',
                '땅콩, 오징어',
                '없음',
                '없음'
            ],
            'sales_count': [50, 30, 25, 40, 35],
            'last_updated': [datetime.now().strftime('%Y-%m-%d %H:%M:%S')] * 5
        }
        df = pd.DataFrame(sample_data)
        df.to_csv(PRODUCTS_FILE, index=False, encoding='utf-8-sig')

def load_products():
    """상품 데이터 로드"""
    ensure_data_dir()
    if not os.path.exists(PRODUCTS_FILE):
        init_products_file()
    return pd.read_csv(PRODUCTS_FILE, encoding='utf-8-sig')

def save_products(df):
    """상품 데이터 저장"""
    ensure_data_dir()
    df.to_csv(PRODUCTS_FILE, index=False, encoding='utf-8-sig')

def update_stock(product_id, new_stock):
    """재고 업데이트"""
    df = load_products()
    if product_id in df['id'].values:
        old_stock = df.loc[df['id'] == product_id, 'stock'].values[0]
        df.loc[df['id'] == product_id, 'stock'] = new_stock
        df.loc[df['id'] == product_id, 'last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        save_products(df)
        
        # 알림 생성
        if old_stock == 0 and new_stock > 0:
            create_notification(product_id, "입고", f"상품이 입고되었습니다. (재고: {new_stock}개)")
        elif old_stock > 0 and new_stock == 0:
            create_notification(product_id, "품절", "상품이 품절되었습니다.")
        
        return True
    return False

def increment_sales(product_id):
    """판매 수량 증가"""
    df = load_products()
    if product_id in df['id'].values:
        df.loc[df['id'] == product_id, 'sales_count'] = df.loc[df['id'] == product_id, 'sales_count'].values[0] + 1
        save_products(df)
        return True
    return False

def load_notifications():
    """알림 데이터 로드"""
    ensure_data_dir()
    if not os.path.exists(NOTIFICATIONS_FILE):
        return []
    with open(NOTIFICATIONS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_notifications(notifications):
    """알림 데이터 저장"""
    ensure_data_dir()
    with open(NOTIFICATIONS_FILE, 'w', encoding='utf-8') as f:
        json.dump(notifications, f, ensure_ascii=False, indent=2)

def create_notification(product_id, notification_type, message):
    """알림 생성"""
    notifications = load_notifications()
    notification = {
        'id': len(notifications) + 1,
        'product_id': product_id,
        'type': notification_type,
        'message': message,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'read': False
    }
    notifications.append(notification)
    save_notifications(notifications)

def get_unread_notifications():
    """읽지 않은 알림 가져오기"""
    notifications = load_notifications()
    return [n for n in notifications if not n.get('read', False)]

def mark_notification_read(notification_id):
    """알림 읽음 처리"""
    notifications = load_notifications()
    for n in notifications:
        if n['id'] == notification_id:
            n['read'] = True
            break
    save_notifications(notifications)

