import tempfile
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def test_flipkart_selectors(product_url):
    data = {}
    """
    Test different CSS selectors on a Flipkart product page and return the results.
    """
    results = {}
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")  # Uncomment this to run headless once it works
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920x1080")
    options.add_argument("--headless=new")

    # Create a unique temporary directory for each Chrome instance
    user_data_dir = tempfile.mkdtemp()
    options.add_argument(f"--user-data-dir={user_data_dir}")

    service = service(executable_path="/usr/local/bin/chromedriver")  # <-- Use Service
    driver = webdriver.Chrome(service=service, options=options)  # <-- Pass service here

    try:
        print(f"Opening URL: {product_url}")
        driver.get(product_url)
        
        # Dictionary of selectors to test
        selectors_to_test = {
            "Title": "h1._6EBuvT span.VU-ZEz",
            "MRP (Fixed)": "div.yRaY8j.A6\\+E6v",
            "MRP (Attribute)": "div[class*='yRaY8j'][class*='A6+E6v']",
            "Special Price": "div.Nx9bqj.CxhGGd",
            "Discount": "div.UkUFwK.WW8yVX span",
            "Brand (from breadcrumb)": "span.B_NuCI",
            "Seller": "div.yeLeBC",
            "Type": "li._7eSDEz:first-child",
            "Highlights": "li._7eSDEz",
            "Product Description": "div.yN\\+eNk.w9jEaj",
            "Ratings Count": "span.Wphh3N > span:first-child",
            "Reviews Count": "span.Wphh3N > span:last-child",
            "Rating Value": "div.XQDdHH",
            "Pack Of Options": "ul.hSEbzK div.V3Zflw.QX54-Q.E1E-3Z",
            "General Rows": "div.GNDEQ-:nth-of-type(2) table._0ZhAN9 tr.WJdYP6"
        }
        
        for name, selector in selectors_to_test.items():
            try:
                if name == "Highlights":
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    results[name] = "; ".join([el.text.strip() for el in elements])
                else:
                    element = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    results[name] = element.text.strip()
            except Exception as e:
                results[name] = f"Error: {str(e)}"
    except Exception as e:
        results["error"] = str(e)
    finally:
        driver.quit()
    return results

if __name__ == "__main__":
    # Test URL - replace with any Flipkart product URL
    test_url = "https://www.flipkart.com/product/p/itme?pid=HGRG6YQWHJQUBNJD"
    
    result = test_flipkart_selectors(test_url)
    for key, value in result.items():
        print(f"{key}: {value}")
