#!/usr/bin/env python3
"""
Backward-Compatible Embedding Manager
Handles optional embeddings for memories with graceful fallback
"""

import json
import sqlite3
import requests
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
import os
import time

class EmbeddingManager:
    """Manages embeddings with backward compatibility and graceful degradation"""
    
    def __init__(self, db_path: str, ollama_url: str = "http://localhost:11434"):
        self.db_path = db_path
        self.ollama_url = ollama_url
        self.embedding_model = "nomic-embed-text"
        self.embedding_enabled = self._test_embedding_availability()
        
        # Initialize embedding storage if available
        if self.embedding_enabled:
            self._init_embedding_tables()
    
    def _test_embedding_availability(self) -> bool:
        """Test if embedding model is available and working"""
        try:
            # Quick test embedding
            response = requests.post(
                f"{self.ollama_url}/api/embeddings",
                json={
                    "model": self.embedding_model,
                    "prompt": "test"
                },
                timeout=5
            )
            return response.status_code == 200
        except:
            return False
    
    def _init_embedding_tables(self):
        """Initialize embedding storage tables if they don't exist"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Create embeddings table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS memory_embeddings (
                        memory_uuid TEXT PRIMARY KEY,
                        embedding BLOB NOT NULL,
                        embedding_model TEXT NOT NULL,
                        content_hash TEXT,
                        created_at TEXT DEFAULT (datetime('now', 'utc')),
                        FOREIGN KEY (memory_uuid) REFERENCES memory (memory_uuid)
                    )
                """)
                
                # Create index for faster lookups
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_memory_embeddings_uuid 
                    ON memory_embeddings (memory_uuid)
                """)
                
                conn.commit()
        except Exception as e:
            print(f"Warning: Could not initialize embedding tables: {e}")
            self.embedding_enabled = False
    
    def get_embedding(self, text: str) -> Optional[List[float]]:
        """Generate embedding for text, return None if not available"""
        if not self.embedding_enabled:
            return None
        
        try:
            response = requests.post(
                f"{self.ollama_url}/api/embeddings",
                json={
                    "model": self.embedding_model,
                    "prompt": text
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("embedding")
            else:
                return None
        except:
            return None
    
    def store_embedding(self, memory_uuid: str, content: str, force_update: bool = False) -> bool:
        """Store embedding for memory content, return success status"""
        if not self.embedding_enabled:
            return False
        
        try:
            # Check if embedding already exists
            if not force_update:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.execute(
                        "SELECT 1 FROM memory_embeddings WHERE memory_uuid = ?",
                        (memory_uuid,)
                    )
                    if cursor.fetchone():
                        return True  # Already exists, no need to regenerate
            
            # Generate embedding
            embedding = self.get_embedding(content[:1000])  # Limit content length
            if not embedding:
                return False
            
            # Store in database
            with sqlite3.connect(self.db_path) as conn:
                # Convert embedding to binary
                embedding_blob = np.array(embedding, dtype=np.float32).tobytes()
                content_hash = hash(content) % (10**10)  # Simple content hash
                
                conn.execute("""
                    INSERT OR REPLACE INTO memory_embeddings 
                    (memory_uuid, embedding, embedding_model, content_hash)
                    VALUES (?, ?, ?, ?)
                """, (memory_uuid, embedding_blob, self.embedding_model, str(content_hash)))
                
                conn.commit()
                return True
                
        except Exception as e:
            print(f"Warning: Failed to store embedding for {memory_uuid}: {e}")
            return False
    
    def get_stored_embedding(self, memory_uuid: str) -> Optional[List[float]]:
        """Retrieve stored embedding for memory"""
        if not self.embedding_enabled:
            return None
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT embedding FROM memory_embeddings WHERE memory_uuid = ?",
                    (memory_uuid,)
                )
                result = cursor.fetchone()
                
                if result:
                    # Convert binary back to list
                    embedding_blob = result[0]
                    embedding = np.frombuffer(embedding_blob, dtype=np.float32).tolist()
                    return embedding
                else:
                    return None
        except:
            return None
    
    def process_existing_memories(self, batch_size: int = 10, max_memories: Optional[int] = None):
        """Process existing memories to add embeddings"""
        if not self.embedding_enabled:
            print("🚫 Embeddings not available - skipping processing")
            return
        
        print("🔄 Processing existing memories for embeddings...")
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Get memories without embeddings
                query = """
                    SELECT m.memory_uuid, m.payload 
                    FROM memory m
                    LEFT JOIN memory_embeddings e ON m.memory_uuid = e.memory_uuid
                    WHERE e.memory_uuid IS NULL
                    ORDER BY m.created_at DESC
                """
                
                if max_memories:
                    query += f" LIMIT {max_memories}"
                
                cursor = conn.execute(query)
                memories_to_process = cursor.fetchall()
                
                print(f"📊 Found {len(memories_to_process)} memories without embeddings")
                
                processed = 0
                for memory_uuid, payload_str in memories_to_process:
                    try:
                        # Extract content from payload
                        payload = json.loads(payload_str)
                        content = payload.get('content', payload_str)
                        
                        # Store embedding
                        success = self.store_embedding(memory_uuid, content)
                        
                        if success:
                            processed += 1
                            print(f"✅ Processed {processed}/{len(memories_to_process)}: {memory_uuid[:8]}...")
                        else:
                            print(f"⚠️  Failed: {memory_uuid[:8]}...")
                        
                        # Batch processing with delay
                        if processed % batch_size == 0:
                            time.sleep(1)  # Rate limiting
                            
                    except Exception as e:
                        print(f"❌ Error processing {memory_uuid[:8]}: {e}")
                        continue
                
                print(f"🎉 Completed: {processed}/{len(memories_to_process)} embeddings created")
                
        except Exception as e:
            print(f"❌ Batch processing failed: {e}")
    
    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between vectors"""
        try:
            a = np.array(vec1)
            b = np.array(vec2)
            
            dot_product = np.dot(a, b)
            norm_a = np.linalg.norm(a)
            norm_b = np.linalg.norm(b)
            
            if norm_a == 0 or norm_b == 0:
                return 0.0
                
            return float(dot_product / (norm_a * norm_b))
        except:
            return 0.0
    
    def semantic_search(self, query: str, limit: int = 10, min_similarity: float = 0.3) -> List[Tuple]:
        """Perform semantic search, return list of (similarity, memory_uuid, content, created_at, type)"""
        if not self.embedding_enabled:
            return []
        
        try:
            # Generate query embedding
            query_embedding = self.get_embedding(query)
            if not query_embedding:
                return []
            
            # Get all memories with embeddings
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT e.memory_uuid, e.embedding, m.payload, m.created_at
                    FROM memory_embeddings e
                    JOIN memory m ON e.memory_uuid = m.memory_uuid
                    ORDER BY m.created_at DESC
                """)
                
                results = []
                for memory_uuid, embedding_blob, payload_str, created_at in cursor:
                    try:
                        # Convert embedding back to list
                        stored_embedding = np.frombuffer(embedding_blob, dtype=np.float32).tolist()
                        
                        # Calculate similarity
                        similarity = self.cosine_similarity(query_embedding, stored_embedding)
                        
                        if similarity >= min_similarity:
                            # Extract content and type
                            payload = json.loads(payload_str)
                            content = payload.get('content', payload_str)
                            memory_type = payload.get('type', 'unknown')
                            
                            results.append((similarity, memory_uuid, content, created_at, memory_type))
                    
                    except Exception as e:
                        continue  # Skip problematic entries
                
                # Sort by similarity and return top results
                results.sort(key=lambda x: x[0], reverse=True)
                return results[:limit]
                
        except Exception as e:
            print(f"❌ Semantic search failed: {e}")
            return []
    
    def get_embedding_stats(self) -> Dict[str, Any]:
        """Get statistics about embedding coverage"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Total memories
                cursor = conn.execute("SELECT COUNT(*) FROM memory")
                total_memories = cursor.fetchone()[0]
                
                # Memories with embeddings
                cursor = conn.execute("SELECT COUNT(*) FROM memory_embeddings")
                embedded_memories = cursor.fetchone()[0] if self.embedding_enabled else 0
                
                coverage = (embedded_memories / total_memories * 100) if total_memories > 0 else 0
                
                return {
                    "embedding_enabled": self.embedding_enabled,
                    "total_memories": total_memories,
                    "embedded_memories": embedded_memories,
                    "coverage_percentage": round(coverage, 1),
                    "model": self.embedding_model if self.embedding_enabled else None
                }
        except:
            return {
                "embedding_enabled": False,
                "total_memories": 0,
                "embedded_memories": 0,
                "coverage_percentage": 0,
                "model": None
            }


def test_embedding_manager():
    """Test the embedding manager with backward compatibility"""
    print("🧪 Testing Embedding Manager...")
    
    # Initialize manager
    db_path = "/Users/mars/Dev/sidekick-boot-loader/db/claude-sonnet-4-session-20250829.db"
    manager = EmbeddingManager(db_path)
    
    # Show stats
    stats = manager.get_embedding_stats()
    print(f"📊 Embedding Stats: {stats}")
    
    if stats["embedding_enabled"]:
        print("✅ Embeddings are available!")
        
        # Test embedding a sample memory
        print("\n🔍 Testing embedding storage...")
        test_uuid = "test-memory-uuid-12345"
        test_content = "This is a test memory about AI coordination and distributed intelligence patterns."
        
        success = manager.store_embedding(test_uuid, test_content)
        print(f"Storage test: {'✅ Success' if success else '❌ Failed'}")
        
        # Test retrieval
        retrieved = manager.get_stored_embedding(test_uuid)
        print(f"Retrieval test: {'✅ Success' if retrieved else '❌ Failed'}")
        
        # Test semantic search
        print("\n🔍 Testing semantic search...")
        results = manager.semantic_search("memory compression crisis", limit=3)
        print(f"Found {len(results)} semantic matches")
        
        for i, (similarity, uuid, content, created_at, mem_type) in enumerate(results, 1):
            print(f"{i}. Similarity: {similarity:.3f} | {uuid[:8]}... | {mem_type}")
    
    else:
        print("⚠️  Embeddings not available - system will use keyword search fallback")


if __name__ == "__main__":
    test_embedding_manager()