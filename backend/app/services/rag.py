def grounded_answer(question:str, chunks:list[dict])->str:
 if not chunks: return "I could not find supporting context in this workspace."
 context="\n".join(f"[{i+1}] {x['text']}" for i,x in enumerate(chunks))
 return f"Retrieved context for your question: {question}\n\n{context}\n\nThis local fallback returns retrieved evidence rather than synthesizing unsupported claims."
