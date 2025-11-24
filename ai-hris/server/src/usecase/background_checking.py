from playwright.sync_api import sync_playwright
from openai import AzureOpenAI
import time
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv

load_dotenv()

#linkedin profile scraping (can only be professional accounts)
def scrape_linkedin_description(url: str) -> str:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        ))
        page = context.new_page()
        print(f"Visiting {url} ...")
        
        try:
            page.goto(url, timeout=20000)
            page.wait_for_timeout(3000)
        except Exception as e:
            print(f"Error visiting LinkedIn page: {e}")
            browser.close()
            return "Failed to load the page."

        html = page.content()
        browser.close()
        context.close()

    # Parse the HTML to extract description
    soup = BeautifulSoup(html, 'html.parser')
    description_tag = soup.find('p', class_='break-words')
    if not description_tag:
        description_tag = soup.find('div', class_='break-words')

    description = description_tag.get_text(strip=True) if description_tag else "Description not found"
    return description

#click the user's tweets
def scrape_first_n_tweets_from_profile(username: str, n: int = 5):
    tweets_content = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(viewport={"width": 1280, "height": 1080})
        page = context.new_page()

        page.goto(f"https://x.com/{username}")
        page.wait_for_selector("[data-testid='primaryColumn']", timeout=15000)

        tweet_links = set()

        while len(tweet_links) < n:
            elements = page.query_selector_all("article [href*='/status/']")
            for e in elements:
                href = e.get_attribute("href")
                if href and href.startswith(f"/{username}/status/"):
                    tweet_links.add(f"https://x.com{href}")
                if len(tweet_links) >= n:
                    break
            page.mouse.wheel(0, 1000)
            time.sleep(1.5)

        print(f"\nFound {len(tweet_links)} tweet URLs. Scraping full content...\n")

        for link in list(tweet_links)[:n]:
            content = scrape_tweet_content(link, context)
            tweets_content.append((link, content))

        browser.close()

    return tweets_content

#scrape tweet content from user
def scrape_tweet_content(url: str, context) -> dict:
    _xhr_calls = []

    def intercept_response(response):
        if response.request.resource_type == "xhr":
            _xhr_calls.append(response)

    page = context.new_page()
    page.on("response", intercept_response)
    page.goto(url)
    try:
        page.wait_for_selector("[data-testid='tweet']", timeout=2000)
    except Exception as e:
        print(f"Timeout waiting for tweet selector on {url}: {e}")
        page.close()
        return {"text": "Tweet not found.", "images": []}

    time.sleep(2)

    tweet_calls = [f for f in _xhr_calls if "TweetResultByRestId" in f.url]
    tweet_text = "Tweet not found."
    for xhr in tweet_calls:
        try:
            data = xhr.json()
            tweet_text = data['data']['tweetResult']['result']['legacy']['full_text']
            break
        except Exception as e:
            print(f"Failed to extract tweet text on {url}: {e}")

    image_elements = page.query_selector_all("article [data-testid='tweetPhoto'] img")
    images = []
    for img in image_elements:
        src = img.get_attribute("src")
        if src:
            images.append(src)

    page.close()

    return {"text": tweet_text, "images": images}

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

DEPLOYMENT_NAME = "gpt-4.1-mini"

def analyze_sentiment_llm(text: str) -> str:
    prompt = (
        "Analyze the sentiment of the following text. "
        "Respond strictly with one of: 'Positive', 'Negative', or 'Neutral'. "
        "You're a very strict investigator confident with your classification. "
        "Do not add explanations or extra text.\n\n"
        f"Text:\n\"{text}\""
    )

    response = client.chat.completions.create(
        model=DEPLOYMENT_NAME,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a sentiment analysis assistant that must strictly classify sentiment as 'Positive', 'Negative', or 'Neutral' only."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.0,
    )
    return response.choices[0].message.content.strip()


if __name__ == "__main__":
    linkedin_description = scrape_linkedin_description("https://www.linkedin.com/company/microsoft/")
    tweet_set = set()
    sentiment_counts = {"Negative": 0, "Neutral": 0, "Positive": 0}
    print(linkedin_description)
    sentiment_counts[analyze_sentiment_llm(linkedin_description)] += 1
    # #dummy data tryout
    tweets = scrape_first_n_tweets_from_profile("elonmusk", n=5)

    for url, content in tweets:
        text = content["text"]
        images = content["images"]

        # Use text+images as a tuple to avoid duplicates
        tweet_set.add((text, tuple(images)))

    for text, images in tweet_set:
        sentiment = analyze_sentiment_llm(text)
        sentiment_counts[sentiment] += 1

    print("Sentiment summary:", sentiment_counts)
    max_sentiment = max(sentiment_counts, key=sentiment_counts.get)
    print(f"Sentiment Conclusion: {max_sentiment}")

