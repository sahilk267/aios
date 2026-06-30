#!/usr/bin/env python3
"""Demonstrate token-saving indexing system."""

import sys
import heapq
sys.path.insert(0, 'backend')

from aios.knowledge.indexer import generate_embedding, chunk_text

# Step 1: Load KNOWLEDGE_BASE.md and calculate tokens
with open('KNOWLEDGE_BASE.md', 'r') as f:
    full_content = f.read()

full_tokens = len(full_content) // 4
print("=== TOKEN SAVINGS DEMONSTRATION ===")
print()
print(f"Full KNOWLEDGE_BASE.md:")
print(f"  Characters: {len(full_content):,}")
print(f"  Estimated tokens: {full_tokens:,}")
print()

# Step 2: Chunk the content
chunks = chunk_text(full_content)
print(f"Total chunks created: {len(chunks)}")
print()

# Step 3: Query for specific information
query = "What are the core responsibilities of the Meta-Controller Agent?"
query_embedding = generate_embedding(query)

# Step 4: Find most relevant chunks using cosine similarity
def cosine_similarity(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    mag_a = sum(x * x for x in a) ** 0.5
    mag_b = sum(x * x for x in b) ** 0.5
    if mag_a == 0 or mag_b == 0:
        return 0
    return dot / (mag_a * mag_b)

# Score each chunk
scored_chunks = []
for i, chunk in enumerate(chunks):
    chunk_embedding = generate_embedding(chunk)
    score = cosine_similarity(query_embedding, chunk_embedding)
    scored_chunks.append((score, chunk))

# Get top 3
top_3 = heapq.nlargest(3, scored_chunks, key=lambda x: x[0])

retrieved_text = "\n\n".join([chunk for _, chunk in top_3])
retrieved_tokens = len(retrieved_text) // 4

print(f"Query: \"{query}\"")
print()
print("Top 3 relevant chunks retrieved:")
for i, (score, chunk) in enumerate(top_3):
    chunk_tokens = len(chunk) // 4
    print(f"  Chunk {i+1}: score={score:.4f}, tokens={chunk_tokens}")

print()
print("Retrieved context:")
print(f"  Characters: {len(retrieved_text):,}")
print(f"  Estimated tokens: {retrieved_tokens:,}")
print()

# Step 5: Calculate savings
savings = ((full_tokens - retrieved_tokens) / full_tokens) * 100
print("=== TOKEN SAVINGS ===")
print(f"Without Index: {full_tokens:,} tokens")
print(f"With Index: {retrieved_tokens:,} tokens")
print(f"Savings: {savings:.1f}%")
print()

# Step 6: Show sample of retrieved content
print("=== SAMPLE RETRIEVED CONTENT (first 500 chars) ===")
print(retrieved_text[:500])
