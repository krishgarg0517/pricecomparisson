import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from db import insert_product, insert_price
from playwright.sync_api import sync_playwright


from playwright.sync_api import sync_playwright
import pandas as pd
from datetime import datetime

from db import insert_product, insert_price


# ⭐ MULTI CATEGORIES (Best for price tracking)
CATEGORIES = [
    "earbuds",
    "power bank",
    "coffee",
    "protein powder",
    "trimmer"
]

MAX_PRODUCTS = 100   # Safe start (DO NOT jump to 500 yet)


def scrape_amazon(search_query):

    data = []

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=False,
            slow_mo=100
        )

        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        )

        page = context.new_page()

        url = f"https://www.amazon.in/s?k={search_query}"

        print(f"\n🚀 Scraping category: {search_query}\n")

        page.goto(url, timeout=60000)

        page.wait_for_selector("div.s-main-slot")

        products = page.query_selector_all(
            "div.s-main-slot div[data-component-type='s-search-result']"
        )

        print(f" Found {len(products)} products\n")

        for product in products[:MAX_PRODUCTS]:

            try:

                # ✅ TITLE
                title_el = product.query_selector("h2 span")
                title = title_el.inner_text() if title_el else "N/A"

                if title == "N/A":
                    continue

                # ✅ BRAND (auto extracted)
                brand = title.split(" ")[0]

                # ✅ PRICE
                price_el = product.query_selector(".a-price-whole")
                price = price_el.inner_text() if price_el else None

                if price:
                    price = int(price.replace(",", ""))
                else:
                    continue   # skip products without price

                # ✅ LINK
                link_el = product.query_selector("h2 a")
                link = (
                    "https://www.amazon.in" + link_el.get_attribute("href")
                    if link_el else "N/A"
                )

                # ✅ IMAGE
                image_el = product.query_selector("img.s-image")
                image = image_el.get_attribute("src") if image_el else "N/A"

                # 🔥 INSERT INTO DATABASE
                product_id = insert_product(
                    title=title,
                    brand=brand,
                    category=search_query,
                    image_url=image
                )

                insert_price(
                    product_id=product_id,
                    platform="Amazon",
                    price=price,
                    url=link
                )

                print(" Inserted ->", title)

                # ✅ CSV Backup
                data.append({
                    "Title": title,
                    "Brand": brand,
                    "Category": search_query,
                    "Price": price,
                    "Link": link,
                    "Image": image,
                    "Marketplace": "Amazon",
                    "Scraped_Date": datetime.today().strftime('%Y-%m-%d')
                })

                # ⭐ HUMAN DELAY (VERY IMPORTANT)
                page.wait_for_timeout(2000)

            except Exception as e:
                print(" Skipping product due to error:", e)

        browser.close()

    return data


def save_data(data, category):

    if not data:
        return

    df = pd.DataFrame(data)

    file_name = f"data/amazon_{category}_{datetime.today().strftime('%Y-%m-%d')}.csv"

    df.to_csv(file_name, index=False)

    print(f"\n🎉 CSV saved -> {file_name}")


# ⭐ MAIN DRIVER
if __name__ == "__main__":

    for category in CATEGORIES:

        products = scrape_amazon(category)

        save_data(products, category)

    print("\n ALL CATEGORIES SCRAPED SUCCESSFULLY!\n")
