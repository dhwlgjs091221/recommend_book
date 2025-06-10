import streamlit as st
import requests

API_KEY = "여기에_본인의_API_키_입력"

def search_books(query, max_results=10):
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

        books = []
        if "items" in data:
            for item in data["items"]:
                info = item.get("volumeInfo", {})
                title = info.get("title", "제목 없음")
                authors = ", ".join(info.get("authors", ["저자 정보 없음"]))
                description = info.get("description", "설명 없음")
                thumbnail = info.get("imageLinks", {}).get("thumbnail")
                link = info.get("infoLink", "#")
                books.append({
                    "title": title,
                    "authors": authors,
                    "description": description,
                    "thumbnail": thumbnail,
                    "link": link
                })
        return books

    except requests.exceptions.RequestException as e:
        st.error(f"API 요청 중 오류 발생: {e}")
        return []

st.set_page_config(page_title="도서 추천기", page_icon="📚")
st.title("📚 분야별 도서 추천기")

query = st.text_input("관심 있는 주제를 입력하세요 (예: 역사, 수학, 철학 등)", "")

MAX_DESC_LENGTH = 300

if st.button("도서 추천 받기"):
    if not query.strip():
        st.warning("주제를 입력해주세요!")
    else:
        st.subheader(f"🔍 '{query}' 분야 도서 추천")
        books = search_books(query)
        if books:
            for book in books:
                with st.container():
                    st.markdown(f"### [{book['title']}]({book['link']})")
                    st.markdown(f"**저자**: {book['authors']}")
                    if book["thumbnail"]:
                        st.image(book["thumbnail"], width=100)
                    
                    desc = book["description"]
                    if len(desc) > MAX_DESC_LENGTH:
                        desc = desc[:MAX_DESC_LENGTH] + "..."
                    
                    st.markdown(desc)
                    st.markdown("---")
        else:
            st.info("검색 결과가 없습니다. 주제를 다시 입력해보세요.")
