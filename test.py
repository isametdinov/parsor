from playwright.sync_api import sync_playwright
import time
import random


def scrape_with_styles():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=[
                '--no-sandbox',
                '--disable-blink-features=AutomationControlled',
                '--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            ]
        )

        page = browser.new_page()
        page.add_init_script("""
            delete Object.getPrototypeOf(navigator).webdriver;
        """)

        try:
            url = "https://hayotbirja.uz/?tabid_procedures=2"
            page.goto(url, wait_until='networkidle', timeout=30000)
            print("Sahifa yuklandi, elementni kutmoqdaman...")
            time.sleep(random.uniform(3, 6))
            page.evaluate("window.scrollTo(0, 300)")
            time.sleep(2)

            # Wait for the main container
            page.wait_for_selector("div.ui-data-view.view_type_grid", timeout=30000)

            # Extract all CSS styles from the page
            all_styles = page.evaluate("""
                () => {
                    const styles = [];
                    for (let sheet of document.styleSheets) {
                        try {
                            for (let rule of sheet.cssRules) {
                                styles.push(rule.cssText);
                            }
                        } catch (e) {
                            // Skip external stylesheets due to CORS
                        }
                    }
                    return styles.join('\\n');
                }
            """)

            # Get the main content
            content = page.query_selector("div.ui-data-view.view_type_grid").inner_html()

            # Create a complete HTML document with styles
            html_content = f"""
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Аукционы - Hayotbirja.uz</title>
    <style>
        /* Reset and base styles */
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background-color: #f5f5f5;
            padding: 20px;
        }}

        /* Grid layout for auction items */
        .ui-data-view.view_type_grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
            max-width: 1200px;
            margin: 0 auto;
        }}

        /* Individual auction item styling */
        .ui-data-view-item {{
            background: white;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            transition: box-shadow 0.3s ease;
        }}

        .ui-data-view-item:hover {{
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        }}

        /* Auction header */
        .auction-header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 1px solid #f0f0f0;
        }}

        .auction-number {{
            font-size: 14px;
            color: #666;
            font-weight: 500;
        }}

        .auction-date {{
            font-size: 14px;
            color: #666;
        }}

        .auction-status {{
            background: #e8f5e8;
            color: #2d5a2d;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 500;
        }}

        /* Auction title */
        .auction-title {{
            font-size: 16px;
            font-weight: 600;
            color: #333;
            margin-bottom: 10px;
            line-height: 1.4;
        }}

        .auction-title a {{
            color: #0066cc;
            text-decoration: none;
        }}

        .auction-title a:hover {{
            text-decoration: underline;
        }}

        /* Organizer info */
        .organizer-info {{
            font-size: 14px;
            color: #666;
            margin-bottom: 15px;
            line-height: 1.4;
        }}

        /* Price and details grid */
        .auction-details {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            font-size: 14px;
        }}

        .detail-row {{
            display: flex;
            justify-content: space-between;
            padding: 5px 0;
        }}

        .detail-label {{
            color: #666;
            font-weight: 500;
        }}

        .detail-value {{
            color: #333;
            font-weight: 600;
        }}

        .price-value {{
            color: #d32f2f;
            font-weight: 700;
        }}

        .time-remaining {{
            color: #ff6b35;
            font-weight: 600;
        }}

        /* Items count badge */
        .items-count {{
            background: #0066cc;
            color: white;
            padding: 2px 6px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 600;
        }}

        /* Responsive design */
        @media (max-width: 768px) {{
            .ui-data-view.view_type_grid {{
                grid-template-columns: 1fr;
                gap: 15px;
                padding: 0 10px;
            }}

            .auction-details {{
                grid-template-columns: 1fr;
            }}
        }}

        /* Additional extracted styles */
        {all_styles}
    </style>
</head>
<body>
    <div class="ui-data-view view_type_grid">
        {content}
    </div>
</body>
</html>
            """

            # Save the styled HTML
            with open("styled_auctions.html", "w", encoding="utf-8") as f:
                f.write(html_content)

            print("✓ Muvaffaqiyat! styled_auctions.html ga saqlandi")

            # Also create a JSON version for easier data processing
            auction_data = page.evaluate("""
                () => {
                    const items = [];
                    const auctionElements = document.querySelectorAll('.ui-data-view-item');

                    auctionElements.forEach(item => {
                        const data = {};

                        // Extract auction number
                        const numberEl = item.querySelector('[class*="number"]');
                        if (numberEl) data.number = numberEl.textContent.trim();

                        // Extract title
                        const titleEl = item.querySelector('a');
                        if (titleEl) {
                            data.title = titleEl.textContent.trim();
                            data.link = titleEl.href;
                        }

                        // Extract all text content and parse details
                        const text = item.textContent;

                        // Extract prices and other details using regex
                        const priceMatch = text.match(/([0-9\\s]+\\.\\d{2})\\s*UZS/g);
                        if (priceMatch) {
                            data.prices = priceMatch;
                        }

                        // Extract time remaining
                        const timeMatch = text.match(/(\\d{2}:\\d{2}:\\d{2})/);
                        if (timeMatch) {
                            data.timeRemaining = timeMatch[1];
                        }

                        items.push(data);
                    });

                    return items;
                }
            """)

            # Save JSON data
            import json
            with open("auction_data.json", "w", encoding="utf-8") as f:
                json.dump(auction_data, f, ensure_ascii=False, indent=2)

            print("✓ JSON ma'lumotlar auction_data.json ga saqlandi")

        except Exception as e:
            print(f"Xatolik: {e}")
            print("VPN yoqilgan ekanligini tekshiring!")
            try:
                page.goto("https://httpbin.org/ip", timeout=10000)
                ip_info = page.text_content("body")
                print(f"Sizning IP: {ip_info}")
            except:
                print("IP ni aniqlab bo'lmadi")

        finally:
            time.sleep(3)
            browser.close()


if __name__ == "__main__":
    scrape_with_styles()
