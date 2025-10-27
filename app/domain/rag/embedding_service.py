import shutil
from typing import List
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from pathlib import Path


class EmbeddingService:
    def __init__(self):
        self.index_path = Path("data/faiss_index")
        self.index_path.mkdir(parents=True, exist_ok=True)
        self.embedding_model = OpenAIEmbeddings()

    def create_embeddings(self, docs_path: Path):
        all_docs = []
        for file in docs_path.iterdir():
            if file.suffix == ".pdf":
                loader = PyPDFLoader(str(file))
            elif file.suffix == ".docx":
                loader = Docx2txtLoader(str(file))
            elif file.suffix in [".txt", ".md"]:
                loader = TextLoader(str(file))
            else:
                continue
            all_docs.extend(loader.load())

        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = splitter.split_documents(all_docs)
        embeddings = OpenAIEmbeddings()
        db = FAISS.from_documents(chunks, embeddings)
        db.save_local(str(self.index_path))
        return db

    def load_embeddings(self):
        embeddings = OpenAIEmbeddings()
        return FAISS.load_local(
            str(self.index_path), embeddings, allow_dangerous_deserialization=True
        )

    def embed_text(self, text: str) -> List[float]:
        """
        Generates an embedding for a single text input using the same model.

        Args:
            text (str): Input text or chunk.
        Returns:
            List[float]: Embedding vector.
        """
        return self.embedding_model.embed_query(text)

    def cleanup(self):
        shutil.rmtree(self.index_path, ignore_errors=True)
        self.index_path.mkdir(parents=True, exist_ok=True)
