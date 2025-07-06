# arxiv_api.py

from fastapi import FastAPI, Query
from typing import List
from pydantic import BaseModel
import requests
from bs4 import BeautifulSoup

app = FastAPI()

# =========================
# 🧠 定义返回格式（标准化输出）
# =========================
class ArxivResult(BaseModel):
    title: str
    authors: str
    date: str
    abstract: str
    link: str

# =========================
# 🚀 核心爬虫逻辑（基本不变）
# =========================
def scrape_arxiv(url: str) -> ArxivResult:
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(resp.text, 'html.parser')

        title = soup.find("h1", class_="title").text.replace("Title:", "").strip()
        authors = soup.find("div", class_="authors").text.replace("Authors:", "").strip()
        abstract = soup.find("blockquote", class_="abstract").text.replace("Abstract:", "").strip()
        date = soup.find("div", class_="dateline").text.strip()

        return ArxivResult(
            title=title,
            authors=authors,
            date=date,
            abstract=abstract,
            link=url
        )
    except Exception as e:
        return ArxivResult(
            title="",
            authors="",
            date="",
            abstract=f"[抓取失败: {e}]",
            link=url
        )

# =========================
# ✅ API 接口（支持多个 URL）
# =========================
@app.get("/crawl", response_model=List[ArxivResult])
def crawl_arxiv(
    urls: List[str] = Query(..., description="arXiv 链接列表")
):
    return [scrape_arxiv(url) for url in urls]
