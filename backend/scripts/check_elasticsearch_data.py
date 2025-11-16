"""
Check Elasticsearch Data Structure
Displays actual document structure and metadata
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import json
from app.config import settings
from app.core.database.elasticsearch import get_elasticsearch_client


def check_elasticsearch_data():
    """Check and display Elasticsearch data structure"""
    
    print("="*80)
    print("🔍 ELASTICSEARCH DATA STRUCTURE CHECK")
    print("="*80)
    
    # Connect to Elasticsearch
    print(f"\n📡 Connecting to Elasticsearch...")
    print(f"   Index: {settings.ELASTICSEARCH_INDEX_NAME}")
    
    try:
        es_client = get_elasticsearch_client()
        print("✅ Connected successfully")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return
    
    # Check index exists
    print(f"\n📊 Checking index...")
    try:
        if not es_client.indices.exists(index=settings.ELASTICSEARCH_INDEX_NAME):
            print(f"❌ Index '{settings.ELASTICSEARCH_INDEX_NAME}' does not exist")
            return
        print(f"✅ Index exists")
    except Exception as e:
        print(f"❌ Error checking index: {e}")
        return
    
    # Get index stats
    print(f"\n📈 Index Statistics:")
    try:
        stats = es_client.indices.stats(index=settings.ELASTICSEARCH_INDEX_NAME)
        doc_count = stats['_all']['primaries']['docs']['count']
        size_bytes = stats['_all']['primaries']['store']['size_in_bytes']
        size_mb = size_bytes / (1024 * 1024)
        print(f"   Total Documents: {doc_count:,}")
        print(f"   Index Size: {size_mb:.2f} MB")
    except Exception as e:
        print(f"❌ Error getting stats: {e}")
    
    # Get mapping
    print(f"\n🗺️  Index Mapping:")
    try:
        mapping = es_client.indices.get_mapping(index=settings.ELASTICSEARCH_INDEX_NAME)
        properties = mapping[settings.ELASTICSEARCH_INDEX_NAME]['mappings']['properties']
        print(f"   Fields: {list(properties.keys())}")
    except Exception as e:
        print(f"❌ Error getting mapping: {e}")
    
    # Get sample documents
    print(f"\n📄 Sample Documents (First 3):")
    print("="*80)
    
    try:
        response = es_client.search(
            index=settings.ELASTICSEARCH_INDEX_NAME,
            body={
                "query": {"match_all": {}},
                "size": 3
            }
        )
        
        for i, hit in enumerate(response['hits']['hits'], 1):
            doc = hit['_source']
            print(f"\n{'='*80}")
            print(f"DOCUMENT {i} (ID: {hit['_id']})")
            print(f"{'='*80}")
            
            # Display main fields
            print(f"\n📝 QUESTION:")
            print(f"   {doc.get('question', 'N/A')[:200]}")
            
            print(f"\n📚 CONTEXT:")
            context = doc.get('context', 'N/A')
            print(f"   {context[:300]}..." if len(context) > 300 else f"   {context}")
            
            print(f"\n📄 ARTICLE:")
            print(f"   {doc.get('article', 'N/A')}")
            
            print(f"\n📖 DOCUMENT:")
            print(f"   {doc.get('document', 'N/A')}")
            
            print(f"\n✏️  EXTRACTIVE ANSWER:")
            extractive = doc.get('extractive_answer', 'N/A')
            print(f"   {extractive[:200]}..." if len(extractive) > 200 else f"   {extractive}")
            
            print(f"\n💬 ABSTRACTIVE ANSWER:")
            abstractive = doc.get('abstractive_answer', 'N/A')
            print(f"   {abstractive[:200]}..." if len(abstractive) > 200 else f"   {abstractive}")
            
            print(f"\n❓ YES/NO:")
            print(f"   {doc.get('yes_no', 'N/A')}")
            
            # Display metadata
            if 'metadata' in doc:
                print(f"\n🏷️  METADATA:")
                metadata = doc['metadata']
                for key, value in metadata.items():
                    if key not in ['created_at', 'indexed_at']:  # Skip timestamps
                        print(f"   {key}: {value}")
            
            # Display embeddings info
            if 'question_embedding' in doc:
                emb_len = len(doc['question_embedding'])
                print(f"\n🔢 EMBEDDINGS:")
                print(f"   Question embedding: {emb_len} dimensions")
                print(f"   First 5 values: {doc['question_embedding'][:5]}")
            
            if 'context_embedding' in doc:
                emb_len = len(doc['context_embedding'])
                print(f"   Context embedding: {emb_len} dimensions")
                print(f"   First 5 values: {doc['context_embedding'][:5]}")
    
    except Exception as e:
        print(f"❌ Error retrieving documents: {e}")
        import traceback
        traceback.print_exc()
    
    # Test search query
    print(f"\n{'='*80}")
    print(f"🔍 TEST SEARCH QUERY")
    print(f"{'='*80}")
    
    test_query = "Điều kiện xét tuyển vào đại học là gì?"
    print(f"\nQuery: {test_query}")
    
    try:
        response = es_client.search(
            index=settings.ELASTICSEARCH_INDEX_NAME,
            body={
                "query": {
                    "multi_match": {
                        "query": test_query,
                        "fields": ["question^2", "context", "abstractive_answer"]
                    }
                },
                "size": 3
            }
        )
        
        print(f"\nFound {response['hits']['total']['value']} results")
        print(f"\nTop 3 Results:")
        
        for i, hit in enumerate(response['hits']['hits'], 1):
            doc = hit['_source']
            score = hit['_score']
            print(f"\n--- Result {i} (Score: {score:.2f}) ---")
            print(f"Question: {doc.get('question', 'N/A')[:150]}")
            print(f"Article: {doc.get('article', 'N/A')}")
            print(f"Document: {doc.get('document', 'N/A')[:100]}")
            
            # Check what answer fields exist
            has_extractive = bool(doc.get('extractive_answer', '').strip())
            has_abstractive = bool(doc.get('abstractive_answer', '').strip())
            print(f"Has extractive_answer: {has_extractive}")
            print(f"Has abstractive_answer: {has_abstractive}")
            
            if has_abstractive:
                print(f"Abstractive: {doc.get('abstractive_answer', '')[:150]}")
            elif has_extractive:
                print(f"Extractive: {doc.get('extractive_answer', '')[:150]}")
    
    except Exception as e:
        print(f"❌ Error in test search: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\n{'='*80}")
    print("✅ CHECK COMPLETE")
    print(f"{'='*80}")


if __name__ == "__main__":
    check_elasticsearch_data()

