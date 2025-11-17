import urllib
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
from urllib.parse import urljoin
import os
import re

# === Proxy Configuration (set these if needed) ===
USE_PROXY = True  # Set to False if you want to bypass proxy
PROXY_STRING = 'http://brd-customer-hl_15ca11df-zone-datacenter_proxy2:wc9jrb60kku2@brd.superproxy.io:33335'
PROXIES = {
    'http': PROXY_STRING,
    'https': PROXY_STRING,
}

def test_proxy():
    test_url = 'https://geo.brdtest.com/welcome.txt?product=dc&method=native'
    try:
        opener = urllib.request.build_opener(
            urllib.request.ProxyHandler({'http': PROXY_STRING, 'https': PROXY_STRING})
        )
        print("Proxy Test Response:", opener.open(test_url).read().decode())
    except Exception as e:
        print(f"Proxy test failed: {e}")

# === Utility Functions ===

def clean_text(text):
    text = re.sub(r'[\t\r\n]+', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def normalize_filename(name):
    return name.lower().replace("-", "").replace(" ", "").replace("_", "")

def extract_brand_name(product_name):
    known_brands = [
        'Acer', 'ADATA', 'Addlink', 'Aigo', 'AMD', 'Anaconda', 'Aorus', 'Apacer', 'Apple', 'Asgard', 'Asura',
        'ASUS', 'ASUS ROG', 'Ayaneo', 'Biostar', 'Biwin', 'CFD Gaming', 'Colorful', 'Corsair', 'Crucial',
        'DapuStor', 'Dera', 'Digifast', 'Digma', 'Drevo', 'Enmotus', 'Fanxiang', 'FlumeIO', 'Framework', 'Galax',
        'Gigabyte', 'Godram', 'HighPoint', 'Hikvision', 'HippStor', 'HP', 'Huawei', 'HyperX', 'Inland', 'Intel',
        'IRDM', 'Kingspec', 'Kingston', 'Kioxia', 'Klevv', 'Kodak', 'Kootion', 'Lenovo', 'Lexar', 'Longsys',
        'Magix', 'Mancer', 'Mega Electronics Fastro', 'Memblaze', 'Meta', 'Micron', 'Microsoft', 'MiWhole',
        'MLD', 'Movespeed', 'MSI', 'Mushkin', 'Neo Forza', 'Netac', 'Nextorage', 'OCZ', 'Orico', 'Patriot',
        'Phison', 'Pichau', 'Plextor', 'PNY', 'Ramaxel', 'Raspberry Pi', 'Redragon', 'Reletech', 'Rise Mode',
        'RZX', 'Sabrent', 'Samsung', 'SanDisk', 'ScaleFlux', 'Seagate', 'Silicon Motion', 'Silicon Power',
        'SK Hynix', 'Solidigm', 'Sony', 'SSD MW Informatica', 'SSD Peperaio', 'SSSTC', 'SSTC', 'Synology',
        'Teamgroup', 'Teracle', 'TLET', 'Toshiba', 'Transcend', 'Union Memory', 'Valve', 'VisionTek',
        'Western Digital', 'Wicgtyp', 'Xbox Series X', 'XPG', 'Xraydisk', 'Zadak', 'Zhitai', 'Zircon']

    for brand in sorted(known_brands, key=len, reverse=True):
        if product_name.lower().startswith(brand.lower()):
            return brand
    return product_name.split()[0]

# === Crawl SSD Updates from Site ===

def crawl_ssd_updates_from_aside(url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers, proxies=PROXIES if USE_PROXY else None)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the page: {e}")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    aside = soup.find('aside', class_='changes')
    if not aside:
        return None

    table = aside.find('table')
    if not table:
        return None

    rows = table.find_all('tr')
    data = []
    seen = set()
    today = datetime.today()
    seven_days_ago = today - timedelta(days=10)
    current_date = None

    for row in rows:
        th = row.find('th')
        date_text_raw = th.get_text(strip=True) if th else ''
        if date_text_raw and date_text_raw != '\xa0':
            try:
                current_date = datetime.strptime(f"{date_text_raw} {today.year}", "%b %d %Y")
                if current_date > today:
                    current_date = current_date.replace(year=current_date.year - 1)
            except Exception:
                current_date = None

        if not current_date or current_date < seven_days_ago:
            continue

        td = row.find('td')
        if not td:
            continue

        a_tag = td.find('a')
        if a_tag:
            product_name = clean_text(a_tag.get_text(strip=True))
            href = a_tag.get('href')
            full_url = urljoin(url, href)
        else:
            product_name = clean_text(td.get_text(strip=True))
            full_url = ""

        if not product_name:
            continue

        key = (product_name, full_url if full_url else product_name)
        if key in seen:
            continue
        seen.add(key)

        data.append({
            'Root Object': extract_brand_name(product_name),
            'Object': product_name,
            'URL': full_url,
            'Product Size': ""
        })

    return pd.DataFrame(data) if data else None

# === Fetch and Parse SSD Spec Page ===

def fetch_ssd_specs(url):
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://www.google.com/",
        "Accept-Language": "en-US,en;q=0.9"
    }
    response = requests.get(url, headers=headers, proxies=PROXIES if USE_PROXY else None)
    if response.status_code == 403:
        raise Exception("Access denied (403 Forbidden).")
    response.raise_for_status()
    return response.text

def extract_text_before_link(td):
    texts = []
    for content in td.contents:
        if getattr(content, 'name', None) == 'a':
            break
        if isinstance(content, str):
            texts.append(content)
        elif hasattr(content, 'get_text'):
            texts.append(content.get_text())
    return clean_text(''.join(texts))

def parse_ssd_spec(html):
    soup = BeautifulSoup(html, "html.parser")
    sections = soup.find_all("section", class_="details")
    category_data = {}
    product_size = ""

    for section in sections:
        header = section.find("h1")
        if not header:
            continue
        section_title = clean_text(header.text.strip())
        table = section.find("table")
        if not table:
            continue

        specs = {}
        for row in table.find_all("tr"):
            th = row.find("th")
            td = row.find("td")
            if th and td:
                key = clean_text(th.text.strip().replace(":", ""))
                if section_title.lower() == "controller":
                    value = extract_text_before_link(td)
                    if "find more drives" in value.lower():
                        continue
                else:
                    value = clean_text(" | ".join(td.stripped_strings))

                if section_title.lower() == "solid-state-drive" and key.lower() == "capacity":
                    match = re.search(r"(\d+\.?\d*) ?TB", value, re.IGNORECASE)
                    if match:
                        product_size = f"{match.group(1)} TB"
                        value = product_size
                    else:
                        product_size = value
                specs[key] = value

        if specs:
            category_data[section_title] = specs

    return category_data, product_size

# === Main Execution ===

if __name__ == "__main__":
    base_url = "https://www.techpowerup.com/ssd-specs/"
    ssd_df = crawl_ssd_updates_from_aside(base_url)

    if ssd_df is not None:
        print("\n--- Recent SSD Database Updates (Last 7–10 Days) ---\n")
        print(ssd_df.to_string(index=False))

        os.makedirs("ssd_data", exist_ok=True)

        category_files = {}
        updated_rows = []

        for _, row in ssd_df.iterrows():
            print(f"\n Fetching specifications for: {row['Object']}")
            try:
                html = fetch_ssd_specs(row['URL']) if row['URL'] else None
                product_data, product_size = parse_ssd_spec(html) if html else ({}, "")
                row["Product Size"] = product_size
                updated_rows.append(row)

                for category, specs in product_data.items():
                    category_key = normalize_filename(category)
                    file_name = f"{category_key}.csv"

                    entry = {
                        "Root Object": row["Root Object"],
                        "Object": row["Object"],
                        "Product Size": product_size,
                        "URL": row["URL"]
                    }
                    entry.update({f"{category}.{key}": value for key, value in specs.items()})

                    if file_name not in category_files:
                        category_files[file_name] = []

                    category_files[file_name].append(entry)

                print(f"Data saved for: {row['Object']} (Product Size: {product_size})")

            except Exception as e:
                print(f"Error fetching data for {row['Object']}: {e}")

        # Save URLs.csv
        pd.DataFrame(updated_rows)[['Root Object', 'Object', 'Product Size', 'URL']].to_csv("ssd_data/URLs.csv", index=False)

        # Save category-wise CSVs
        for file_name, entries in category_files.items():
            df = pd.DataFrame(entries)
            df.to_csv(f"ssd_data/{file_name}", index=False)

        # Save RootObject.csv
        root_object_df = pd.DataFrame(updated_rows)[['Root Object', 'Object']].drop_duplicates().sort_values(by=['Root Object', 'Object'])
        root_object_df.to_csv("ssd_data/RootObject.csv", index=False)

    else:
        print("\nNo recent updates found.")
