"use client";
import { useState } from "react";
const base = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";
export default function Home() {
 const [token,setToken]=useState(""), [workspace,setWorkspace]=useState(""), [query,setQuery]=useState(""), [result,setResult]=useState<any>(null);
 async function search(){const r=await fetch(`${base}/search`,{method:"POST",headers:{"Content-Type":"application/json",Authorization:`Bearer ${token}`},body:JSON.stringify({workspace_id:workspace,query,top_k:5})});setResult(await r.json())}
 return <main><section><p className="eyebrow">VECTORVAULT</p><h1>Secure semantic knowledge retrieval.</h1><p>Upload, search, and ask against tenant-isolated document collections.</p></section><section className="panel"><label>Access token<input value={token} onChange={e=>setToken(e.target.value)} placeholder="Bearer token"/></label><label>Workspace ID<input value={workspace} onChange={e=>setWorkspace(e.target.value)} /></label><label>Semantic search<input value={query} onChange={e=>setQuery(e.target.value)} placeholder="Ask your knowledge base"/></label><button onClick={search}>Search</button>{result&&<pre>{JSON.stringify(result,null,2)}</pre>}</section><footer>API documentation: <a href="http://localhost:8000/docs">/docs</a></footer></main>}
