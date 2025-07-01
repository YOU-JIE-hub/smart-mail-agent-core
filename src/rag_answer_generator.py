#!/usr/bin/env python
"""
rag_answer_generator.py
使用 LangChain + OpenAI 針對 FAQ 進行檢索式回答（RAG 架構）。
"""

import argparse
import json
import os
import textwrap
import pathlib
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.llms import OpenAI
from langchain.chains.question_answering import load_qa_chain

# 讀取 API 金鑰（建議放在 .env 檔中）
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# 預設找不到答案時的回覆
TEMPLATE_CONTACT = (
    "很抱歉，目前知識庫中找不到相關資訊。"
    "我們已將您的問題轉交客服專員，將於 1 個工作日內與您聯絡；"
    "或您也可以直接來信 support@example.com / 電話 (02)-1234-5678。謝謝！"
)


def build_prompt(query: str, docs: list[str]) -> str:
    """
    組合 RAG 輸入 prompt，將檢索結果與使用者問題一併餵給 LLM
    """
    if not docs:
        return TEMPLATE_CONTACT

    joined = "\n\n".join(docs)
    prompt = textwrap.dedent(f"""
        以下為文件內容節錄，請根據內容回答使用者問題。
        若文件未包含答案，請回答「{TEMPLATE_CONTACT}」：

        文件：
        {joined}

        使用者問題：
        {query}

        回答（中文）：
    """)
    return prompt.strip()


def main() -> None:
    ap = argparse.ArgumentParser(description="根據 FAQ 回答問題")
    ap.add_argument("--query", required=True, help="使用者問題")
    ap.add_argument("--kb", required=True, help="FAQ 檔案（txt 或 markdown）")
    ap.add_argument("--output", required=True, help="輸出 JSON 路徑")
    ap.add_argument("--model", default="gpt-3.5-turbo", help="使用的 GPT 模型")
    args = ap.parse_args()

    # 1. 讀取 FAQ → 切段 → 向量化
    faq_text = pathlib.Path(args.kb).read_text(encoding="utf-8")
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    docs = splitter.split_text(faq_text)
    embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
    vect = FAISS.from_texts(docs, embeddings)

    # 2. 檢索相關段落
    retriever = vect.as_retriever(search_kwargs={"k": 3})
    rel_docs = [d.page_content for d in retriever.get_relevant_documents(args.query)]

    # 3. 組 prompt 並請 GPT 回答
    prompt = build_prompt(args.query, rel_docs)
    llm = OpenAI(model=args.model, temperature=0.2, openai_api_key=OPENAI_API_KEY)
    chain = load_qa_chain(llm, chain_type="stuff")
    reply = chain.run({"input_documents": [], "question": prompt}).strip()

    # 4. 儲存結果為 JSON
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump({
            "query": args.query,
            "answer": reply
        }, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
