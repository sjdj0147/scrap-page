from flask import Flask, render_template, request
from urllib.parse import unquote, urlparse
from controller.imweb import ImwebScraper
from controller.cafe24 import Cafe24Scraper
from controller.naver import NaverScraper
from controller.sixshop import SixshopScraper
import json

app = Flask(__name__, template_folder="view")

# Scraper 객체 생성
cafe24_scraper = Cafe24Scraper()
naver_scraper = NaverScraper()
imweb_scraper = ImwebScraper()
sixshop_scraper = SixshopScraper()


# 라우트 및 뷰 함수 정의
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/scrape", methods=["POST"])
def scrape():
    url = request.form["url"]
    if url:
        if "smartstore" in url:
            scraper = naver_scraper
        elif "idx" in url:
            scraper = imweb_scraper
        elif "display" in url:
            scraper = cafe24_scraper
        else:
            scraper = sixshop_scraper

    else:
        return render_template("error.html", message="Unsupported URL")

    try:
        result_str = scraper.get_product_info(url)
        result_dict = json.loads(result_str)
        # "상세 설명"을 Markup으로 감싸서 전달
        introduce_value = result_dict.get("introduce", "")
        result_introduce = json.dumps(
            introduce_value,
            ensure_ascii=False,
        )

        try:
            introduce_value_v2 = result_dict.get("introduce_v2", "")
            result_introduce_v2 = json.dumps(
                introduce_value_v2,
                ensure_ascii=False,
            )
        except:
            pass
        return render_template(
            "result.html",
            result_dict=result_dict,
            result_intro=result_introduce,
            result_intro_v2=result_introduce_v2,
        )

    except Exception as e:
        return render_template("error.html", message=str(e))


if __name__ == "__main__":
    app.run(debug=True)
