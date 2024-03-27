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
import os
from dotenv import load_dotenv

load_dotenv()

path = os.environ.get("path")

class Cafe24Scraper:
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

        # Cafe24 웹페이지 파싱 예시
        brand_name = self.get_brand_name_cafe24(web)

        # 일반적으로 그냥 get_product_name을 사용하지만
        product_name = self.get_product_name(web, brand_name)
        # 너무 이름이 일치하지 않는경우 버전 2사용
        if not product_name or "온라인" in product_name:
            product_name = self.get_product_name2(web, brand_name)

        domain = self.get_domain(product_url)
        image_url = self.get_image_url(driver)

        if not image_url or "배너" in image_url:
            image_url = self.get_image_url_master(web, domain, image_url)

        original_price = self.get_original_price_meta(web)
        discount_price = self.get_discount_price_meta(web)
        original_price, discount_price = self.get_discount_price_master(
            web, original_price, discount_price
        )
        options = None
        options = self.get_options_master(web, options)
        options2 = self.get_options2_ec_product_button(driver, web)
        options3 = self.get_options3_ec_product_button(web, options, options2)

        introduce = self.get_introduce(driver)
        introduce_v2 = self.get_introduce_v2(driver)
        crawl = "cafe24"

        # 드라이버 종료
        driver.quit()

        # 추출한 정보를 JSON 형태로 반환
        if discount_price == 0:
            if (
                options2 == None
                or options2 == 0
                or options2 == []
                and options3 == None
                or options3 == 0
                or options3 == []
            ):
                return json.dumps(
                    {
                        "brand_name": brand_name,
                        "product_name": product_name,
                        "image_url": image_url,
                        "original_price": original_price,
                        "options1": options,
                        "introduce": introduce,
                        "introduce_v2": introduce_v2,
                        "crawl": crawl,
                    },
                    ensure_ascii=False,
                    indent=4,
                )
            elif options3 == None or options3 == 0 or options3 == []:
                return json.dumps(
                    {
                        "brand_name": brand_name,
                        "product_name": product_name,
                        "image_url": image_url,
                        "original_price": original_price,
                        "discount_price": discount_price,
                        "options1": options,
                        "options2": options2,
                        "introduce": introduce,
                        "introduce_v2": introduce_v2,
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
                        "introduce": introduce,
                        "introduce_v2": introduce_v2,
                        "crawl": crawl,
                    },
                    ensure_ascii=False,
                    indent=4,
                )
        else:
            if (
                options2 == None
                or options2 == 0
                or options2 == []
                and options3 == None
                or options3 == 0
                or options3 == []
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
                        "introduce_v2": introduce_v2,
                        "crawl": crawl,
                    },
                    ensure_ascii=False,
                    indent=4,
                )
            elif options3 == None or options3 == 0 or options3 == []:
                return json.dumps(
                    {
                        "brand_name": brand_name,
                        "product_name": product_name,
                        "image_url": image_url,
                        "original_price": original_price,
                        "discount_price": discount_price,
                        "options1": options,
                        "options2": options2,
                        "introduce": introduce,
                        "introduce_v2": introduce_v2,
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
                        "introduce": introduce,
                        "introduce_v2": introduce_v2,
                        "crawl": crawl,
                    },
                    ensure_ascii=False,
                    indent=4,
                )

    def get_brand_name_cafe24(self, web):
        try:
            # og:site_name 메타 태그 찾기

            brand_name_cafe24 = None
            meta_tag = web.find("meta", {"property": "og:site_name"})
            # 추가된 부분: meta_tag이 None이 아닌 경우에만 .get() 메소드 호출
            brand_name_cafe24 = (
                meta_tag.get("content") if meta_tag is not None else None
            )
        except Exception as e:
            # 추가된 부분: 예외 메시지 출력
            print(f"Error in get_brand_name: {e}")
            return None
        if brand_name_cafe24:
            return brand_name_cafe24

    ## 일반적인 제풒 이름
    def get_product_name(self, web, brand_name):
        try:
            # 대상 meta 태그 찾기
            meta_tag = web.find("meta", {"property": "og:title"})

            # meta 태그가 있는 경우 content 속성 값을 가져오고, ,를 기준으로 나누기
            if meta_tag:
                content = meta_tag.get("content", "")

                # brand_name이 content에 포함되어 있다면 해당 부분을 제거
                if brand_name in content:
                    content = content.replace(brand_name, "").replace("-", "").strip()

                keywords = [keyword.strip() for keyword in content.split(",")]

                # 첫 번째 키워드 반환
                if keywords:
                    return content

            return None
        except Exception as e:
            print(f"Error in get_product_name: {e}")
            return None

    def get_product_name2(self, web, brand_name):
        try:
            # 대상 title 태그 찾기
            title_tag = web.find("title")

            # title 태그가 있는 경우 텍스트를 가져와서 처리
            if title_tag:
                title_text = title_tag.text.strip()

                # 제목에서 브랜드 이름이 포함되어 있다면 해당 부분 제거
                if brand_name in title_text:
                    title_text = title_text.replace(brand_name, "").strip()

                # 불필요한 정보를 제거하고 첫 번째 키워드 반환
                keywords = [keyword.strip() for keyword in title_text.split("-")]

                if keywords:
                    return keywords[0]

            return None

        except Exception as e:
            print(f"Error in get_product_name: {e}")
            return None

    def get_image_url(self, driver):
        try:
            # WebDriverWait를 사용하여 이미지가 로드될 때까지 기다립니다.
            meta_tags = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, 'meta[property="og:image"]')
                )
            )

            # 여러 개의 이미지 URL 중에서 조건에 맞는 이미지 URL을 찾습니다.
            for meta_tag in meta_tags:
                image_url = meta_tag.get_attribute("content")
                print(image_url)
                if "cafe24" in image_url or "big" in image_url:
                    return image_url

            # 모든 이미지 URL에 대해 조건에 맞는 이미지를 찾지 못한 경우 None을 반환합니다.
            print("No image URL containing 'big' text found.")
            return None

        except TimeoutException:
            print("Timeout occurred while waiting for og:image meta tag.")
            return None
        except Exception as e:
            # 예외 메시지 출력
            print(f"Error in get_image_url: {e}")
            return None

    def get_original_price_meta(self, web):
        try:
            # og:site_name 메타 태그 찾기
            meta_tag = web.find("meta", {"property": "product:price:amount"})

            # 추가된 부분: meta_tag이 None이 아닌 경우에만 .get() 메소드 호출
            original_price = meta_tag.get("content") if meta_tag is not None else None

            if original_price:
                return int("".join(filter(str.isdigit, original_price)))

            return 0
        except Exception as e:
            # 추가된 부분: 예외 메시지 출력
            print(f"Error in get original_price: {e}")
            return None

    def get_discount_price_meta(self, web):
        try:
            # og:site_name 메타 태그 찾기
            meta_tag = web.find("meta", {"property": "product:sale_price:amount"})

            # 추가된 부분: meta_tag이 None이 아닌 경우에만 .get() 메소드 호출
            discount_price = meta_tag.get("content") if meta_tag is not None else None

            if discount_price:
                return int("".join(filter(str.isdigit, discount_price)))

            return 0
        except Exception as e:
            # 추가된 부분: 예외 메시지 출력
            print(f"Error in get_discount_price: {e}")
            return None

    def get_discount_price_master(self, web, original_price, discount_price):
        if original_price == discount_price:
            original_price = self.get_original_price_master(web, discount_price)
        if original_price == 0 or original_price is None:
            original_price = discount_price
            discount_price = 0
        else:
            return original_price, discount_price

        # original_price와 discount_price를 함께 반환
        return original_price, discount_price

    ## 정상가 모음 함수
    def get_original_price_master(self, web, discount_price):

        master = self.get_original_price_tit(web, discount_price)
        if master == 0 or master == None or discount_price == master:
            master = self.get_original_price_span_text(web, discount_price)
        if master == 0 or master == None or discount_price == master:
            master = self.get_original_price_custom_through(web, discount_price)
        if master == 0 or master == None or discount_price == master:
            master = self.get_original_price_span_custom(web, discount_price)
        return master

    ##정상가 함수 세부 사항
    def get_original_price_span_text(self, web, discount_price):
        try:
            # strong 태그에서 id가 span_product_price_text를 찾음
            original_price_tag = web.find("strong", {"id": "span_product_price_text"})
            # strong 태그에서 text 추출
            original_price = (
                original_price_tag.text.strip() if original_price_tag else None
            )

            if original_price:
                original_price = int("".join(filter(str.isdigit, original_price)))
                if original_price == discount_price:
                    return 0
                else:
                    original_price

            return 0
        except Exception as e:
            # 예외 메시지 출력
            print(f"Error in get_original_price_span_text: {e}")
            return None

    def get_original_price_span_custom(self, web, discount_price):
        try:
            # span 태그에서 id가 span_product_price_custom을 찾음
            original_price_tag = web.find("span", {"id": "span_product_price_custom"})

            # 추가된 부분: span 태그 내의 strike 태그에서 텍스트 추출
            strike_tag = original_price_tag.find("strike")
            original_price = strike_tag.text.strip() if strike_tag else None

            if original_price:
                original_price = int("".join(filter(str.isdigit, original_price)))
                if original_price == discount_price:
                    return 0
                else:
                    return original_price  # 수정된 부분

            return 0
        except Exception as e:
            # 예외 메시지 출력
            print(f"Error in get_original_price_span_custom: {e}")
            return None

    def get_original_price_tit(self, web, discount_price):
        try:
            # 클래스명이 'info-tit-con 1'인 div 태그를 찾음
            original_price_tag = web.find("div", {"class": "info-tit-con 1"})

            # div 태그 내의 텍스트를 가져옴
            original_price_text = (
                original_price_tag.text.strip() if original_price_tag else None
            )

            if original_price_text:
                # 텍스트에서 숫자만 추출하여 정수로 변환
                original_price = int("".join(filter(str.isdigit, original_price_text)))

                # 할인 가격과 일치하는 경우 0을 반환
                if original_price == discount_price or original_price == None:
                    return 0
                else:
                    return original_price

            return 0
        except Exception as e:
            # 예외 메시지 출력
            print(f"Error in get_original_price_tit: {e}")
            return None

    def get_original_price_custom_through(self, web, discount_price):
        try:
            # 클래스명이 'custom through'인 span 태그를 찾음
            original_price_tag = web.find("span", {"class": "custom through"})

            # span 태그 내의 텍스트를 가져옴
            original_price_text = (
                original_price_tag.text.strip() if original_price_tag else None
            )

            if original_price_text:
                # 텍스트에서 숫자만 추출하여 정수로 변환
                original_price = int("".join(filter(str.isdigit, original_price_text)))

                # 할인 가격과 일치하는 경우 0을 반환
                if original_price == discount_price:
                    return 0
                else:
                    return original_price

            return 0
        except Exception as e:
            # 예외 메시지 출력
            print(f"Error in get_original_price_custom_through: {e}")
            return None

    ##요
    ##기
    ##까
    ##지
    ##정
    ##상
    ##기
    ##함
    ##수
    # 요기까지 정상가 함수

    def get_options_master(self, web, options):
        options = self.get_options_product_option_id1(web)
        if options == None or options == []:
            options = self.get_options(web)
        if options == None or options == []:
            options = self.get_options_optgroup(web)
        if options == None or options == []:
            options = self.get_options_ec_product_button(web)
        if options == None or options == []:
            options = self.get_options_Product_Option0(web)
        if not options:
            options = "수량 옵션"
        return options

    ## 옵션 추출 함수 ul안에 바로 li인 경우
    def get_options(self, web):
        try:
            # option 태그 중 link_image 속성이 포함된 모든 옵션을 찾음
            options_tags = web.find_all("option", {"link_image": True})

            # 옵션 태그 리스트에서 알파벳인 텍스트 값을 추출하여 리스트로 반환
            options_list = [
                option.text.strip()
                for option in options_tags
                if option.text.strip().isalpha()
            ]

            return options_list
        except Exception as e:
            # 예외 메시지 출력
            print(f"Error in get_options: {e}")
            return None

    ## 옵션 추출 함수 optgroup인 경우 ul안에 있는 optgroup로 묶인 경우
    def get_options_optgroup(self, web):
        try:
            # optgroup 태그 중 label 속성이 'SIZE'인 태그를 찾음
            size_optgroup = web.find("optgroup", {"label": "SIZE"})
            if size_optgroup == None:
                size_optgroup = web.find("optgroup", {"label": "색상/사이즈"})

            if size_optgroup:
                # optgroup 태그 아래에 있는 모든 option 태그를 찾음
                options_tags = size_optgroup.find_all("option")

                # 옵션 태그 리스트에서 텍스트 값을 추출하여 리스트로 반환
                options_list = [
                    option.text.strip()
                    for option in options_tags
                    if option.get("value") not in ["*", "**"]
                    and not option.get("selected")
                    and not option.get("dsiabled")
                ]

                return options_list
            else:
                print("SIZE optgroup not found.")
                return None
        except Exception as e:
            # 예외 메시지 출력
            print(f"Error in get_options: {e}")
            return None

    ## 옵션 추출 함수 ec_product_button인 경우 ul태그 없이 바로 선택인 경우
    def get_options_ec_product_button(self, web):
        try:
            # class가 'ec-product-button'인 ul 태그를 찾음
            product_button_ul = web.find("ul", {"class": "ec-product-button"})

            if product_button_ul:
                # ul 태그 아래에 있는 모든 span 태그를 찾음
                span_tags = product_button_ul.find_all("span")

                # span 태그 내의 텍스트 값을 추출하여 리스트로 반환
                span_text_list = [
                    span.text.strip()
                    for span in span_tags
                    if span.get("value") not in ["*", "**"]
                    and not span.get("selected")
                    and not span.get("dsiabled")
                ]

                return span_text_list
            else:
                print("'ec-product-button' ul not found.")
                return None
        except Exception as e:
            # 예외 메시지 출력
            print(f"Error in get_options_ec_product_button: {e}")
            return None

    def get_options_Product_Option0(self, web):
        try:
            # class가 'ProductOption0'인 select 태그를 찾음
            product_option_select = web.find("select", {"class": "ProductOption0"})

            if product_option_select:
                # select 태그 아래에 있는 모든 option 태그를 찾음
                option_tags = product_option_select.find_all("option")

                # 특정 값이나 속성을 가진 option 태그를 제외하고, 나머지 태그의 텍스트를 추출하여 리스트로 반환
                option_text_list = [
                    option.text.strip()
                    for option in option_tags
                    if option.get("value") not in ["*", "**"]
                    and not option.get("selected")
                    and not option.get("disabled")
                ]

                return option_text_list
            else:
                print("'ProductOption0' select not found.")
                return None
        except Exception as e:
            # 예외 메시지 출력
            print(f"Error in get_options_Product_Option0: {e}")
            return None

    def get_options_product_option_id1(self, web):
        try:
            # class가 'ProductOption0'인 select 태그를 찾음
            product_option_select = web.find("select", {"id": "product_option_id1"})

            if product_option_select:
                # select 태그 아래에 있는 모든 option 태그를 찾음
                option_tags = product_option_select.find_all("option")

                # 특정 값이나 속성을 가진 option 태그를 제외하고, 나머지 태그의 텍스트를 추출하여 리스트로 반환
                option_text_list = [
                    option.text.strip()
                    for option in option_tags
                    if option.get("value") not in ["*", "**"]
                    and not option.get("selected")
                    and not option.get("disabled")
                ]

                return option_text_list
            else:
                print("'ProductOption0' select not found.")
                return None
        except Exception as e:
            # 예외 메시지 출력
            print(f"Error in get_options_Product_Option0: {e}")
            return None

    def get_options2_ec_product_button(self, driver, web):
        try:
            try:
                # class가 'ec-product-button'인 모든 ul 태그를 찾음
                ul_tags = driver.find_elements_by_css_selector("ul.ec-product-button")

                # 두 번째 'ec-product-button' 클래스를 가진 ul 태그 찾기
                second_ul_tag = ul_tags[1]

                # 두 번째 ul 태그 아래에 있는 모든 span 태그를 찾기
                span_tags = second_ul_tag.find_elements_by_tag_name("span")

                # span 태그 내의 텍스트 값을 추출하여 리스트로 반환
                span_text_list = [
                    span.text.strip()
                    for span in span_tags
                    if span.get_attribute("value") not in ["*", "**"]
                    and not span.get_attribute("selected")
                    and not span.get_attribute("disabled")
                ]

                if span_text_list:
                    return span_text_list
                else:
                    print("At least two 'ec-product-button' ul tags not found.")
                    pass
            except Exception as e:
                print(f"Error in get_span_text_list: {e}")
                pass
            try:
                # 추가적으로 구현할 내용이 있으면 여기에 작성하세요.
                pass
            except Exception as e:
                print(f"Error in additional implementation: {e}")
                return None
        except Exception as e:
            # 예외 메시지 출력
            print(f"Error in get_options_ec_product_button: {e}")
            return None

    def get_options3_ec_product_button(self, web, options, options2):
        try:
            try:
                # class가 'ec-product-button'인 모든 ul 태그를 찾음
                ul_tags = web.find_all("ul", {"class": "ec-product-button"})

                if len(ul_tags) >= 3:
                    # 두 번째 ul 태그 선택
                    second_ul_tag = ul_tags[2]

                    # 두 번째 ul 태그 아래에 있는 모든 span 태그를 찾음
                    span_tags = second_ul_tag.find_all("span")

                    # span 태그 내의 텍스트 값을 추출하여 리스트로 반환
                    span_text_list = [
                        span.text.strip()
                        for span in span_tags
                        if span.get("value") not in ["*", "**"]
                        and not span.get("selected")
                        and not span.get("dsiabled")
                    ]
                    print(span_text_list)
                    print(options)
                    if span_text_list == options:
                        return None
                    else:
                        return span_text_list
                else:
                    print("At least three 'ec-product-button' ul tags not found.")
                    pass
            except:
                pass
            try:
                a_tags = web.select(
                    "div.custom_color_option_wrap.flex_wrap.space_between > div:nth-child(1) > ul > li > a"
                )
                color_names = [a_tag["data-color-name"] for a_tag in a_tags]
                if color_names == options or color_names == options2:
                    return None
                else:
                    return color_names

            except:
                return None
        except Exception as e:
            # 예외 메시지 출력
            print(f"Error in get_options_ec_product_button: {e}")
            return None

    ##요
    ##기
    ##까
    ##지
    ##옵
    ##션
    ##함
    ##수
    # 요기까지옵션함수

    # 이미지 URl 옵션
    def get_image_url_master(self, web, domain, imageUrl):
        # 이미지 URL이 None이거나 도메인이 이미지 URL에 포함되어 있지 않으면 다른 함수로 대체
        if imageUrl is None or domain not in imageUrl:
            imageUrl = self.get_image_url_ThumbImage(web)

        # 이미지 URL이 None이거나 도메인이 이미지 URL에 포함되어 있지 않으면 다른 함수로 대체
        if imageUrl is None or domain not in imageUrl:
            imageUrl = self.get_image_url_BigImage(web)

        return imageUrl

    def get_image_url_BigImage(self, web):
        try:
            # 클래스명이 'BigImage'인 img 태그를 찾음
            image_tag = web.find("img", {"class": "BigImage"})

            # img 태그에서 src 속성값을 가져옴
            image_url = image_tag.get("src") if image_tag is not None else None

            # "https:" 추가
            if image_url and not image_url.startswith("https:"):
                image_url = "https:" + image_url

            return image_url
        except Exception as e:
            # 예외 메시지 출력
            print(f"Error in get_image_url_BigImage: {e}")
            return None

    def get_image_url_ThumbImage(self, web):
        try:
            # 클래스명이 'BigImage'인 img 태그를 찾음
            image_tag = web.find("img", {"class": "ThumbImage"})

            # img 태그에서 src 속성값을 가져옴
            image_url = image_tag.get("src") if image_tag is not None else None

            # "https:" 추가
            if image_url and not image_url.startswith("https:"):
                image_url = "https:" + image_url

            return image_url
        except Exception as e:
            # 예외 메시지 출력
            print(f"Error in get_image_url_BigImage: {e}")
            return None

    # 요
    # 기
    # 는
    # 이
    # 미
    # 지
    # 함
    # 수
    # 요기는이미지함수

    # domain = extract_domain(url) #domain에 앞 부분 추출
    def get_domain(self, url):
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        return domain

    def get_introduce(self, driver):
        try:
            if driver:
                # 첫 번째 방법 시도: class가 'cont'인 요소 찾기
                try:
                    element = driver.find_element(
                        By.CSS_SELECTOR,
                        "article.gallery.loaded",
                    )
                    inner_html = element.get_attribute("innerHTML")
                    if inner_html:
                        return inner_html
                    else:
                        print(0)

                except:
                    print(0)
                    pass
                try:
                    element = driver.find_element(
                        By.CSS_SELECTOR,
                        "#details div div",
                    )
                    inner_html = element.get_attribute("innerHTML")
                    if inner_html:
                        return inner_html
                    else:
                        print(1)

                except:
                    print(1)
                    pass

                # 두 번째 방법 시도: class가 'window-body'인 요소 찾기
                try:
                    element = driver.find_element(
                        By.CSS_SELECTOR, ".tab-cont.window ul.window-body li.active ul"
                    )
                    # innerHTML 가져오기
                    inner_html = element.get_attribute("innerHTML")
                    if inner_html:
                        return inner_html
                    else:
                        print(2)

                except:
                    print(2)
                    pass

                try:
                    element = driver.find_element(
                        By.CSS_SELECTOR,
                        "div.xans-element-.xans-product.xans-product-detail.detail_wrap div.detail_left_wrap_outer div div.detail_left.only_pc",
                    )
                    inner_html = element.get_attribute("innerHTML")
                    if inner_html:
                        return inner_html
                    else:
                        print(3)

                except:
                    print(3)
                    pass
                try:
                    p_elements = driver.find_elements(
                        By.CSS_SELECTOR,
                        "#layout-contents div.layout-contents-wrap div:nth-child(2) div:nth-child(3) div p img",
                    )

                    # 이미지 태그의 outerHTML을 저장할 리스트를 생성합니다.
                    img_tags = []

                    # 각 이미지 태그의 outerHTML을 추출하여 리스트에 추가합니다.
                    for img_element in p_elements:
                        img_tags.append(img_element.get_attribute("outerHTML"))

                    if inner_html:
                        return inner_html
                    else:
                        print(4)

                except:
                    print(4)
                    pass

                try:
                    introduce_div = driver.find_element(By.CLASS_NAME, "cont")

                    inner_html = introduce_div.get_attribute("innerHTML")

                    if inner_html != "" and "<img" in inner_html and inner_html != []:
                        return inner_html
                    else:
                        print(5)

                except:
                    print(5)
                    pass

                try:
                    introduce_div = driver.find_element(
                        By.CLASS_NAME,
                        "xans-element-.xans-product.xans-product-image.imgArea ",
                    )

                    inner_html = introduce_div.get_attribute("innerHTML")
                    if inner_html:
                        return inner_html
                    else:
                        print(6)

                except:
                    print(6)
                    pass

                print("모든 방법 실패: 소개 정보를 찾을 수 없음")
                return None
            else:
                print("웹 객체가 유효하지 않습니다.")
                return None
        except Exception as e:
            print(f"Error in get_introduce: {e}")
            return None

    def get_introduce_v2(self, driver):
        try:
            try:
                introduce_strong = driver.find_element(
                    By.CSS_SELECTOR,
                    "div.headingArea strong",
                )
                inner_html = introduce_strong.get_attribute("innerHTML")
                return inner_html
            except:
                pass
            try:
                introduce_p = driver.find_element(By.CSS_SELECTOR, "#view1 > p")
                inner_html = introduce_p.get_attribute("innerHTML")
                return inner_html
            except:
                pass
            try:
                introduce_div = driver.find_element(By.CSS_SELECTOR, "div.simple_wrap")
                inner_html = introduce_div.get_attribute("innerHTML")
                return inner_html
            except:
                pass
            try:
                introduce_dd = driver.find_element(By.CSS_SELECTOR, "dd.desc_short")
                inner_html = introduce_dd.get_attribute("innerHTML")
                return inner_html
            except:
                pass
            try:
                introduce_div = driver.find_element(
                    By.CSS_SELECTOR, "div#descDetail div#prdDetail div div"
                )
                inner_html = introduce_div.get_attribute("innerHTML")
                return inner_html
            except:
                pass
            try:
                introduce_tbody = driver.find_element(
                    By.CSS_SELECTOR,
                    "div.xans-element-.xans-product.xans-product-detaildesign table tbody tr:last-child",
                )
                inner_html = introduce_tbody.get_attribute("innerHTML")
                return inner_html
            except:
                pass
            try:
                introduce_dd = driver.find_element(
                    By.CSS_SELECTOR,
                    "#detail-information-slide > dl:nth-child(2) > dd",
                )
                inner_html = introduce_dd.get_attribute("innerHTML")
                return inner_html
            except:
                pass
            try:
                introduce_ol = driver.find_element(
                    By.CSS_SELECTOR,
                    "ul.xans-element-.xans-product.xans-product-additional.tab_tail li.open ol",
                )
                inner_html = introduce_ol.get_attribute("innerHTML")
                return inner_html
            except:
                pass
        except Exception as e:
            print(f"ERROR get_introduce2 : {e}")
            return None


# 테스트
if __name__ == "__main__":
    product_url = input("상품 상세 URL을 입력하세요: ")
    scraper = Cafe24Scraper()
    result = scraper.get_product_info(product_url)
    print(result)
