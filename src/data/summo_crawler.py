import re
import time
import random
import pandas as pd

from pathlib import Path
from datetime import datetime
from collections import defaultdict

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager


# =========================
# 配置
# =========================

BASE_URL = (
    "https://suumo.jp/jj/chintai/ichiran/FR301FC001/"
    "?ar=030&bs=040&ta=13&sc={sc}"
    "&cb=0.0&ct=9999999&et=9999999&cn=9999999"
    "&mb=0&mt=9999999"
    "&shkr1=03&shkr2=03&shkr3=03&shkr4=03"
    "&fw2=&srch_navi=1"
)

OUTPUT_DIR = Path("suumo_output")
AREA_DIR = OUTPUT_DIR / "areas"
MERGED_DIR = OUTPUT_DIR / "merged"

AREA_DIR.mkdir(parents=True, exist_ok=True)
MERGED_DIR.mkdir(parents=True, exist_ok=True)

MAX_ROWS_PER_AREA = 500
MAX_ROWS_PER_BUILDING = 2
MAX_PAGES_PER_AREA = 80

# 连续多少页没有新增数据就停止，防止空转
MAX_NO_NEW_PAGES = 3

ALLOWED_LAYOUTS = {
    "ワンルーム",
    "1R",
    "1K",
    "1DK",
    "1LDK",
    "2K",
    "2DK",
    "2LDK",
}




AREAS = [
    {"name": "千代田区", "sc": "13101"},
    {"name": "中央区", "sc": "13102"},
    {"name": "港区", "sc": "13103"},
    {"name": "新宿区", "sc": "13104"},
    {"name": "文京区", "sc": "13105"},
    {"name": "台東区", "sc": "13106"},
    {"name": "墨田区", "sc": "13107"},
    {"name": "江東区", "sc": "13108"},
    {"name": "品川区", "sc": "13109"},
    {"name": "目黒区", "sc": "13110"},
    {"name": "大田区", "sc": "13111"},
    {"name": "世田谷区", "sc": "13112"},
    {"name": "渋谷区", "sc": "13113"},
    {"name": "中野区", "sc": "13114"},
    {"name": "杉並区", "sc": "13115"},
    {"name": "豊島区", "sc": "13116"},
    {"name": "北区", "sc": "13117"},
    {"name": "荒川区", "sc": "13118"},
    {"name": "板橋区", "sc": "13119"},
    {"name": "練馬区", "sc": "13120"},
    {"name": "足立区", "sc": "13121"},
    {"name": "葛飾区", "sc": "13122"},
    {"name": "江戸川区", "sc": "13123"},
    {"name": "八王子市", "sc": "13201"},
    {"name": "立川市", "sc": "13202"},
    {"name": "武蔵野市", "sc": "13203"},
    {"name": "三鷹市", "sc": "13204"},
    {"name": "青梅市", "sc": "13205"},
    {"name": "府中市", "sc": "13206"},
    {"name": "昭島市", "sc": "13207"},
    {"name": "調布市", "sc": "13208"},
    {"name": "町田市", "sc": "13209"},
    {"name": "小金井市", "sc": "13210"},
    {"name": "小平市", "sc": "13211"},
    {"name": "日野市", "sc": "13212"},
    {"name": "東村山市", "sc": "13213"},
    {"name": "国分寺市", "sc": "13214"},
    {"name": "国立市", "sc": "13215"},
    {"name": "多摩市", "sc": "13224"},
    {"name": "稲城市", "sc": "13225"},
    {"name": "西東京市", "sc": "13229"},
]


# =========================
# 浏览器
# =========================

def create_driver() -> webdriver.Chrome:
    options = webdriver.ChromeOptions()

    # 想看浏览器运行过程就保持注释
    # options.add_argument("--headless=new")

    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    driver.execute_script("""
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        })
    """)
    return driver


# =========================
# 工具函数
# =========================

def safe_text(parent, by, selector) -> str:
    try:
        return parent.find_element(by, selector).text.strip()
    except Exception:
        return ""


def extract_number(text: str):
    if not text:
        return None
    m = re.search(r"(\d+(?:\.\d+)?)", text.replace(",", ""))
    return float(m.group(1)) if m else None


def normalize_building_type(text: str) -> str:
    if not text:
        return ""
    if "マンション" in text:
        return "mansion"
    if "アパート" in text:
        return "apartment"
    return text


def normalize_layout(layout: str) -> str:
    if not layout:
        return ""
    layout = layout.strip().upper()
    if layout == "1ワンルーム":
        return "ワンルーム"
    return layout


def parse_station_lines(station_block_text: str):
    if not station_block_text:
        return []
    return [x.strip() for x in station_block_text.split("\n") if x.strip()]


def parse_walk(line: str):
    if not line:
        return None
    m = re.search(r"歩(\d+)分", line)
    return int(m.group(1)) if m else None


def parse_age_and_total_floors(text: str):
    age = None
    total_floors = None

    if not text:
        return age, total_floors

    lines = [x.strip() for x in text.split("\n") if x.strip()]

    for line in lines:
        if "新築" in line:
            age = 0.0
        elif "築" in line and "年" in line:
            n = extract_number(line)
            if n is not None:
                age = n

        if "階建" in line:
            n = extract_number(line)
            if n is not None:
                total_floors = n

    return age, total_floors


def parse_layout_area(layout_area_text: str):
    if not layout_area_text:
        return "", None

    lines = [x.strip() for x in layout_area_text.split("\n") if x.strip()]
    layout_type = ""
    area = None

    if len(lines) >= 1:
        layout_type = normalize_layout(lines[0])

    if len(lines) >= 2:
        area = extract_number(lines[1])

    return layout_type, area


def parse_price_block(price_text: str):
    if not price_text:
        return None, None

    lines = [x.strip() for x in price_text.split("\n") if x.strip()]
    rent = None
    management_fee = None

    if len(lines) >= 1:
        rent = extract_number(lines[0])

    if len(lines) >= 2:
        management_fee = extract_number(lines[1])

    return rent, management_fee


def safe_filename(text: str) -> str:
    return re.sub(r'[\\/:*?"<>| ]+', "_", text)


def wait_for_listings(driver, timeout=15):
    WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div.cassetteitem"))
    )


def get_current_page_from_url(url: str):
    m = re.search(r"[?&]page=(\d+)", url)
    if m:
        return int(m.group(1))
    return 1


def goto_next_page(driver: webdriver.Chrome) -> bool:
    old_url = driver.current_url
    old_page = get_current_page_from_url(old_url)

    # 先找所有分页链接
    all_links = driver.find_elements(By.CSS_SELECTOR, "a")

    best_link = None
    best_target_page = old_page

    for link in all_links:
        try:
            if not link.is_displayed():
                continue

            text = (link.text or "").strip()
            href = (link.get_attribute("href") or "").strip()

            if not href:
                continue

            # 优先：文字里明确写“次へ”
            if "次へ" in text or "次のページ" in text:
                best_link = link
                break

            # 备用：href 里有 page=，而且目标页比当前页大
            if "page=" in href:
                target_page = get_current_page_from_url(href)
                if target_page > best_target_page:
                    best_target_page = target_page
                    best_link = link

        except Exception:
            continue

    if best_link is None:
        return False

    try:
        click_text = (best_link.text or "").strip()
        click_href = (best_link.get_attribute("href") or "").strip()

        print(f"  [翻页] old_url = {old_url}")
        print(f"  [翻页] click  = text='{click_text}', href='{click_href}'")

        driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});", best_link
        )
        time.sleep(random.uniform(1.0, 2.0))
        driver.execute_script("arguments[0].click();", best_link)

        WebDriverWait(driver, 10).until(
            lambda d: d.current_url != old_url
        )

        wait_for_listings(driver, timeout=15)

        new_url = driver.current_url
        new_page = get_current_page_from_url(new_url)

        print(f"  [翻页] new_url = {new_url}")

        if new_url == old_url:
            return False

        # 如果 URL 有 page 参数，就要求页码必须前进
        if "page=" in new_url and new_page <= old_page:
            print("  [翻页] 页码没有前进，判定失败。")
            return False

        return True

    except Exception as e:
        print(f"  [翻页] 失败: {e}")
        return False
    """
    只点真正的“下一页”，并且确认 URL 发生变化。
    避免 2 <-> 3 来回循环。
    """
    old_url = driver.current_url
    old_page = get_current_page_from_url(old_url)

    candidate_selectors = [
        "a[rel='next']",
        "a[title='次へ']",
        "a[aria-label='次へ']",
    ]

    for selector in candidate_selectors:
        try:
            links = driver.find_elements(By.CSS_SELECTOR, selector)

            for link in links:
                if not link.is_displayed():
                    continue

                text = (link.text or "").strip()
                href = link.get_attribute("href") or ""

                # 只接受明确的下一页按钮
                is_next = (
                    selector == "a[rel='next']"
                    or "次へ" in text
                    or "次のページ" in text
                )

                if not is_next:
                    continue

                if not href:
                    continue

                target_page = get_current_page_from_url(href)
                if target_page <= old_page and "page=" in href:
                    continue

                print(f"  [翻页] old_url = {old_url}")
                print(f"  [翻页] click  = text='{text}', href='{href}'")

                driver.execute_script(
                    "arguments[0].scrollIntoView({block: 'center'});", link
                )
                time.sleep(random.uniform(1.0, 2.0))
                driver.execute_script("arguments[0].click();", link)

                WebDriverWait(driver, 10).until(
                    lambda d: d.current_url != old_url
                )

                # 等待新页房源出现
                wait_for_listings(driver, timeout=15)

                new_url = driver.current_url
                new_page = get_current_page_from_url(new_url)

                print(f"  [翻页] new_url = {new_url}")

                # 防止没前进或乱跳
                if new_url == old_url:
                    return False

                if new_page <= old_page and "page=" in new_url:
                    print("  [翻页] 页码没有前进，判定失败。")
                    return False

                return True

        except TimeoutException:
            print("  [翻页] 点击后页面未正常变化。")
            return False
        except Exception as e:
            print(f"  [翻页] selector={selector} 失败: {e}")
            continue

    return False


# =========================
# 抓一页
# =========================

def extract_listing_data(driver: webdriver.Chrome, area_name: str, scraped_at: str, scraped_date: str):
    rows = []

    wait_for_listings(driver, timeout=15)
    items = driver.find_elements(By.CSS_SELECTOR, "div.cassetteitem")

    for item in items:
        try:
            building_type_raw = safe_text(
                item, By.CSS_SELECTOR, "div.cassetteitem_content-label"
            )
            building_type = normalize_building_type(building_type_raw)

            # 只抓 mansion
            if building_type != "mansion":
                continue

            title = safe_text(item, By.CSS_SELECTOR, "div.cassetteitem_content-title")
            address = safe_text(item, By.CSS_SELECTOR, "li.cassetteitem_detail-col1")

            station_block_text = safe_text(
                item, By.CSS_SELECTOR, "li.cassetteitem_detail-col2"
            )
            station_lines = parse_station_lines(station_block_text)

            walk_list = []
            for line in station_lines:
                w = parse_walk(line)
                if w is not None:
                    walk_list.append(w)
            min_walk = min(walk_list) if walk_list else None

            age_floor_text = safe_text(
                item, By.CSS_SELECTOR, "li.cassetteitem_detail-col3"
            )
            age, total_floors = parse_age_and_total_floors(age_floor_text)

            room_rows = item.find_elements(By.CSS_SELECTOR, "tbody tr.js-cassette_link")

            for row in room_rows:
                floor_text = safe_text(row, By.CSS_SELECTOR, "td:nth-child(3)")
                price_text = safe_text(row, By.CSS_SELECTOR, "td:nth-child(4)")
                layout_area_text = safe_text(row, By.CSS_SELECTOR, "td:nth-child(6)")

                floor = extract_number(floor_text)
                rent, management_fee = parse_price_block(price_text)
                layout_type, area = parse_layout_area(layout_area_text)

                if layout_type not in ALLOWED_LAYOUTS:
                    continue

                building_key = f"{area_name}__{title}__{address}"

                rows.append({
                    "scraped_at": scraped_at,
                    "scraped_date": scraped_date,
                    "area_name": area_name,
                    "building_type": building_type,
                    "title": title,
                    "address": address,
                    "walk": min_walk,
                    "age": age,
                    "total_floors": total_floors,
                    "floor": floor,
                    "layout_type": layout_type,
                    "area": area,
                    "rent_man_yen": rent,
                    "management_fee_yen": management_fee,
                    "building_key": building_key,
                    "source_url": driver.current_url,
                })

        except Exception as e:
            print(f"[WARN] 解析一个楼盘失败: {e}")

    return rows


# =========================
# 保存单个区/市
# =========================

def save_area_csv(area_name: str, rows: list[dict], scraped_date: str):
    if not rows:
        print(f"[{area_name}] 没有数据，不保存。")
        return None

    df = pd.DataFrame(rows)

    if "building_key" in df.columns:
        df = df.drop(columns=["building_key"])

    filename = f"{scraped_date}_{safe_filename(area_name)}.csv"
    output_path = AREA_DIR / filename
    df.to_csv(output_path, index=False, encoding="utf-8-sig")

    print(f"[{area_name}] 已保存: {output_path}")
    return output_path


# =========================
# merge 全部
# =========================

def merge_all_area_csv(scraped_date: str):
    csv_files = sorted(AREA_DIR.glob(f"{scraped_date}_*.csv"))

    if not csv_files:
        print("没有找到可合并的分区 CSV。")
        return None

    df_list = []
    for file in csv_files:
        try:
            df = pd.read_csv(file)
            df_list.append(df)
        except Exception as e:
            print(f"[WARN] 读取 {file} 失败: {e}")

    if not df_list:
        print("分区 CSV 读取失败，无法合并。")
        return None

    merged_df = pd.concat(df_list, ignore_index=True)

    merged_path = MERGED_DIR / f"{scraped_date}_merged_all_areas.csv"
    merged_df.to_csv(merged_path, index=False, encoding="utf-8-sig")

    print(f"\n合并完成: {merged_path}")
    print(f"总行数: {len(merged_df)}")
    return merged_path


# =========================
# 主流程
# =========================

def main():
    driver = create_driver()

    scraped_now = datetime.now()
    scraped_at = scraped_now.strftime("%Y-%m-%d %H:%M:%S")
    scraped_date = scraped_now.strftime("%Y-%m-%d")

    global_seen = set()

    try:
        for area_cfg in AREAS:
            area_name = area_cfg["name"]
            sc = area_cfg["sc"]
            start_url = BASE_URL.format(sc=sc)

            print(f"\n========== 开始抓取 {area_name} ({sc}) ==========")
            driver.get(start_url)
            time.sleep(random.uniform(3, 5))

            try:
                wait_for_listings(driver, timeout=15)
            except TimeoutException:
                print(f"[{area_name}] 页面加载失败或没有房源，跳过。")
                continue

            area_rows = []
            building_counter = defaultdict(int)
            visited_urls = set()
            page_num = 1
            no_new_pages = 0

            while page_num <= MAX_PAGES_PER_AREA and len(area_rows) < MAX_ROWS_PER_AREA:
                current_url = driver.current_url

                if current_url in visited_urls:
                    print(f"[{area_name}] 检测到重复页面，停止: {current_url}")
                    break
                visited_urls.add(current_url)

                print(f"[{area_name}] 第 {page_num} 页: {current_url}")

                try:
                    page_rows = extract_listing_data(
                        driver=driver,
                        area_name=area_name,
                        scraped_at=scraped_at,
                        scraped_date=scraped_date,
                    )
                except TimeoutException:
                    print(f"[{area_name}] 当前页房源加载失败，停止。")
                    break

                new_count = 0
                for row in page_rows:
                    unique_key = (
                        row["area_name"],
                        row["title"],
                        row["address"],
                        row["floor"],
                        row["rent_man_yen"],
                        row["area"],
                        row["layout_type"],
                    )

                    if unique_key in global_seen:
                        continue

                    bk = row["building_key"]
                    if building_counter[bk] >= MAX_ROWS_PER_BUILDING:
                        continue

                    global_seen.add(unique_key)
                    building_counter[bk] += 1
                    area_rows.append(row)
                    new_count += 1

                    if len(area_rows) >= MAX_ROWS_PER_AREA:
                        break

                print(
                    f"[{area_name}] 本页新增 {new_count} 条，"
                    f"当前累计 {len(area_rows)} 条"
                )

                if new_count == 0:
                    no_new_pages += 1
                else:
                    no_new_pages = 0

                if no_new_pages >= MAX_NO_NEW_PAGES:
                    print(f"[{area_name}] 连续 {MAX_NO_NEW_PAGES} 页无新增数据，停止。")
                    break

                if len(area_rows) >= MAX_ROWS_PER_AREA:
                    print(f"[{area_name}] 已达到 {MAX_ROWS_PER_AREA} 条，停止。")
                    break

                moved = goto_next_page(driver)
                if not moved:
                    print(f"[{area_name}] 没有下一页了，停止。")
                    break

                page_num += 1
                time.sleep(random.uniform(4, 7))

            save_area_csv(area_name, area_rows, scraped_date)

        merge_all_area_csv(scraped_date)

    finally:
        driver.quit()


if __name__ == "__main__":
    main()