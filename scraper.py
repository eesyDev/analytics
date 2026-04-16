import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}


def scrape_page(url: str, timeout: int = 12) -> dict:
    result = {
        "URL": url,
        "Status": None,
        "Title": "",
        "Title Length": 0,
        "Meta Description": "",
        "Meta Desc Length": 0,
        "H1": "",
        "H1 Count": 0,
        "H2 Count": 0,
        "H3 Count": 0,
        "Word Count": 0,
        "Images Total": 0,
        "Images No Alt": 0,
        "Canonical": "",
        "Has Schema": False,
        "Internal Links": 0,
        "External Links": 0,
        "Error": None,
    }
    try:
        r = requests.get(url, headers=HEADERS, timeout=timeout, allow_redirects=True)
        result["Status"] = r.status_code
        if r.status_code != 200:
            result["Error"] = f"HTTP {r.status_code}"
            return result

        soup = BeautifulSoup(r.content, "lxml")

        # Title
        title_tag = soup.find("title")
        if title_tag:
            result["Title"] = title_tag.get_text(strip=True)
            result["Title Length"] = len(result["Title"])

        # Meta description
        meta = soup.find("meta", {"name": re.compile(r"^description$", re.I)})
        if meta and meta.get("content"):
            result["Meta Description"] = meta["content"].strip()
            result["Meta Desc Length"] = len(result["Meta Description"])

        # Headings
        h1s = soup.find_all("h1")
        result["H1 Count"] = len(h1s)
        result["H1"] = h1s[0].get_text(strip=True)[:120] if h1s else ""
        result["H2 Count"] = len(soup.find_all("h2"))
        result["H3 Count"] = len(soup.find_all("h3"))

        # Word count (body text only)
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()
        body = soup.find("body")
        if body:
            text = body.get_text(separator=" ", strip=True)
            result["Word Count"] = len(text.split())

        # Images
        imgs = soup.find_all("img")
        result["Images Total"] = len(imgs)
        result["Images No Alt"] = sum(
            1 for img in imgs if not img.get("alt", "").strip()
        )

        # Canonical
        canonical = soup.find("link", {"rel": "canonical"})
        if canonical:
            result["Canonical"] = canonical.get("href", "")

        # Schema markup
        result["Has Schema"] = bool(
            soup.find("script", {"type": "application/ld+json"})
        )

        # Links
        domain = urlparse(url).netloc
        links = soup.find_all("a", href=True)
        internal = external = 0
        for a in links:
            href = a["href"]
            parsed = urlparse(href)
            if parsed.netloc in ("", domain):
                internal += 1
            elif parsed.scheme in ("http", "https"):
                external += 1
        result["Internal Links"] = internal
        result["External Links"] = external

    except requests.exceptions.Timeout:
        result["Error"] = "Timeout"
    except requests.exceptions.ConnectionError:
        result["Error"] = "Connection error"
    except Exception as e:
        result["Error"] = str(e)[:80]

    return result


def scrape_content_deep(url: str, timeout: int = 15) -> dict:
    """Extended scrape for AI content analysis — returns heading tree + full body text."""
    result = {
        "url": url,
        "title": "",
        "meta_desc": "",
        "headings": [],      # list of (level_str, text), e.g. [("H1", "..."), ("H2", "...")]
        "body_text": "",
        "word_count": 0,
        "paragraph_count": 0,
        "error": None,
    }
    try:
        r = requests.get(url, headers=HEADERS, timeout=timeout, allow_redirects=True)
        result_status = r.status_code
        if result_status != 200:
            result["error"] = f"HTTP {result_status}"
            return result

        soup = BeautifulSoup(r.content, "lxml")

        title_tag = soup.find("title")
        if title_tag:
            result["title"] = title_tag.get_text(strip=True)

        meta = soup.find("meta", {"name": re.compile(r"^description$", re.I)})
        if meta and meta.get("content"):
            result["meta_desc"] = meta["content"].strip()

        for tag in soup.find_all(["h1", "h2", "h3", "h4"]):
            text = tag.get_text(strip=True)[:150]
            if text:
                result["headings"].append((tag.name.upper(), text))

        for tag in soup(["script", "style", "nav", "footer", "header", "aside", "iframe"]):
            tag.decompose()

        body = soup.find("body")
        if body:
            result["paragraph_count"] = len(body.find_all("p"))
            result["body_text"] = body.get_text(separator="\n", strip=True)
            result["word_count"] = len(result["body_text"].split())

    except requests.exceptions.Timeout:
        result["error"] = "Timeout"
    except requests.exceptions.ConnectionError:
        result["error"] = "Connection error"
    except Exception as e:
        result["error"] = str(e)[:80]

    return result
