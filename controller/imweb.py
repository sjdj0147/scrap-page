from bs4 import BeautifulSoup
import requests
import re
import json
import csv
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
from dotenv import load_dotenv

load_dotenv()

path = os.environ.get("path")


class ImwebScraper:
    def __init__(self):
        self.options = webdriver.ChromeOptions()
        self.options.add_argument("--headless")  # 헤드리스 모드 사용하지 않음
        self.options.add_argument(
            "--window-size=1920,1080"
        )  # 윈도우크기 설정 (헤드리스 모드 클릭 옵션)
        self.options.add_argument("disable-gpu")  # 가속 사용 x
        self.options.add_argument("lang=ko_KR")  # 가짜 플러그인 탑재

    def get_product_info(self, product_url):
        header = {
            "User-Agent": "Mozilla/5.0(Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        }
        driver = webdriver.Chrome(path, options=self.options)
        driver.get(product_url)
        time.sleep(1)

        page_source = driver.page_source
        web = BeautifulSoup(page_source, "html.parser")

        # 조건문 기본은 0
        if 0:
            brand_name = self.get_brand_name(web)
            product_name = self.get_product_name(web)
        else:
            brand_and_product = self.get_brand_and_product_name(web)
            if brand_and_product:
                product_name, brand_name = brand_and_product
            else:
                print("Failed to get brand and product name.")

        image_url = self.get_image_url(web)
        original_price = self.get_real_price(web)
        discount_price = self.get_sale_price(web)
        options = self.get_options(driver)
        time.sleep(0.1)
        introduce = self.get_introduce(driver)
        delivery = self.get_delivery(driver)
        crawl = "imweb"

        driver.quit()

        if discount_price == None or discount_price == 0:
            return json.dumps(
                {
                    "brand_name": brand_name,
                    "product_name": product_name,
                    "image_url": image_url,
                    "original_price": original_price,
                    "options1": options,
                    "introduce": introduce,
                    "delivery": delivery,
                    "crawl": crawl,
                },
                ensure_ascii=False,
                indent=4,
            )
        else:
            return json.dumps(
                {
                    "brand_name": brand_name,
                    "product_name": product_name,
                    "image_url": image_url,
                    "original_price": discount_price,
                    "discount_price": original_price,
                    "options1": options,
                    "introduce": introduce,
                    "delivery": delivery,
                    "crawl": crawl,
                },
                ensure_ascii=False,
                indent=4,
            )

    def get_brand_and_product_name(self, web):
        try:
            meta_tag = web.find("meta", {"property": "og:title"})
            if meta_tag is None:
                print("meta_tag is None")

            brand_product = meta_tag.get("content") if meta_tag is not None else None
            colon_count = brand_product.count(":")

            if brand_product and ":" in brand_product and colon_count == 2:
                product_name, brand_name = map(str.strip, brand_product.rsplit(":", 1))
                return [product_name, brand_name]
            elif brand_product and ":" in brand_product and colon_count == 1:
                product_name, brand_name = map(str.strip, brand_product.split(":", 1))
                return [product_name, brand_name]
            elif brand_product:
                title_tag = web.find("title")
                if title_tag:
                    title_text = title_tag.text.strip()
                    title_parts = title_text.split()
                    if len(title_parts) >= 2:
                        brand_name = title_parts[0]
                        product_name = " ".join(title_parts[1:])
                        return [product_name, brand_name]
                else:
                    return None
            else:
                return None
        except Exception as e:
            print(f"Error in get_brand_and_product_name: {e}")
            return None

    def get_brand_name(self, web):
        try:
            title_tag = web.find("title")
            if title_tag:
                # title 태그의 텍스트 반환
                return title_tag.text.strip()
        except Exception as e:
            print(f"Error in get_brand_name: {e}")
            return None

    def get_product_name(self, web):
        try:
            meta_tag = web.find("meta", {"name": "keywords"})
            if meta_tag:
                # content 속성에서 키워드 문자열 추출
                keywords = meta_tag.get("content")
                # 쉼표로 분리하여 리스트로 만든 후 첫 번째 요소 반환
                product_name = keywords.split(",")[0].strip()
                return product_name
        except Exception as e:
            print(f"Error in get_product_name: {e}")
            return None

    def get_image_url(self, web):
        try:
            meta_tag = web.find("meta", {"property": "og:image"})
            image_url = meta_tag.get("content") if meta_tag is not None else None
            return image_url
        except Exception as e:
            print(f"Error in get_brand_name: {e}")
            return None

    def get_real_price(self, web):
        try:
            price_tag = web.find("span", {"class": "real_price"})
            original_price_text = price_tag.text if price_tag is not None else None

            if original_price_text:
                original_price = int("".join(filter(str.isdigit, original_price_text)))
                return original_price

            return 0
        except Exception as e:
            print(f"Error in get_original_price_meta: {e}")
            return None

    def get_sale_price(self, web):
        try:
            span_tag = web.find("span", {"class": "sale_price"})
            price_text = span_tag.text if span_tag is not None else None

            if price_text:
                return int("".join(filter(str.isdigit, price_text)))

            return 0
        except Exception as e:
            print(f"Error in get_discount_price: {e}")
            return None

    # prod_options > div > div:nth-child(1) > div.txt_l > label:nth-child(1)
    def get_options(self, driver):
        options = []
        try:
            if driver:

                try:
                    try:
                        buy_button_class = ".btn.defualt.buy.bg-brand"
                        WebDriverWait(driver, 3).until(
                            EC.element_to_be_clickable(
                                (By.CSS_SELECTOR, buy_button_class)
                            )
                        ).click()
                    except:
                        pass
                    try:
                        buy_button_class = "a._btn_buy.button.bg-brand "
                        WebDriverWait(driver, 3).until(
                            EC.element_to_be_clickable(
                                (By.CSS_SELECTOR, buy_button_class)
                            )
                        ).click()
                    except:
                        pass
                    radio_btn = WebDriverWait(driver, 3).until(
                        EC.element_to_be_clickable(
                            (
                                By.CSS_SELECTOR,
                                "div:nth-child(1) div.txt_l label:nth-child(1)",
                            )
                        )
                    )
                    radio_btn.click()
                    time.sleep(0.3)
                    # 모든 라벨 태그 찾기
                    label_elements = driver.find_elements(
                        By.CSS_SELECTOR,
                        "div:nth-child(1) div.txt_l label[data-title]",
                    )

                    options.append(
                        [label.get_attribute("data-title") for label in label_elements]
                    )

                    # 라벨 태그들의 data-title 속성 추출

                    # size.
                    size_dropdown = (
                        WebDriverWait(driver, 3)
                        .until(
                            EC.element_to_be_clickable(
                                (
                                    By.CSS_SELECTOR,
                                    "div.form-select-wrap a.dropdown-toggle[aria-haspopup='true']",
                                )
                            )
                        )
                        .click()
                    )

                    WebDriverWait(driver, 3).until(
                        EC.visibility_of_element_located(
                            (By.CSS_SELECTOR, "div.dropdown-menu")
                        )
                    )

                    sizes = driver.find_elements(
                        By.CSS_SELECTOR,
                        "div.dropdown-menu div.dropdown-item a span.blocked:not(.no-margin)",
                    )

                    # options 리스트에 빈 문자열이 아닌 경우에만 추가
                    options.append([size.text for size in sizes if size.text.strip()])
                    return options

                except:
                    pass

                try:
                    # size.
                    size_dropdown = (
                        WebDriverWait(driver, 3)
                        .until(
                            EC.element_to_be_clickable(
                                (
                                    By.CSS_SELECTOR,
                                    "div.form-select-wrap a.dropdown-toggle[aria-haspopup='true']",
                                )
                            )
                        )
                        .click()
                    )

                    size_click = (
                        WebDriverWait(driver, 3).until(
                            EC.element_to_be_clickable(
                                (
                                    By.CSS_SELECTOR,
                                    "div.dropdown-item a.blocked._requireOption",
                                )
                            )
                        )
                    ).click()

                    WebDriverWait(driver, 3).until(
                        EC.visibility_of_element_located(
                            (By.CSS_SELECTOR, "div.dropdown-menu")
                        )
                    )

                    sizes = driver.find_elements(
                        By.CSS_SELECTOR,
                        "div.dropdown-menu div.dropdown-item a span.blocked:not(.no-margin)",
                    )

                    # options 리스트에 빈 문자열이 아닌 경우에만 추가
                    options.append([size.text for size in sizes if size.text.strip()])

                    radio_btn = WebDriverWait(driver, 3).until(
                        EC.element_to_be_clickable(
                            (
                                By.CSS_SELECTOR,
                                "div:nth-child(2) div.txt_l label:nth-child(1)",
                            )
                        )
                    )
                    radio_btn.click()
                    time.sleep(0.3)
                    # 모든 라벨 태그 찾기
                    label_elements = driver.find_elements(
                        By.CSS_SELECTOR,
                        "div:nth-child(1) div.txt_l label[data-title]",
                    )

                    options.append(
                        [label.get_attribute("data-title") for label in label_elements]
                    )
                    return options

                except:
                    pass

                try:
                    size_dropdown = WebDriverWait(driver, 3).until(
                        EC.element_to_be_clickable(
                            (
                                By.CSS_SELECTOR,
                                "div.form-select-wrap a.dropdown-toggle[aria-haspopup='true']",
                            )
                        )
                    )
                    size_dropdown.click()

                    WebDriverWait(driver, 3).until(
                        EC.visibility_of_element_located(
                            (By.CSS_SELECTOR, "div.dropdown-menu")
                        )
                    )

                    sizes = driver.find_elements(
                        By.CSS_SELECTOR,
                        "div.dropdown-menu div.dropdown-item a span.blocked:not(.no-margin)",
                    )

                    # options 리스트에 빈 문자열이 아닌 경우에만 추가
                    options = [size.text for size in sizes if size.text.strip()]

                    return options

                except:
                    pass

                try:
                    size_dropdown = WebDriverWait(driver, 3).until(
                        EC.element_to_be_clickable(
                            (
                                By.CSS_SELECTOR,
                                "div.form-select-wrap a.dropdown-toggle[aria-haspopup='true']",
                            )
                        )
                    )
                    size_dropdown.click()

                    WebDriverWait(driver, 3).until(
                        EC.visibility_of_element_located(
                            (By.CSS_SELECTOR, "div.dropdown-menu")
                        )
                    )

                    sizes = driver.find_elements(
                        By.CSS_SELECTOR,
                        #  "div.dropdown-menu div.dropdown-item a span.blocked.margin-bottom-lg",
                        "div.dropdown-menu div.dropdown-item a span.blocked:not(.no-margin)",
                    )

                    # options 리스트에 빈 문자열이 아닌 경우에만 추가
                    options = [size.text for size in sizes if size.text.strip()]
                    return options

                except:
                    pass

                try:
                    size_dropdown = WebDriverWait(driver, 3).until(
                        EC.element_to_be_clickable(
                            (
                                By.CSS_SELECTOR,
                                "div.form-select-wrap a.dropdown-toggle[aria-haspopup='true']",
                            )
                        )
                    )
                    size_dropdown.click()

                    WebDriverWait(driver, 3).until(
                        EC.visibility_of_element_located(
                            (By.CSS_SELECTOR, "div.dropdown-menu")
                        )
                    )

                    sizes = driver.find_elements(
                        By.CSS_SELECTOR,
                        "div.dropdown-menu div.dropdown-item a span.blocked:not(.no-margin)",
                    )
                    options = [size.text for size in sizes if size.text.strip()]
                    return options
                except:
                    print("옵션 수량")
                    return "수량"

            else:
                print("웹 객체가 유효하지 않음")
        except:
            print("모든 방법 실패")
            return None

    def get_introduce(self, driver):
        try:
            if driver:
                try:
                    div_element = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located(
                            (
                                By.CSS_SELECTOR,
                                "div.categorize.review-box div.open.text-center.margin-top-xxl.margin-bottom-xxl",
                            )
                        )
                    )

                    # div 태그 안에 있는 a 태그를 찾습니다.
                    a_element = div_element.find_element(
                        By.CSS_SELECTOR, "a.btn[aria-controls='prod_detail_body']"
                    )

                    # a 태그를 클릭합니다.
                    a_element.click()

                    introduce_tag = driver.find_element(
                        By.CSS_SELECTOR,
                        "div._prod_detail_detail_lazy_load.clearfix.shop_view_body.fr-view.seemore_detail.active",
                    )
                    inner_html = introduce_tag.get_attribute("innerHTML")
                    if inner_html:
                        return inner_html
                    else:
                        pass
                except:
                    pass
                try:
                    div_element = driver.find_element(By.CSS_SELECTOR, "div.fr-view")
                    inner_html = div_element.get_attribute("innerHTML")
                    if inner_html and "<img" in inner_html:
                        return inner_html
                    else:
                        pass
                except:
                    print(2)
                    pass
                try:
                    div_element = driver.find_element(
                        By.CSS_SELECTOR, "div.categorize.review-box"
                    )

                    introduce_element = div_element.find_element(
                        By.CSS_SELECTOR,
                        "div#prod_detail_body",
                    )

                    inner_html = introduce_element.get_attribute("innerHTML")
                    if (
                        inner_html
                        and inner_html
                        != "<style>@keyframes lazyload {0% {opacity: 0;} 50% {opacity: 0.1;} 100% {opacity: 0;}}</style>"
                    ):
                        return inner_html
                    else:
                        pass
                except:
                    print(3)
                    pass
                try:
                    div_element = driver.find_element(
                        By.CSS_SELECTOR,
                        "#prod_goods_form div.goods_summary.body_font_color_70",
                    )

                    introduce_element = div_element.find_element(
                        By.CSS_SELECTOR, "div.fr-view"
                    )
                    inner_html = introduce_element.get_attribute("innerHTML")
                    if inner_html:
                        return inner_html
                    else:
                        pass
                except:
                    print(4)
                    pass
            else:
                print("웹 객체가 유효하지 않습니다.")
                return None
        except:
            print("모든 방법 실패")
            return None

    def get_delivery(self, driver):
        try:
            # 세 번째 시도
            block_elements = driver.find_elements(
                By.CSS_SELECTOR,
                '#prod_deliv_setting div.option_wrap[style="display: block; font-size:14px;"]',
            )
            # 결과를 저장할 리스트 초기화
            delivery_info = []
            # 각 요소에서 span 태그를 찾아 텍스트 추출
            for element in block_elements:
                print(element, block_elements)
                # 배송 방법 제목 추출
                title_element = element.find_element(
                    By.CSS_SELECTOR, "div:nth-child(1) > span.option_title"
                )
                delivery_title = title_element.text.strip()
                print(delivery_title)
                # 배송 방법 내용 추출
                data_element = element.find_element(
                    By.CSS_SELECTOR, "div:nth-child(2) > span.option_data"
                )
                delivery_data = data_element.text.strip()
                # 결과를 튜플로 저장
                delivery_info.append((delivery_title, delivery_data))

            # 결과 반환
            print(delivery_info)
            if delivery_info:
                return delivery_info
            pass

        except Exception as e:
            print(f"Error in second try block: {e}")
            pass

        try:
            # 첫 번째 시도
            block_elements = driver.find_elements(
                By.CSS_SELECTOR,
                '#prod_goods_form div.item_detail div div:nth-child(1) .option_wrap[style="display: block; font-size:12px;"]',
            )

            # block_elements가 비어 있는지 확인
            if not block_elements:
                # 두 번째 시도
                block_elements = driver.find_elements(
                    By.CSS_SELECTOR,
                    '#prod_goods_form div.item_detail div div:nth-child(1) .option_wrap[style="display: block; font-size:14px;"]',
                )

            # 첫 번째 요소를 제외한 나머지 요소를 선택
            block_elements_excluding_first = block_elements[1:]
            # 결과를 저장할 리스트 초기화
            delivery_info = []
            # 각 요소에서 span 태그를 찾아 텍스트 추출
            for element in block_elements_excluding_first:
                # 배송 방법 제목 추출
                title_element = element.find_element(
                    By.CSS_SELECTOR, "div:nth-child(1) > span.option_title"
                )
                delivery_title = title_element.text.strip()
                print(delivery_title)
                # 배송 방법 내용 추출
                data_element = element.find_element(
                    By.CSS_SELECTOR, "div:nth-child(2) > span.option_data"
                )
                delivery_data = data_element.text.strip().replace("\npopover", "")
                # 결과를 튜플로 저장
                delivery_info.append((delivery_title, delivery_data))

            # 결과 반환
            print(delivery_info)
            return delivery_info

        except Exception as e:
            print(f"Error in first try block: {e}")
            return None


if __name__ == "__main__":
    product_url = input("상품 상세 URL을 입력하세요: ")
    scraper = ImwebScraper()
    result = scraper.get_product_info(product_url)
    print(result)
