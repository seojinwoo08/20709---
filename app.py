import streamlit as st
import pandas as pd
import plotly.express as px
from utils.data_manager import (
    load_products, save_products, update_stock, increment_sales,
    load_notifications, get_unread_notifications, mark_notification_read,
    create_notification
)

# 페이지 설정
st.set_page_config(
    page_title="매점 상품 현황",
    page_icon="🏪",
    layout="wide"
)

# 세션 상태 초기화
if 'selected_product' not in st.session_state:
    st.session_state.selected_product = None
if 'view_mode' not in st.session_state:
    st.session_state.view_mode = 'list'

def main():
    st.title("🏪 토평고등학교 매점 상품 현황")
    
    # 알림 표시
    show_notifications()
    
    # 사이드바
    with st.sidebar:
        st.header("📋 메뉴")
        menu = st.radio(
            "선택하세요",
            ["상품 목록", "인기 상품 순위", "관리자 모드"]
        )
        
        # 카테고리 필터
        if menu == "상품 목록":
            st.header("🔍 필터")
            products = load_products()
            categories = ["전체"] + sorted(products['category'].unique().tolist())
            selected_category = st.selectbox("카테고리", categories)
            
            # 재고 상태 필터
            stock_filter = st.selectbox(
                "재고 상태",
                ["전체", "재고 있음", "품절"]
            )
    
    # 메인 콘텐츠
    if menu == "상품 목록":
        show_product_list(selected_category, stock_filter)
    elif menu == "인기 상품 순위":
        show_popular_products()
    elif menu == "관리자 모드":
        show_admin_mode()

def show_notifications():
    """알림 표시"""
    notifications = get_unread_notifications()
    if notifications:
        with st.container():
            st.info(f"🔔 새로운 알림 {len(notifications)}개")
            for notif in notifications[:3]:  # 최근 3개만 표시
                products = load_products()
                product_name = products[products['id'] == notif['product_id']]['name'].values[0] if len(products[products['id'] == notif['product_id']]) > 0 else "알 수 없음"
                st.warning(f"{product_name}: {notif['message']} ({notif['timestamp']})")
                if st.button(f"확인", key=f"notif_{notif['id']}"):
                    mark_notification_read(notif['id'])
                    st.rerun()

def show_product_list(category_filter, stock_filter):
    """상품 목록 표시"""
    st.header("📦 상품 목록")
    
    products = load_products()
    
    # 필터 적용
    if category_filter != "전체":
        products = products[products['category'] == category_filter]
    
    if stock_filter == "재고 있음":
        products = products[products['stock'] > 0]
    elif stock_filter == "품절":
        products = products[products['stock'] == 0]
    
    # 정렬 옵션
    col1, col2 = st.columns([3, 1])
    with col1:
        sort_option = st.selectbox(
            "정렬 기준",
            ["인기순", "가격 낮은순", "가격 높은순", "이름순", "카테고리순"]
        )
    
    # 정렬 적용
    if sort_option == "인기순":
        products = products.sort_values('sales_count', ascending=False)
    elif sort_option == "가격 낮은순":
        products = products.sort_values('price', ascending=True)
    elif sort_option == "가격 높은순":
        products = products.sort_values('price', ascending=False)
    elif sort_option == "이름순":
        products = products.sort_values('name', ascending=True)
    elif sort_option == "카테고리순":
        products = products.sort_values(['category', 'name'], ascending=[True, True])
    
    # 상품 카드 표시
    if len(products) == 0:
        st.info("표시할 상품이 없습니다.")
    else:
        cols = st.columns(3)
        for idx, (_, product) in enumerate(products.iterrows()):
            col_idx = idx % 3
            with cols[col_idx]:
                with st.container():
                    # 재고 상태 표시
                    stock_status = "✅ 재고 있음" if product['stock'] > 0 else "❌ 품절"
                    stock_color = "green" if product['stock'] > 0 else "red"
                    
                    st.markdown(f"### {product['name']}")
                    st.markdown(f"**카테고리:** {product['category']}")
                    st.markdown(f"**가격:** {product['price']:,}원")
                    st.markdown(f"**재고:** <span style='color:{stock_color}'>{stock_status} ({product['stock']}개)</span>", unsafe_allow_html=True)
                    
                    if st.button(f"상세 정보", key=f"detail_{product['id']}"):
                        st.session_state.selected_product = int(product['id'])
                        st.session_state.view_mode = 'detail'
                        st.rerun()
                    
                    st.divider()
        
        # 상품 상세 정보 표시
        if st.session_state.selected_product is not None:
            show_product_detail(st.session_state.selected_product)

def show_product_detail(product_id):
    """상품 상세 정보 표시"""
    products = load_products()
    product = products[products['id'] == product_id].iloc[0]
    
    st.header(f"📋 {product['name']} 상세 정보")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("기본 정보")
        st.write(f"**이름:** {product['name']}")
        st.write(f"**카테고리:** {product['category']}")
        st.write(f"**가격:** {product['price']:,}원")
        
        stock_status = "✅ 재고 있음" if product['stock'] > 0 else "❌ 품절"
        st.write(f"**재고:** {stock_status} ({product['stock']}개)")
        st.write(f"**판매량:** {product['sales_count']}개")
        st.write(f"**최종 업데이트:** {product['last_updated']}")
    
    with col2:
        st.subheader("성분 정보")
        st.write("**성분표:**")
        st.text(product['ingredients'])
        st.write("**알레르기 유발 성분:**")
        st.text(product['allergens'])
    
    # 구매 버튼 (시뮬레이션)
    if product['stock'] > 0:
        if st.button("구매하기 (시뮬레이션)", key=f"buy_{product_id}"):
            new_stock = product['stock'] - 1
            update_stock(product_id, new_stock)
            increment_sales(product_id)
            st.success("구매 완료!")
            st.rerun()
    else:
        st.error("품절된 상품입니다.")
        if st.button("입고 알림 신청", key=f"alert_{product_id}"):
            create_notification(product_id, "입고 요청", f"{product['name']} 입고 알림을 신청하셨습니다.")
            st.info("입고 알림이 신청되었습니다. 입고 시 알림을 드리겠습니다.")
    
    if st.button("목록으로 돌아가기", key="back_to_list"):
        st.session_state.selected_product = None
        st.session_state.view_mode = 'list'
        st.rerun()

def show_popular_products():
    """인기 상품 순위 표시"""
    st.header("🏆 인기 상품 순위")
    
    products = load_products()
    products = products.sort_values('sales_count', ascending=False)
    
    # 상위 10개만 표시
    top_products = products.head(10)
    
    # 막대 그래프
    fig = px.bar(
        top_products,
        x='sales_count',
        y='name',
        orientation='h',
        labels={'sales_count': '판매량', 'name': '상품명'},
        title="인기 상품 TOP 10"
    )
    fig.update_layout(yaxis={'categoryorder': 'total ascending'})
    st.plotly_chart(fig, width='stretch')
    
    # 순위 테이블
    st.subheader("📊 순위표")
    rank_data = []
    for idx, (_, product) in enumerate(top_products.iterrows(), 1):
        rank_data.append({
            '순위': idx,
            '상품명': product['name'],
            '카테고리': product['category'],
            '판매량': product['sales_count'],
            '가격': f"{product['price']:,}원",
            '재고': product['stock']
        })
    
    rank_df = pd.DataFrame(rank_data)
    st.dataframe(rank_df, width='stretch', hide_index=True)
    
    # 카테고리별 통계
    st.subheader("📈 카테고리별 통계")
    category_stats = products.groupby('category').agg({
        'sales_count': 'sum',
        'price': 'mean'
    }).reset_index()
    category_stats.columns = ['카테고리', '총 판매량', '평균 가격']
    category_stats['평균 가격'] = category_stats['평균 가격'].round(0).astype(int)
    
    fig2 = px.pie(
        category_stats,
        values='총 판매량',
        names='카테고리',
        title="카테고리별 판매량 비율"
    )
    st.plotly_chart(fig2, width='stretch')
    
    st.dataframe(category_stats, width='stretch', hide_index=True)

def show_admin_mode():
    """관리자 모드"""
    st.header("⚙️ 관리자 모드")
    
    password = st.text_input("비밀번호", type="password")
    
    # 간단한 비밀번호 체크 (실제로는 더 안전한 방법 사용)
    if password == "admin123" or st.session_state.get('admin_logged_in', False):
        st.session_state.admin_logged_in = True
        
        st.success("관리자 모드에 접속했습니다.")
        
        products = load_products()
        
        st.subheader("📦 재고 관리")
        
        # 상품 선택
        product_options = {f"{row['name']} (ID: {row['id']})": row['id'] for _, row in products.iterrows()}
        selected_product_name = st.selectbox("상품 선택", list(product_options.keys()))
        selected_product_id = product_options[selected_product_name]
        
        product = products[products['id'] == selected_product_id].iloc[0]
        
        st.write(f"**현재 재고:** {product['stock']}개")
        
        col1, col2 = st.columns(2)
        with col1:
            new_stock = st.number_input("새로운 재고 수량", min_value=0, value=int(product['stock']), key="new_stock")
            if st.button("재고 업데이트"):
                update_stock(selected_product_id, new_stock)
                st.success("재고가 업데이트되었습니다!")
                st.rerun()
        
        with col2:
            if st.button("새 상품 추가"):
                st.info("새 상품 추가 기능은 향후 구현 예정입니다.")
        
        st.subheader("📋 전체 상품 목록")
        st.dataframe(products, width='stretch', hide_index=True)
        
        st.subheader("🔔 알림 관리")
        notifications = load_notifications()
        if notifications:
            for notif in reversed(notifications[-10:]):  # 최근 10개
                st.write(f"**{notif['type']}** - {notif['message']} ({notif['timestamp']})")
        else:
            st.info("알림이 없습니다.")
        
        if st.button("로그아웃"):
            st.session_state.admin_logged_in = False
            st.rerun()
    else:
        if password:
            st.error("비밀번호가 올바르지 않습니다.")
        st.info("관리자 모드에 접속하려면 비밀번호를 입력하세요. (기본 비밀번호: admin123)")

if __name__ == "__main__":
    main()

