# test_rag.py

import asyncio
from langchain_community.vectorstores import Chroma
from server.core.google_llm import embeddings
from server.core.config import settings

async def main():
    """ChromaDB에서 문서를 검색하는 테스트"""
    query = "7월10일 진행한 'AI 도입 TF' 회의록 요약해줘."
    print(f"질문: {query}")

    try:
        # 1. Vector DB 로드
        vectorstore = Chroma(
            persist_directory=settings.CHROMA_PATH, 
            embedding_function=embeddings
        )
        
        # 2. Retriever 생성 (가장 유사한 3개 문서 검색)
        retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
        
        # 3. 문서 검색 실행
        docs = await retriever.ainvoke(query)
        
        print("\n--- 검색 결과 ---")
        if not docs:
            print("검색된 문서가 없습니다.")
        else:
            for i, doc in enumerate(docs):
                print(f"\n[문서 {i+1}]")
                print(f"내용: {doc.page_content[:300]}...") # 내용 일부만 출력
                print(f"출처: {doc.metadata.get('source', 'N/A')}")

    except Exception as e:
        print(f"\n--- 에러 발생 ---")
        print(f"오류: {e}")

if __name__ == "__main__":
    asyncio.run(main())

