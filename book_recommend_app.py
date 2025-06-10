import streamlit as st
import requests

API_KEY = "AIzaSyDkQPoHigCFIMANl4zhKMjvyqh_Z21qTPY"

def search_books_titles(query, max_results=10):
    url = "https://www.googleapis.com/books/v1/volumes"
    params = {
        "q": query,
        "maxResults": max_results,
        "key": API_KEY
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        titles = []
        if "items" in data:
            for item in data["items"]:
                info = item.get("volumeInfo", {})
                title = info.get("title", "제목 없음")
                titles.append(title)
        return titles

    except requests.exceptions.RequestException as e:
        st.error(f"API 요청 중 오류 발생: {e}")
        return []

st.title("📚 책 제목만 보여주기")

query = st.text_input("관심 있는 주제를 입력하세요 (예: 역사, 수학, 철학 등)")

if st.button("검색"):
    if not query.strip():
        st.warning("주제를 입력해주세요!")
    else:
        titles = search_books_titles(query)
        if titles:
            st.subheader(f"'{query}' 관련 도서 제목 목록")
            for i, title in enumerate(titles, 1):
                st.write(f"{i}. {title}")
        else:
            st.info("검색 결과가 없습니다.")
