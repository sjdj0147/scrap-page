import time
from bs4 import BeautifulSoup
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoAlertPresentException
from urllib.parse import urlparse
from decouple import config

path = config("path")

class NaverScraper:
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

        brand_and_product = self.get_brand_and_product_name(web)
        if brand_and_product:
            product_name, brand_name = brand_and_product
        else:
            print("Failed to get brand and product name.")
        product_name = self.get_product_name(driver)

        image_url = self.get_image_url(web)
        original_price = self.get_original_price(web)
        discount_price = self.get_discount_price(web)
        options = self.get_options(driver)
        options2 = self.get_options2(driver)
        options3 = self.get_options3(driver)
        introduce = self.get_introduce(driver)
        delivery = self.get_delivery(driver)
        crawl = "smartstore"

        if options == None or options == 0:
            options = self.get_radio_options(web)
            options2 = self.get_radio_options2(web)

        # 드라이버 종료
        driver.quit()

        if discount_price == original_price:
            if (options2 == None or options2 == 0) and (
                options3 == None or options3 == 0
            ):
                return json.dumps(
                    {
                        "brand_name": brand_name,
                        "product_name": product_name,
                        "image_url": image_url,
                        "original_price": original_price,
                        "options1": options,
                        "delivery": delivery,
                        "introduce": introduce,
                        "crawl": crawl,
                    },
                    ensure_ascii=False,
                    indent=4,
                )
            elif options3 == None or options3 == 0:
                return json.dumps(
                    {
                        "brand_name": brand_name,
                        "product_name": product_name,
                        "image_url": image_url,
                        "original_price": original_price,
                        "options1": options,
                        "options2": options2,
                        "delivery": delivery,
                        "introduce": introduce,
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
                        "options1": options,
                        "options2": options2,
                        "options3": options3,
                        "delivery": delivery,
                        "introduce": introduce,
                        "crawl": crawl,
                    },
                    ensure_ascii=False,
                    indent=4,
                )

        else:
            if (options2 == None or options2 == 0) and (
                options3 == None or options3 == 0
            ):
                return json.dumps(
                    {
                        "brand_name": brand_name,
                        "product_name": product_name,
                        "image_url": image_url,
                        "original_price": original_price,
                        "discount_price": discount_price,
                        "options1": options,
                        "introduce": introduce,
                        "delivery": delivery,
                        "crawl": crawl,
                    },
                    ensure_ascii=False,
                    indent=4,
                )
            elif options3 == None or options3 == 0:
                return json.dumps(
                    {
                        "brand_name": brand_name,
                        "product_name": product_name,
                        "image_url": image_url,
                        "original_price": original_price,
                        "discount_price": discount_price,
                        "options1": options,
                        "options2": options2,
                        "delivery": delivery,
                        "introduce": introduce,
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
                        "options2": options2,
                        "options3": options3,
                        "delivery": delivery,
                        "introduce": introduce,
                        "crawl": crawl,
                    },
                    ensure_ascii=False,
                    indent=4,
                )

    def get_brand_and_product_name(self, web):
        try:
            # og:title 메타 태그 찾기
            meta_tag = web.find("meta", {"property": "og:title"})
            if meta_tag is None:
                print("meta_tag is None")

            # 추가된 부분: meta_tag이 None이 아닌 경우에만 .get() 메소드 호출
            brand_product = meta_tag.get("content") if meta_tag is not None else None

            if brand_product and ":" in brand_product:
                # ":"을 기준으로 분리하여 앞부분은 제품명, 뒷부분은 브랜드명으로 추출
                product_name, brand_name = map(str.strip, brand_product.split(":", 1))
                return [product_name, brand_name]

            return None
        except Exception as e:
            # 추가된 부분: 예외 메시지 출력
            print(f"Error in get_brand_and_product_name: {e}")
            return None

    def get_product_name(self, driver):
        try:
            h3_tag = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "div._1eddO7u4UC > h3")
                )
            )
            product_name = h3_tag.text
            if product_name:
                return product_name
            else:
                pass
        except Exception as e:
            print(f"Error in get_product_name: {e}")

    def get_image_url(self, web):
        try:
            # og:site_name 메타 태그 찾기
            meta_tag = web.find("meta", {"property": "og:image"})

            # 추가된 부분: meta_tag이 None이 아닌 경우에만 .get() 메소드 호출
            image_url = meta_tag.get("content") if meta_tag is not None else None

            return image_url
        except Exception as e:
            # 추가된 부분: 예외 메시지 출력
            print(f"Error in get_brand_name: {e}")
            return None

    def get_original_price(self, web):
        try:
            # span 태그의 클래스가 "_1LY7DqCnwR"인 요소 찾기
            span_tag = web.find("span", class_="_1LY7DqCnwR")

            # 추가된 부분: span_tag이 None이 아닌 경우에만 .text 속성을 가져옴
            original_price_content = span_tag.text if span_tag is not None else None

            if original_price_content:
                # 숫자만 추출하여 반환
                return int("".join(filter(str.isdigit, original_price_content)))

            return 0
        except Exception as e:
            # 추가된 부분: 예외 메시지 출력
            print(f"Error in get_original_price: {e}")
            return None

    def get_discount_price(self, web):
        try:
            # strong 태그의 클래스가 "aICRqgP9zw"인 요소 찾기
            strong_tag = web.find("strong", class_="aICRqgP9zw")

            # 추가된 부분: strong_tag이 None이 아닌 경우에만 .text 속성을 가져옴
            price_content = strong_tag.text if strong_tag is not None else None

            if price_content:
                # 숫자만 추출하여 반환
                return int("".join(filter(str.isdigit, price_content)))

            return 0
        except Exception as e:
            # 추가된 부분: 예외 메시지 출력
            print(f"Error in get_price_in_strong_tag: {e}")
            return None

    def get_options(self, driver):
        try:
            # 대상 a 태그를 JavaScript로 클릭
            a_tag = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (
                        By.CSS_SELECTOR,
                        "#content > div > div._2-I30XS1lA > div._2QCa6wHHPy > fieldset > div.bd_2dy3Y > div:nth-child(1) > a",
                    )
                )
            )

            # a 태그 클릭
            time.sleep(0.3)
            driver.execute_script("arguments[0].click();", a_tag)

            # 대기 시간을 설정하여 a 태그의 부모 ul 태그를 기다림
            ul_tag = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (
                        By.CSS_SELECTOR,
                        "#content > div > div._2-I30XS1lA > div._2QCa6wHHPy > fieldset > div.bd_2dy3Y > div:nth-child(1) > ul",
                    )
                )
            )

            # ul 태그 아래에 있는 모든 li 태그를 찾음
            li_tags = ul_tag.find_elements(By.TAG_NAME, "li")

            # li 태그 내의 a 태그의 텍스트 값을 추출하여 리스트로 반환
            option_texts = [
                li.find_element(By.CSS_SELECTOR, "a").text.strip() for li in li_tags
            ]

            li_tag = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (
                        By.CSS_SELECTOR,
                        "#content > div > div._2-I30XS1lA > div._2QCa6wHHPy > fieldset > div.bd_2dy3Y > div:nth-child(1) > ul > li:nth-child(1) > a",
                    )
                )
            )
            # a 태그 클릭
            time.sleep(0.3)
            driver.execute_script("arguments[0].click();", li_tag)

            return option_texts
        except Exception as e:
            # 예외 메시지 출력
            print(f"Error in get_options: {e}")
            return None

    def get_options2(self, driver):
        try:
            # 대상 a 태그를 JavaScript로 클릭
            a_tag = driver.find_element(
                By.CSS_SELECTOR,
                "#content > div > div._2-I30XS1lA > div._2QCa6wHHPy > fieldset > div.bd_2dy3Y > div:nth-child(2) > a",
            )

            # a 태그 클릭
            time.sleep(0.3)
            driver.execute_script("arguments[0].click();", a_tag)

            # 대기 시간을 설정하여 a 태그의 부모 ul 태그를 기다림
            ul_tag = driver.find_element(
                By.CSS_SELECTOR,
                "#content > div > div._2-I30XS1lA > div._2QCa6wHHPy > fieldset > div.bd_2dy3Y > div:nth-child(2) > ul",
            )

            # ul 태그 아래에 있는 모든 li 태그를 찾음
            li_tags = ul_tag.find_elements(By.TAG_NAME, "li")

            # li 태그 내의 a 태그의 텍스트 값을 추출하여 리스트로 반환
            option_texts = [
                li.find_element(By.CSS_SELECTOR, "a").text.strip() for li in li_tags
            ]

            li_tag = driver.find_element(
                By.CSS_SELECTOR,
                "#content > div > div._2-I30XS1lA > div._2QCa6wHHPy > fieldset > div.bd_2dy3Y > div:nth-child(2) > ul > li:nth-child(1) > a",
            )
            # a 태그 클릭
            time.sleep(0.3)
            driver.execute_script("arguments[0].click();", li_tag)

            return option_texts
        except Exception as e:
            # 예외 메시지 출력
            # print(f"Error in get_options2: {e}")
            return None

    def get_options3(self, driver):
        try:
            # 대상 a 태그를 JavaScript로 클릭
            a_tag = driver.find_element(
                By.CSS_SELECTOR,
                "#content > div > div._2-I30XS1lA > div._2QCa6wHHPy > fieldset > div.bd_2dy3Y > div:nth-child(3) > a",
            )

            # a 태그 클릭
            time.sleep(0.3)
            driver.execute_script("arguments[0].click();", a_tag)

            # 대기 시간을 설정하여 a 태그의 부모 ul 태그를 기다림
            ul_tag = driver.find_element(
                By.CSS_SELECTOR,
                "#content > div > div._2-I30XS1lA > div._2QCa6wHHPy > fieldset > div.bd_2dy3Y > div:nth-child(3) > ul",
            )

            # ul 태그 아래에 있는 모든 li 태그를 찾음
            li_tags = ul_tag.find_elements(By.TAG_NAME, "li")

            # li 태그 내의 a 태그의 텍스트 값을 추출하여 리스트로 반환
            option_texts = [
                li.find_element(By.CSS_SELECTOR, "a").text.strip() for li in li_tags
            ]

            return option_texts
        except Exception as e:
            # 예외 메시지 출력
            # print(f"Error in get_options3: {e}")
            return None

    def get_radio_options(self, web):
        try:
            # 대상 div 태그를 찾기
            div_tag = web.find("div", class_="bd_3Wnjv _nlog_impression_element")

            # div 태그 내의 모든 button 태그 찾기
            button_tags = div_tag.find_all(
                "button", class_="bd_1Z-oO N=a:pcs.optcolor _nlog_click"
            )

            # 각 button 태그의 색상 이름 추출
            color_options = [
                button.get("data-shp-contents-id") for button in button_tags
            ]

            return color_options
        except Exception as e:
            # 예외 메시지 출력
            print(f"Error in get_radio_options: {e}")
            return None

    def get_radio_options2(self, web):
        try:
            # 대상 button 태그를 모두 찾기
            button_tags = web.find_all(
                "button", class_="bd_2YDJp N=a:pcs.optsize _nlog_click"
            )

            # 각 button 태그의 사이즈 추출
            size_options = [
                button.get("data-shp-contents-id") for button in button_tags
            ]

            # 중복값 제거 후 원래 순서대로 정렬
            size_options = sorted(
                list(set(size_options)), key=lambda x: size_options.index(x)
            )

            return size_options
        except Exception as e:
            # 예외 메시지 출력
            print(f"Error in get_radio_options2: {e}")
            return None

    def extract_base_url(self, url):
        # URL에서 '?' 이전의 부분을 추출
        base_url = url.split("?")[0]
        return base_url

    def get_introduce(self, driver):
        if driver:
            try:
                # introduce 버튼 클릭
                introduce_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable(
                        (
                            By.CSS_SELECTOR,
                            "#INTRODUCE > div > div._3osy73V_eD._1Hc_ju_IXp > button",
                        )
                    )
                )
                introduce_button.click()

                # introduce_div 내부의 HTML 코드 추출
                introduce_div = WebDriverWait(driver, 10).until(
                    EC.visibility_of_element_located(
                        (
                            By.CSS_SELECTOR,
                            "#INTRODUCE > div > div._3osy73V_eD._1Hc_ju_IXp._2pWm5xPRcr",
                        )
                    )
                )

                # introduce_div 내부의 HTML 코드 추출
                introduce_details_html = introduce_div.get_attribute("innerHTML")

                return introduce_details_html
            except Exception as e:
                print(f"에러 발생: {e}")
                return None
        else:
            print("웹 객체가 유효하지 않습니다.")
            return None

    def get_delivery(self, driver):
        try:
            if driver:
                today_delivery_text = None
                other_delivery_text = None

                # 첫 번째 정보를 추출합니다.
                try:
                    other_delivery = driver.find_element(By.CLASS_NAME, "_1rGSKv6aq_")
                    other_delivery_text = other_delivery.text.strip()
                except Exception as e:
                    pass  # 첫 번째 정보가 없는 경우 넘어갑니다.

                # 두 번째 정보를 추출합니다.
                try:
                    today_delivery = driver.find_element(By.CLASS_NAME, "_3GaTsu4I03")
                    today_delivery_text = today_delivery.text.strip()
                except Exception as e:
                    pass  # 두 번째 정보가 없는 경우 넘어갑니다.

                # \n을 줄바꿈으로 처리하여 반환합니다.
                today_delivery_text = (
                    today_delivery_text.replace("\n", " ")
                    if today_delivery_text
                    else None
                )
                other_delivery_text = (
                    other_delivery_text.replace("\n", " ")
                    if other_delivery_text
                    else None
                )

                if today_delivery_text == None:
                    return other_delivery_text
                elif other_delivery_text == None:
                    return today_delivery_text
                else:
                    return (
                        today_delivery_text,
                        other_delivery_text,
                    )  # 튜플로 반환합니다.
            else:
                print("웹 객체가 유효하지 않습니다.")
        except Exception as e:
            print(f"Error in get_delivery: {e}")
            return None, None


# 테스트
if __name__ == "__main__":
    product_url = input("상품 상세 URL을 입력하세요: ")
    scraper = NaverScraper()
    result = scraper.get_product_info(product_url)
    print(result)
