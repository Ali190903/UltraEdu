import asyncio


class Indexer:
    def __init__(self, embedding, qdrant):
        self.embedding = embedding
        self.qdrant = qdrant

    async def index_textbook_chunks(self, chunks: list[dict], batch_size: int = 5):
        """Embed and index textbook chunks into Qdrant."""
        total = len(chunks)
        for i in range(0, total, batch_size):
            batch = chunks[i : i + batch_size]
            batch_num = i // batch_size + 1
            total_batches = (total + batch_size - 1) // batch_size
            texts = [c["text_content"] for c in batch]

            print(f"      Batch {batch_num}/{total_batches} ({len(batch)} chunks)...")

            # embed_batch now handles retries internally
            vectors = await self.embedding.embed_batch(texts)

            points = []
            for chunk, vector in zip(batch, vectors):
                payload = {k: v for k, v in chunk.items() if k != "id"}
                points.append({
                    "id": chunk["id"],
                    "vector": vector,
                    "payload": payload,
                })

            self.qdrant.upsert(collection="textbooks", points=points)

            # Delay between batches to stay under rate limits
            if i + batch_size < total:
                await asyncio.sleep(3)

    async def index_dim_questions(self, questions: list[dict], batch_size: int = 5):
        """Embed and index DIM questions into Qdrant."""
        total = len(questions)
        for i in range(0, total, batch_size):
            batch = questions[i : i + batch_size]
            batch_num = i // batch_size + 1
            total_batches = (total + batch_size - 1) // batch_size
            texts = [q["question_text"] for q in batch]

            print(f"      DIM Batch {batch_num}/{total_batches} ({len(batch)} questions)...")

            # embed_batch handles retries internally
            vectors = await self.embedding.embed_batch(texts)

            points = []
            for question, vector in zip(batch, vectors):
                payload = {k: v for k, v in question.items() if k != "id"}
                points.append({
                    "id": question["id"],
                    "vector": vector,
                    "payload": payload,
                })

            self.qdrant.upsert(collection="dim_tests", points=points)

            # Delay between batches
            if i + batch_size < total:
                await asyncio.sleep(3)