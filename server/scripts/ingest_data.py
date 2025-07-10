import os
import shutil
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma

# 프로젝트 루트 디렉토리를 기준으로 경로 설정
from server.core.llm import get_embedding_model
from server.core.config import settings

def ingest_documents():
    """docs 폴더의 문서를 임베딩하여 ChromaDB에 저장합니다."""
    
    # 기존 db 디렉토리가 있다면 삭제
    if os.path.exists(settings.CHROMA_PATH):
        print(f"기존 Vector DB '{settings.CHROMA_PATH}'를 삭제합니다.")
        shutil.rmtree(settings.CHROMA_PATH)

    print("문서 로딩을 시작합니다...")
    # 'utf-8' 인코딩 명시
    loader = DirectoryLoader(
        'docs', 
        glob="**/*.txt", 
        loader_cls=TextLoader, 
        loader_kwargs={'encoding': 'utf-8'}
    )
    documents = loader.load()
    if not documents:
        print("로드할 문서가 없습니다.")
        return

    print(f"{len(documents)}개의 문서를 로드했습니다.")
    
    print("문서 분할을 시작합니다...")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(documents)
    print(f"{len(splits)}개의 청크로 분할했습니다.")

    print("임베딩 및 Vector DB 저장을 시작합니다...")
    embedding_model = get_embedding_model()
    
    # ChromaDB에 저장
    vectorstore = Chroma.from_documents(
        documents=splits,
        embedding=embedding_model,
        persist_directory=settings.CHROMA_PATH
    )
    
    print(f"'{settings.CHROMA_PATH}'에 Vector DB 저장을 완료했습니다.")

if __name__ == "__main__":
    ingest_documents()