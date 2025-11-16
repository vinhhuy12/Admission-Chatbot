"""
Data Ingestion Script for Admissions Q&A Dataset
Reads train.csv, generates embeddings, and indexes to Elasticsearch
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
from datetime import datetime
from tqdm import tqdm
from sentence_transformers import SentenceTransformer
from elasticsearch.helpers import bulk

from app.config import settings
from app.core.elasticsearch import get_elasticsearch_client


class DataIngestion:
    """Handle data ingestion from CSV to Elasticsearch"""
    
    def __init__(self):
        self.es_client = get_elasticsearch_client()
        self.index_name = settings.ELASTICSEARCH_INDEX_NAME
        
        # Load embedding model
        print(f"📦 Loading embedding model: {settings.EMBEDDING_MODEL}")
        self.embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)
        print(f"✅ Model loaded. Embedding dimension: {settings.EMBEDDING_DIMENSION}")
        
    def load_csv(self, file_path: str) -> pd.DataFrame:
        """Load CSV file"""
        print(f"\n📂 Loading CSV file: {file_path}")
        df = pd.read_csv(file_path)
        print(f"✅ Loaded {len(df)} rows")
        print(f"📊 Columns: {list(df.columns)}")
        return df
    
    def classify_question_type(self, yes_no_value: str) -> str:
        """Classify question type based on yes/no field"""
        if pd.isna(yes_no_value) or yes_no_value == "":
            return "factual"
        yes_no_lower = str(yes_no_value).lower().strip()
        if yes_no_lower in ["yes", "no", "có", "không"]:
            return "yes_no"
        return "factual"
    
    def get_answer_type(self, row: dict) -> str:
        """Determine answer type"""
        has_extractive = pd.notna(row.get("extractive answer")) and str(row.get("extractive answer")).strip() != ""
        has_abstractive = pd.notna(row.get("abstractive answer")) and str(row.get("abstractive answer")).strip() != ""
        
        if has_extractive and has_abstractive:
            return "both"
        elif has_extractive:
            return "extractive"
        elif has_abstractive:
            return "abstractive"
        else:
            return "none"
    
    def create_metadata(self, row: dict, index: int) -> dict:
        """Create comprehensive metadata for document"""
        return {
            # Document identification
            "doc_id": f"qa_{index:06d}",
            "source_file": "train.csv",
            "source_row": index,
            "created_at": datetime.now().isoformat(),
            "indexed_at": datetime.now().isoformat(),
            
            # Legal/Regulatory metadata
            "article": str(row.get("article", "")).strip(),
            "document_name": str(row.get("document", "")).strip(),
            "document_type": "regulation",
            "language": "vi",
            
            # Content metadata
            "question_length": len(str(row.get("question", ""))),
            "context_length": len(str(row.get("context", ""))),
            "answer_length": len(str(row.get("abstractive answer", ""))),
            
            # Classification
            "question_type": self.classify_question_type(row.get("yes/no")),
            "answer_type": self.get_answer_type(row),
            "has_extractive_answer": pd.notna(row.get("extractive answer")) and str(row.get("extractive answer")).strip() != "",
            "has_abstractive_answer": pd.notna(row.get("abstractive answer")) and str(row.get("abstractive answer")).strip() != "",
            
            # Chunking metadata (no chunking for this dataset)
            "is_chunked": False,
            "chunk_index": 0,
            "total_chunks": 1,
            "chunk_position": 0.0,
            "parent_doc_id": None,
            
            # Optimization flags
            "boost_factor": 1.0,
            "is_active": True,
            "is_verified": True,
            "priority": "normal",
        }
    
    def generate_embeddings(self, texts: list) -> list:
        """Generate embeddings for a batch of texts"""
        embeddings = self.embedding_model.encode(
            texts,
            batch_size=settings.EMBEDDING_BATCH_SIZE,
            show_progress_bar=False,
            convert_to_numpy=True
        )
        return embeddings.tolist()
    
    def prepare_document(self, row: dict, index: int, question_emb: list, context_emb: list) -> dict:
        """Prepare document for Elasticsearch indexing"""
        return {
            "_index": self.index_name,
            "_id": f"qa_{index:06d}",
            "_source": {
                # Original data
                "index": index,
                "question": str(row.get("question", "")).strip(),
                "context": str(row.get("context", "")).strip(),
                "article": str(row.get("article", "")).strip(),
                "document": str(row.get("document", "")).strip(),
                "extractive_answer": str(row.get("extractive answer", "")).strip(),
                "abstractive_answer": str(row.get("abstractive answer", "")).strip(),
                "yes_no": str(row.get("yes/no", "")).strip(),
                
                # Embeddings
                "question_embedding": question_emb,
                "context_embedding": context_emb,
                
                # Metadata
                "metadata": self.create_metadata(row, index),
                
                # Timestamps
                "created_at": datetime.now().isoformat(),
            }
        }
    
    def check_existing_documents(self) -> int:
        """Check how many documents already exist in index"""
        try:
            count = self.es_client.count(index=self.index_name)
            return count["count"]
        except:
            return 0
    
    def ingest_data(self, df: pd.DataFrame, skip_existing: bool = True):
        """Main ingestion process"""
        
        # Check existing documents
        existing_count = self.check_existing_documents()
        if existing_count > 0 and skip_existing:
            print(f"\n⚠️  Index already contains {existing_count} documents")
            response = input("Do you want to continue and add more? (y/n): ")
            if response.lower() != 'y':
                print("❌ Ingestion cancelled")
                return
        
        print(f"\n🚀 Starting data ingestion...")
        print(f"📊 Total documents to process: {len(df)}")
        print(f"📦 Batch size: {settings.BATCH_SIZE_INGESTION}")
        
        # Process in batches
        batch_size = settings.BATCH_SIZE_INGESTION
        total_batches = (len(df) + batch_size - 1) // batch_size
        
        success_count = 0
        error_count = 0
        
        for batch_idx in tqdm(range(total_batches), desc="Processing batches"):
            start_idx = batch_idx * batch_size
            end_idx = min(start_idx + batch_size, len(df))
            batch_df = df.iloc[start_idx:end_idx]
            
            try:
                # Extract texts for embedding
                questions = batch_df["question"].fillna("").astype(str).tolist()
                contexts = batch_df["context"].fillna("").astype(str).tolist()
                
                # Generate embeddings
                question_embeddings = self.generate_embeddings(questions)
                context_embeddings = self.generate_embeddings(contexts)
                
                # Prepare documents
                documents = []
                for i, (idx, row) in enumerate(batch_df.iterrows()):
                    doc = self.prepare_document(
                        row.to_dict(),
                        idx,
                        question_embeddings[i],
                        context_embeddings[i]
                    )
                    documents.append(doc)
                
                # Bulk index to Elasticsearch
                success, errors = bulk(
                    self.es_client,
                    documents,
                    raise_on_error=False,
                    raise_on_exception=False
                )
                
                success_count += success
                if errors:
                    error_count += len(errors)
                    print(f"\n⚠️  Batch {batch_idx + 1}: {len(errors)} errors")
                
            except Exception as e:
                error_count += len(batch_df)
                print(f"\n❌ Error processing batch {batch_idx + 1}: {e}")
        
        # Summary
        print(f"\n{'='*60}")
        print(f"✅ INGESTION COMPLETE")
        print(f"{'='*60}")
        print(f"✅ Successfully indexed: {success_count} documents")
        if error_count > 0:
            print(f"❌ Failed: {error_count} documents")
        print(f"📊 Total in index: {self.check_existing_documents()} documents")
        print(f"{'='*60}")


def main():
    """Main execution"""
    print("="*60)
    print("🎓 ADMISSIONS Q&A DATA INGESTION")
    print("="*60)
    
    # Initialize ingestion
    ingestion = DataIngestion()
    
    # Load CSV
    csv_path = Path(__file__).parent.parent.parent / settings.DATA_FILE_PATH
    if not csv_path.exists():
        print(f"❌ CSV file not found: {csv_path}")
        return 1
    
    df = ingestion.load_csv(str(csv_path))
    
    # Start ingestion
    ingestion.ingest_data(df, skip_existing=settings.SKIP_EXISTING_DOCS)
    
    print("\n🎉 Done!")
    return 0


if __name__ == "__main__":
    exit(main())

