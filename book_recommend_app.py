import streamlit as st
import requests
from datetime import datetime
import pandas as pd

# 초기화: 세션 상태에 독서 기록과 목표 저장
if "reading_log" not in st.session_state:
    st.session_state.reading_log = []

if "monthly_goal" not in st.session_state:
    st.session_state.monthly_goal = 5  # 기본 목표 5권

# 함수: 구글 북스 API로 책 검색
def search_books(query, max_results=10):
    url = "https://www.googleapis.com/books/v1/volumes"
    params = {"q": query, "maxResults": max_results,"key": "AIzaSyCfw7nmYXCRbDC2BMoGvAmvSM06w5Zvqb8"}
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        st.write("🔍 API 결과 (디버그용):", data)  # API 원본 데이터 출력
        books = []
        for item in data.get("items", []):
            info = item.get("volumeInfo", {})
            books.append({
                "title": info.get("title", "제목 없음"),
                "authors": ", ".join(info.get("authors", ["정보 없음"])),
                "publishedDate": info.get("publishedDate", "출판일 없음"),
                "description": (info.get("description", "")[:300] + "...") if info.get("description") else "",
                "thumbnail": info.get("imageLinks", {}).get("thumbnail", None),
                "infoLink": info.get("infoLink", None),
            })
        return books
    except Exception as e:
        st.error(f"API 요청 중 오류 발생: {e}")
        return []

# UI: 독서 목표 설정
st.sidebar.header("독서 목표 설정")
monthly_goal = st.sidebar.number_input("이번 달 목표 권수", min_value=1, max_value=50, value=st.session_state.monthly_goal)
st.session_state.monthly_goal = monthly_goal

# UI: 제목
st.title("📚 책 추천 및 독서 기록 앱")

# UI: 장르 입력 (키워드 검색용)
genre_query = st.text_input("관심 있는 장르/주제 입력 (예: SF, 역사, 자기계발)")

if genre_query:
    st.subheader(f'📖 "{genre_query}" 분야 추천 도서')
    books = search_books(genre_query)

    if not books:
        st.info("🔍 검색 결과가 없습니다. 다른 키워드로 시도해보세요.")
    else:
        for idx, book in enumerate(books):
            cols = st.columns([1, 3])
            with cols[0]:
                if book["thumbnail"]:
                    st.image(book["thumbnail"], width=80)
            with cols[1]:
                st.markdown(f"**[{book['title']}]({book['infoLink']})**")
                st.markdown(f"*저자: {book['authors']}*")
                st.markdown(f"*출판일: {book['publishedDate']}*")
                st.write(book["description"])
                if st.button(f"읽은 책으로 등록하기 - {idx}", key=f"log_{idx}"):
                    st.session_state.reading_log.append({
                        "title": book["title"],
                        "authors": book["authors"],
                        "date": datetime.today().strftime("%Y-%m-%d"),
                        "rating": None,
                        "review": "",
                    })
                    st.success(f"'{book['title']}' 가 독서 기록에 추가되었어요!")

st.markdown("---")

# UI: 독서 기록 리스트 및 입력
st.subheader("📝 독서 기록")

if st.session_state.reading_log:
    df = pd.DataFrame(st.session_state.reading_log)
    st.dataframe(df[["title", "authors", "date"]])

    # 기록 수정(평점/감상평)
    for i, record in enumerate(st.session_state.reading_log):
        with st.expander(f"'{record['title']}' 상세 기록 수정"):
            rating = st.slider("평점 (1~5)", 1, 5, value=record["rating"] if record["rating"] else 3, key=f"rating_{i}")
            review = st.text_area("감상평", value=record["review"], key=f"review_{i}")
            st.session_state.reading_log[i]["rating"] = rating
            st.session_state.reading_log[i]["review"] = review

else:
    st.write("아직 읽은 책이 없습니다. 추천 도서에서 ‘읽은 책으로 등록하기’를 눌러보세요!")

# 독서 목표 진행률
st.markdown("---")
st.subheader("🎯 독서 목표 진행률")

this_month = datetime.now().strftime("%Y-%m")
count_this_month = sum(1 for r in st.session_state.reading_log if r["date"].startswith(this_month))

st.write(f"이번 달 목표: {st.session_state.monthly_goal} 권")
st.write(f"이번 달 기록된 독서: {count_this_month} 권")

progress = min(count_this_month / st.session_state.monthly_goal, 1.0)
st.progress(progress)

# 독서 기록 CSV 다운로드
if st.session_state.reading_log:
    df_all = pd.DataFrame(st.session_state.reading_log)
    csv = df_all.to_csv(index=False).encode('utf-8')
    st.download_button("📥 독서 기록 CSV 다운로드", csv, "reading_log.csv", "text/csv")
