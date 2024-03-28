import time
from bs4 import BeautifulSoup
import re
import json
import csv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urlparse
from decouple import config

path = config("path")

class SixshopScraper:
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
        brand_name = self.get_brand_name(driver)
        product_name = self.get_product_name(web)
        image_url = self.get_image_url(driver)
        original_price = self.get_original_price(driver)
        discount_price = self.get_discount_price(driver)
        options = self.get_size_options(driver)
        product_description = self.get_introduce(driver)
        delivery = self.get_delivery(driver)
        crawl = "sixshop"

        if discount_price == None or discount_price == 0:
            return json.dumps(
                {
                    "brand_name": brand_name,
                    "product_name": product_name,
                    "image_url": image_url,
                    "original_price": original_price,
                    "options1": options,
                    "introduce": product_description,
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
                    "original_price": original_price,
                    "discount_price": discount_price,
                    "options1": options,
                    "introduce": product_description,
                    "delivery": delivery,
                    "crawl": crawl,
                },
                ensure_ascii=False,
                indent=4,
            )

    def get_product_name(self, web):
        try:
            # 대상 meta 태그 찾기
            time.sleep(1)
            meta_tag = web.find("meta", {"property": "og:title"})

            # meta 태그가 있는 경우 content 속성 값을 가져오기
            if meta_tag:
                return meta_tag.get("content")

            return None

        except Exception as e:
            # 예외 메시지 출력
            print(f"get_product_name 함수에서 오류 발생: {e}")
            return None

    def get_brand_name(self, driver):
        try:
            # JavaScript를 사용하여 숨겨진 요소의 텍스트를 가져옵니다.
            brand_text = driver.execute_script(
                'return document.querySelector(".site-name").textContent;'
            )
            return brand_text.strip() if brand_text else None
        except Exception as e:
            print(f"Error in get_brand_name: {e}")
            return None

    def get_image_url(self, driver):
        try:
            # WebDriverWait를 사용하여 이미지가 로드될 때까지 기다립니다.
            image_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'meta[property="og:image"]')
                )
            )

            # 이미지 URL을 가져옵니다.
            image_url = image_element.get_attribute("content")
            return image_url
        except Exception as e:
            print(f"Error in get_image_url: {e}")
            return None

    def get_original_price(self, driver):
        try:
            try:
                price_tag = driver.find_element(
                    By.CSS_SELECTOR, "span.productPriceSpan"
                )
                price_text = price_tag.text.strip() if price_tag else None

                if price_text:
                    # 가격 정보에서 숫자만 추출하여 정수로 변환
                    price_text = int(re.sub(r"\D", "", price_text))
                    print(price_text)
                    return price_text
            except:
                pass
            try:
                # 'productPriceSpan' 클래스로 가격 정보를 찾지 못한 경우, 'productPriceWithDiscountSpan' 클래스를 가진 요소에서 찾기
                price_tag = driver.find_element(
                    By.CSS_SELECTOR, "span.productPriceWithDiscountSpan"
                )
                price_text = price_tag.text.strip() if price_tag else None

                if price_text:
                    # 할인된 가격 정보에서 숫자만 추출하여 정수로 변환
                    price_text = int(re.sub(r"\D", "", price_text))
                    print(price_text)
                    return price_text
            except:
                pass

        except Exception as e:
            # 예외 발생 시 예외 메시지 출력
            print(f"Error retrieving price: {e}")
            return None

    def get_discount_price(self, driver):
        try:
            discount_price_tag = driver.find_element(
                By.CLASS_NAME, "productDiscountPriceSpan"
            )
            discount_price_text = (
                discount_price_tag.text.strip() if discount_price_tag else None
            )
            if discount_price_text:
                return int(re.sub(r"\D", "", discount_price_text))
        except Exception as e:
            print(f"할인X or Error in get_discount_price: {e}")
            return None

    def get_size_options(self, driver):
        try:
            # '사이즈 선택' 드롭다운 클릭
            size_dropdown = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (
                        By.CSS_SELECTOR,
                        "div.custom-select-box",
                    )
                )
            )
            size_dropdown.click()

            # 사이즈 옵션들이 포함된 드롭다운 메뉴가 나타나는 것을 기다림
            WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located(
                    (By.CSS_SELECTOR, "div.custom-select-box-list")
                )
            )

            # 사용 가능한 사이즈 옵션 출력
            sizes = driver.find_elements(
                By.CSS_SELECTOR,
                "div.custom-select-box-list > div.custom-select-box-list-inner > div.custom-select-option[data-soldout] > div.custom-select-option-info",
            )

            # 각 사이즈를 리스트로 추출하되 빈 값을 제외함
            size_options = [size.text.strip() for size in sizes if size.text.strip()]
            return size_options

        except Exception as e:
            # 예외 메시지 출력
            print(f"수량 옵션 OR Error in get_size_options: {e}")
            return "수량"

    def get_introduce(self, driver):
        try:
            if driver:
                # ID가 'INTRODUCE'인 div 태그를 찾기
                introduce_div = driver.find_element(By.ID, "productCommonHeader")

                if introduce_div:
                    # introduce_div 하위에 있는 모든 하위 태그의 HTML 코드 추출
                    introduce_details_html = introduce_div.get_attribute("innerHTML")

                # 결과 반환
                return introduce_details_html
            else:
                print("웹 객체가 유효하지 않습니다.")
                return None
        except Exception as e:
            # print(f"Error in get_introduce_details: {e}")
            introduce_div = driver.find_element(By.ID, "productDescriptionDetailPage")
            introduce_details = introduce_div.get_attribute("innerHTML")
            if introduce_div:
                return introduce_details
            return None

    def get_delivery(self, driver):
        try:
            if driver:
                delivery_info = ""

                # 첫 번째 정보를 추출합니다.
                try:
                    product_info_element = driver.find_element(
                        By.ID, "productAdditionalInfo"
                    )
                    shopsetting_element = product_info_element.find_element(
                        By.ID, "shopSettingShipmentDiv"
                    )
                    delivery_elements = shopsetting_element.find_elements(
                        By.TAG_NAME, "span"
                    )
                    for element in delivery_elements:
                        delivery_info += element.text.strip() + " "

                except Exception as e:
                    pass  # 첫 번째 정보가 없는 경우 넘어갑니다.

                # 두 번째 정보를 추출합니다.
                try:
                    extra_fee_element = driver.find_element(
                        By.CLASS_NAME, "js-extraFeeDescription"
                    )
                    extra_fee_text_element = extra_fee_element.find_element(
                        By.CLASS_NAME, "shopSettingShipmentInfo"
                    )
                    delivery_info += extra_fee_text_element.text.strip()
                except Exception as e:
                    pass  # 두 번째 정보가 없는 경우 넘어갑니다.

                return delivery_info.strip()  # 텍스트 값을 반환합니다.
            else:
                print("웹 객체가 유효하지 않습니다.")
        except Exception as e:
            print(f"Error in get_delivery: {e}")
            return None


if __name__ == "__main__":
    product_url = input("상품 상세 URL을 입력하세요: ")
    scraper = SixshopScraper()
    result = scraper.get_product_info(product_url)
    print(result)
