import re
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/151.0.0.0 Safari/537.36"
    )
}

REQUEST_TIMEOUT = 30


# ============================================================
# KNOWN DOCUMENTATION URL OVERRIDES
# ============================================================

KNOWN_URLS = {

    # --------------------------------------------------------
    # Previously failed apps
    # --------------------------------------------------------

    "Salesforce":
        "https://developer.salesforce.com/docs",

    "SendGrid":
        "https://www.twilio.com/docs/sendgrid",

    "Twilio SendGrid":
        "https://www.twilio.com/docs/sendgrid",

    "Salesforce Commerce Cloud":
        "https://developer.salesforce.com/docs/commerce",

    "Magento / Adobe Commerce":
        "https://developer.adobe.com/commerce/",

    "Adobe Commerce":
        "https://developer.adobe.com/commerce/",

    "fanbasis":
        "https://docs.fanbasis.com/",

    "Commas (formerly FanBasis)":
        "https://docs.fanbasis.com/",

    "SE Ranking":
        "https://seranking.com/api/",

    "Neo4j":
        "https://neo4j.com/docs/",

    "Binance":
        "https://developers.binance.com/docs/",

    "Paygent Connect":
        "https://www.nmi.com/",
}


# ============================================================
# URL NORMALIZATION
# ============================================================

def normalize_url(url: str) -> str:
    """
    Normalize a URL before fetching.
    """

    if not url:
        return ""

    url = url.strip()

    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    return url.rstrip("/")


# ============================================================
# FETCH PAGE
# ============================================================

def fetch_page(url: str) -> str:
    """
    Fetch a webpage and return cleaned readable text.
    """

    url = normalize_url(url)

    response = requests.get(
        url,
        headers=HEADERS,
        timeout=REQUEST_TIMEOUT,
        allow_redirects=True,
    )

    response.raise_for_status()

    soup = BeautifulSoup(
        response.text,
        "html.parser",
    )

    # Remove elements that usually do not contain
    # useful documentation content.
    for element in soup([
        "script",
        "style",
        "noscript",
        "svg",
        "nav",
        "footer",
        "header",
        "aside",
    ]):
        element.decompose()

    text = soup.get_text(
        separator=" ",
        strip=True,
    )

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text


# ============================================================
# FETCH URL WITH RETRIES
# ============================================================

def fetch_with_retry(
    url: str,
    retries=3,
):
    """
    Fetch a URL with retry handling for temporary
    network failures.
    """

    last_error = None

    for attempt in range(
        1,
        retries + 1,
    ):

        try:

            return fetch_page(url)

        except requests.RequestException as e:

            last_error = e

            print(
                f"  Fetch attempt "
                f"{attempt}/{retries} failed: "
                f"{str(e)[:250]}"
            )

            if attempt < retries:

                import time

                time.sleep(3)

    raise last_error


# ============================================================
# DISCOVER LINKS
# ============================================================

def discover_links(
    url: str,
    keywords=None,
    max_links=6,
):
    """
    Discover relevant links from an official
    documentation page.

    Only links from the same domain are considered.
    """

    if keywords is None:

        keywords = [
            "authentication",
            "authenticate",
            "oauth",
            "api",
            "developer",
            "developers",
            "mcp",
            "pricing",
            "plans",
            "getting-started",
            "getting_started",
            "quickstart",
            "reference",
            "documentation",
            "docs",
            "sdk",
            "webhook",
        ]

    url = normalize_url(url)

    response = requests.get(
        url,
        headers=HEADERS,
        timeout=REQUEST_TIMEOUT,
        allow_redirects=True,
    )

    response.raise_for_status()

    soup = BeautifulSoup(
        response.text,
        "html.parser",
    )

    base_domain = urlparse(
        response.url
    ).netloc.lower()

    candidates = []

    for link in soup.find_all(
        "a",
        href=True,
    ):

        href = link["href"].strip()

        if not href:
            continue

        if href.startswith("#"):
            continue

        if href.startswith(
            (
                "mailto:",
                "javascript:",
                "tel:",
            )
        ):
            continue

        full_url = urljoin(
            response.url,
            href,
        )

        parsed = urlparse(full_url)

        if parsed.scheme not in (
            "http",
            "https",
        ):
            continue

        link_domain = parsed.netloc.lower()

        # Same domain.
        if link_domain != base_domain:
            continue

        full_url = full_url.rstrip("/")

        # Remove fragments.
        full_url = full_url.split("#")[0]

        # GitHub version aliases.
        full_url = full_url.replace(
            "/en/free-pro-team@latest",
            "/en",
        )

        link_text = link.get_text(
            " ",
            strip=True,
        ).lower()

        combined = (
            f"{link_text} "
            f"{full_url.lower()}"
        )

        score = 0

        for keyword in keywords:

            if keyword in combined:
                score += 1

        # High-value pages.
        if any(
            value in combined
            for value in [
                "getting-started",
                "getting_started",
                "quickstart",
            ]
        ):
            score += 3

        if any(
            value in combined
            for value in [
                "authentication",
                "authenticate",
            ]
        ):
            score += 3

        if "oauth" in combined:
            score += 2

        if "pricing" in combined:
            score += 2

        if "mcp" in combined:
            score += 4

        if "api" in combined:
            score += 2

        if "reference" in combined:
            score += 2

        if "sdk" in combined:
            score += 2

        # Penalize huge permission/reference pages.
        if "endpoints-available" in combined:
            score -= 5

        if "permissions-required" in combined:
            score -= 5

        if score > 0:

            candidates.append(
                (
                    score,
                    full_url,
                    link_text,
                )
            )

    candidates.sort(
        key=lambda item: item[0],
        reverse=True,
    )

    results = []

    seen = set()

    for _, link_url, link_text in candidates:

        if link_url in seen:
            continue

        seen.add(link_url)

        results.append(
            {
                "url": link_url,
                "title": link_text,
            }
        )

        if len(results) >= max_links:
            break

    return results


# ============================================================
# CLASSIFY DOCUMENT
# ============================================================

def classify_document(
    url: str,
    title: str = "",
) -> str:

    value = (
        f"{url} {title}"
    ).lower()

    # MCP FIRST
    if "mcp" in value:
        return "mcp"

    # Authentication
    if any(
        keyword in value
        for keyword in [
            "authentication",
            "authenticate",
            "oauth",
            "auth",
            "credential",
            "token",
            "api-key",
            "api_key",
            "access-token",
            "access_token",
        ]
    ):
        return "authentication"

    # Pricing / access
    if any(
        keyword in value
        for keyword in [
            "pricing",
            "plans",
            "billing",
            "subscription",
            "commercial",
            "enterprise",
        ]
    ):
        return "access"

    # API
    if any(
        keyword in value
        for keyword in [
            "api",
            "reference",
            "endpoint",
            "graphql",
            "rest",
            "sdk",
            "webhook",
        ]
    ):
        return "api"

    return "general"


# ============================================================
# TRUNCATE TEXT
# ============================================================

def truncate_text(
    text: str,
    max_chars=20000,
):

    if len(text) <= max_chars:
        return text

    return (
        text[:max_chars]
        + "\n[DOCUMENT TRUNCATED]"
    )


# ============================================================
# GET KNOWN URL
# ============================================================

def get_known_url(
    app_name: str,
    root_url: str,
):
    """
    Return a known official documentation URL
    when available.
    """

    if app_name in KNOWN_URLS:

        return KNOWN_URLS[
            app_name
        ]

    return normalize_url(root_url)


# ============================================================
# RETRIEVE DOCUMENT BUNDLE
# ============================================================

def retrieve_document_bundle(
    root_url: str,
    max_links=6,
    app_name=None,
):
    """
    Retrieve the root documentation page and
    several relevant official documentation pages.

    Supports:
    - Known URL overrides
    - Redirects
    - Retry handling
    - Link discovery
    - Documentation classification
    """

    documents = []

    # --------------------------------------------------------
    # Resolve URL
    # --------------------------------------------------------

    if app_name:

        actual_root = get_known_url(
            app_name,
            root_url,
        )

        if actual_root != normalize_url(root_url):

            print(
                f"  Using documentation override: "
                f"{actual_root}"
            )

    else:

        actual_root = normalize_url(
            root_url
        )

    # --------------------------------------------------------
    # Root documentation
    # --------------------------------------------------------

    print(
        f"Fetching root documentation: "
        f"{actual_root}"
    )

    try:

        root_text = fetch_with_retry(
            actual_root
        )

        documents.append(
            {
                "url": actual_root,
                "title": "Root documentation",
                "category": classify_document(
                    actual_root,
                    "Root documentation",
                ),
                "text": root_text,
            }
        )

    except Exception as e:

        print(
            f"Failed to fetch root page: "
            f"{e}"
        )

    # --------------------------------------------------------
    # Discover links
    # --------------------------------------------------------

    try:

        discovered = discover_links(
            actual_root,
            max_links=max_links,
        )

    except Exception as e:

        print(
            f"Link discovery failed: "
            f"{e}"
        )

        discovered = []

    # --------------------------------------------------------
    # Fetch discovered pages
    # --------------------------------------------------------

    for item in discovered:

        url = item["url"]

        title = item["title"]

        if normalize_url(url) == normalize_url(
            actual_root
        ):
            continue

        # Avoid duplicates.
        existing_urls = {
            document["url"]
            for document in documents
        }

        if url in existing_urls:
            continue

        try:

            print(
                f"  Fetching: {url}"
            )

            text = fetch_with_retry(
                url
            )

            category = classify_document(
                url,
                title,
            )

            documents.append(
                {
                    "url": url,
                    "title": title,
                    "category": category,
                    "text": text,
                }
            )

        except Exception as e:

            print(
                f"  Skipped {url}: "
                f"{str(e)[:300]}"
            )

    # --------------------------------------------------------
    # If root failed but discovered pages worked,
    # still return discovered pages.
    # --------------------------------------------------------

    return documents


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    url = (
        "https://docs.github.com/en/rest"
    )

    print(
        f"Testing retriever with: {url}"
    )

    documents = retrieve_document_bundle(
        url,
        max_links=6,
        app_name="GitHub",
    )

    print(
        f"\nCollected "
        f"{len(documents)} documents"
    )

    print(
        "\nDocument classification:"
    )

    for index, document in enumerate(
        documents,
        start=1,
    ):

        print(
            f"{index}. "
            f"[{document['category']}] "
            f"{document['url']}"
        )

        print(
            f"   Characters: "
            f"{len(document['text'])}"
        )