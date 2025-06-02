from flask import Flask, request, render_template_string
from scraper import test_flipkart_selectors

import io
import csv
import html
import json
from flask import Flask, request, render_template_string, send_file

app = Flask(__name__)

HTML_TEMPLATE = '''
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>Flipkart Product Scraper</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <!-- Google Fonts -->
    <link href="https://fonts.googleapis.com/css?family=Roboto:400,700&display=swap" rel="stylesheet">
    <style>
        body {
            font-family: 'Roboto', Arial, sans-serif;
            background: linear-gradient(120deg, #e0eafc 0%, #cfdef3 100%);
            min-height: 100vh;
            margin: 0;
            padding: 0;
        }
        .container {
            max-width: 850px;
            margin: 40px auto;
            background: #fff;
            border-radius: 18px;
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.15);
            padding: 36px 40px 30px 40px;
        }
        h2 {
            color: #2874f0;
            letter-spacing: 1px;
            margin-bottom: 12px;
            font-weight: 700;
            font-size: 2.2rem;
        }
        form {
            margin-bottom: 20px;
        }
        label {
            font-weight: 500;
            color: #222;
        }
        input[type="text"] {
            width: 70%;
            padding: 10px;
            margin: 8px 0 16px 0;
            border: 1px solid #b5c7d3;
            border-radius: 8px;
            font-size: 1rem;
            background: #f8fafc;
            transition: border 0.3s;
        }
        input[type="text"]:focus {
            border: 1.5px solid #2874f0;
            outline: none;
        }
        input[type="submit"], button {
            background: linear-gradient(90deg, #2874f0 0%, #0059b3 100%);
            color: #fff;
            border: none;
            border-radius: 8px;
            padding: 10px 26px;
            font-size: 1.08rem;
            font-weight: 600;
            cursor: pointer;
            margin-top: 5px;
            box-shadow: 0 2px 8px rgba(40,116,240,0.09);
            transition: background 0.2s;
        }
        input[type="submit"]:hover, button:hover {
            background: linear-gradient(90deg, #0059b3 0%, #2874f0 100%);
        }
        .note {
            font-size: 0.97rem;
            color: #555;
            margin-bottom: 18px;
            display: block;
        }
        .error {
            color: #d8000c;
            background: #ffeded;
            border-left: 5px solid #d8000c;
            padding: 10px 15px;
            margin-bottom: 18px;
            border-radius: 6px;
            font-weight: 500;
        }
        .product-card {
            background: #f7faff;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(40,116,240,0.07);
            margin-bottom: 30px;
            padding: 22px 18px 14px 18px;
            border: 1.5px solid #e3eaf2;
            transition: box-shadow 0.2s;
        }
        .product-card:hover {
            box-shadow: 0 6px 20px rgba(40,116,240,0.13);
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 8px;
            background: transparent;
        }
        th, td {
            padding: 10px 8px;
            text-align: left;
        }
        th {
            background: #2874f0;
            color: #fff;
            font-weight: 600;
            border-radius: 4px 4px 0 0;
        }
        tr:nth-child(even) {
            background: #e9f0fa;
        }
        tr:nth-child(odd) {
            background: #f7faff;
        }
        @media (max-width: 700px) {
            .container {
                padding: 18px 6vw 18px 6vw;
            }
            input[type="text"] {
                width: 100%;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h2>Flipkart Product Scraper</h2>
        <form method="post">
            <label><b>Enter either:</b></label><br>
            <label>Product URL:</label>
            <input type="text" name="product_url" placeholder="https://www.flipkart.com/..." /><br>
            <label><b>OR</b></label><br>
            <label>Product ID:</label>
            <input type="text" name="product_id" placeholder="e.g., HGRH7VYWCYKDTF4Y, HGRH7VYWCYKDTF4Z" /><br>
            <span class="note">(Separate multiple IDs with spaces or commas)</span>
            <input type="submit" value="Scrape">
        </form>
        {% if error %}
            {% for err in error %}
                <div class="error">{{ err }}</div>
            {% endfor %}
        {% endif %}
        {% if results %}
            <div class="results-header">
                <form method="post" action="/download" style="display:inline;">
                    <input type="hidden" name="csv_data" value='{{ results|tojson }}'>
                    <button type="submit" class="download-all-btn">⬇️ Download CSV (All Products)</button>
               </form>
            </div>
            <h3>Results:</h3>
            {% for product in results %}
                <div class="product-card">
                    <table>
                        <tr><th>Field</th><th>Value</th></tr>
                        {% for key, value in product.items() %}
                            <tr>
                                <td>{{ key }}</td>
                                <td style="word-break: break-all;">{{ value }}</td>
                            </tr>
                        {% endfor %}
                    </table>
                </div>
            {% endfor %}
            <form method="post" action="/download">
                <input type="hidden" name="csv_data" value='{{ results|tojson }}'>
                <button type="submit">Download CSV (All Products)</button>
            </form>
        {% endif %}
    </div>
</body>
</html>
'''


@app.route('/', methods=['GET', 'POST'])
def index():
    results = []
    errors = []  # Use a list for multiple errors
    if request.method == 'POST':
        product_url = request.form.get('product_url', '').strip()
        product_id = request.form.get('product_id', '').strip()

        if not product_url and not product_id:
            errors.append("❌ Please enter a Product URL or Product ID.")
        else:
            # Process Product IDs
            if product_id:
                # Split and filter empty strings
                product_ids = [pid.strip() for pid in product_id.replace(',', ' ').split() if pid.strip()]
                for pid in product_ids:
                    url = f"https://www.flipkart.com/product/p/itme?pid={pid}"
                    try:
                        product_data = test_flipkart_selectors(url)
                        product_data['Product ID'] = pid  # Add ID to results
                        results.append(product_data)
                    except Exception as e:
                        errors.append(f"Failed to scrape {pid}: {str(e)}")
            
            # Process Product URL (only if no product IDs provided)
            elif product_url:
                try:
                    product_data = test_flipkart_selectors(product_url)
                    results.append(product_data)
                except Exception as e:
                    errors.append(f"Failed to scrape URL: {str(e)}")

    return render_template_string(HTML_TEMPLATE, results=results, error=errors)

    
@app.route('/download', methods=['POST'])
def download():
    try:
        csv_data = html.unescape(request.form.get('csv_data', ''))
        all_products = json.loads(csv_data)
        
        # Create CSV with one row per product
        si = io.StringIO()
        writer = csv.writer(si)
        
        # Write header (use keys from first product)
        if all_products:
            headers = ["Product ID"] + list(all_products[0].keys())
            headers.remove("Product ID")  # Avoid duplicate if already present
            writer.writerow(["Product ID"] + headers)
            
            # Write data
            for product in all_products:
                pid = product.get("Product ID", "")
                row = [pid] + [product.get(key, "") for key in headers]
                writer.writerow(row)
        
        si.seek(0)
        return send_file(
            io.BytesIO(si.getvalue().encode('utf-8')),
            mimetype='text/csv',
            as_attachment=True,
            download_name='flipkart_products.csv'
        )
    except Exception as e:
        return f"Download failed: {str(e)}", 400



if __name__ == '__main__':
    app.run(debug=True, port=5002)