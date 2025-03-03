import asyncio
import aiohttp
import time
import streamlit as st
import pandas as pd

# ------------------------------------------------- ---------------
# Asynchronous Fetch Function
# ----------------------------------------------------------------
async def fetch(url: str, session: aiohttp.ClientSession, semaphore: asyncio.Semaphore):
    """
    Asynchronously fetch the content from a given URL.
    
    A semaphore is used to limit the number of concurrent requests,
    preventing resource exhaustion when scaling to many URLs.
    """
    async with semaphore:
        try:
            async with session.get(url) as response:
                text = await response.text()
                # Return a dictionary with key info about the URL fetch
                return {
                    "URL": url,
                    "Status": response.status,
                    "Content Length": len(text)
                }
        except Exception as e:
            return {"URL": url, "Status": "Error", "Content Length": 0, "Error": str(e)}

# ----------------------------------------------------------------
# Asynchronous Scraper Runner
# ----------------------------------------------------------------
async def run_scraper(urls, concurrency_limit=10):
    """
    Run the asynchronous scraper on a list of URLs with a specified concurrency limit.
    
    Scalability Explanation:
      - Uses asyncio.gather to schedule many I/O-bound tasks concurrently.
      - Limits the number of concurrent requests using asyncio.Semaphore.
      - Efficiently handles hundreds or thousands of requests without spawning extra threads.
    """
    semaphore = asyncio.Semaphore(concurrency_limit)
    async with aiohttp.ClientSession() as session:
        tasks = [asyncio.create_task(fetch(url, session, semaphore)) for url in urls]
        results = await asyncio.gather(*tasks)
    return results

# ----------------------------------------------------------------
# Streamlit Dashboard
# ----------------------------------------------------------------
def main():
    st.title("Scalable Async Web Scraper")
    st.markdown(
        """
        This demo showcases how to build a scalable web scraper using asynchronous programming.
        The scraper fetches multiple URLs concurrently using `aiohttp` and `asyncio`.
        
        **Scalability Highlights:**
        - **Asynchronous I/O:** Non-blocking HTTP requests allow the system to handle many URLs.
        - **Concurrency Control:** A semaphore limits concurrent requests to avoid overloading resources.
        - **Efficient Resource Usage:** Runs many I/O-bound tasks with minimal overhead.
        """
    )

    # Sidebar: Settings for the scraper
    st.sidebar.header("Scraper Settings")
    url_input = st.sidebar.text_area(
        "Enter URLs (one per line)",
        value="https://www.example.com\nhttps://www.python.org\nhttps://www.asyncio.org"
    )
    concurrency_limit = st.sidebar.slider("Concurrency Limit", min_value=1, max_value=20, value=5)
    start_scraping = st.sidebar.button("Start Scraping")

    if start_scraping:
        # Process URL input into a list
        urls = [line.strip() for line in url_input.splitlines() if line.strip()]
        st.info(f"Starting to scrape **{len(urls)}** URLs with a concurrency limit of **{concurrency_limit}**...")

        start_time = time.time()
        with st.spinner("Scraping in progress..."):
            results = asyncio.run(run_scraper(urls, concurrency_limit=concurrency_limit))
        elapsed = time.time() - start_time

        st.success(f"Scraping completed in {elapsed:.2f} seconds.")

        # Convert results to a DataFrame for a clean display
        df = pd.DataFrame(results)
        st.markdown("### Scraping Results")
        st.dataframe(df)

        # Additional detailed display for errors and success messages
        for res in results:
            if res.get("Status") == "Error":
                st.error(f"Error fetching {res.get('URL')}: {res.get('Error')}")
            else:
                st.write(
                    f"Fetched **{res.get('URL')}** with status **{res.get('Status')}** and content length **{res.get('Content Length')}**."
                )

if __name__ == '__main__':
    main()
