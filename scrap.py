from queue import Queue
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import lxml

SPORTS = {
    "kbaseball": "야구",
    "wbaseball": "해외야구",
    "kfootball": "축구",
    "wfootball": "해외축구",
    "basketball": "농구",
    "volleyball": "배구",
    "golf": "골프",
    "general": "일반",
}


def get_news(result: Queue().queue, keyword):
    url = f"https://search.naver.com/search.naver?where=news&query={keyword}&sm=tab_opt&sort=0&photo=0&field=0&pd=4&ds=&de=&docid=&related=0&mynews=0&office_type=0&office_section_code=0&news_office_checked=&nso=so%3Ar%2Cp%3A1d&is_sug_officeid=0"
    # url = "https://search.naver.com/search.naver?where=news&query=%EB%84%A5%EC%8A%A8&sm=tab_opt&sort=0&photo=0&field=0&pd=4&ds=&de=&docid=&related=0&mynews=0&office_type=0&office_section_code=0&news_office_checked=&nso=so%3Ar%2Cp%3A1d&is_sug_officeid=0"

    p = sync_playwright().start()
    browser = p.chromium.launch(headless=True).new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"
    )
    page = browser.new_page()
    page.goto(url)

    soup = BeautifulSoup(page.content(), "lxml")
    news_list = soup.find_all("div", class_="news_area")
    news_list = news_list[:3]

    out_text = f"뉴스 - {keyword}\n"

    for news in news_list:
        a = news.find("a", class_="news_tit")
        title = a["title"]
        link = a["href"]
        # print(f"{title} {link=}")
        out_text += f"{title}\n{link}\n"

    out_text += "\n"

    browser.close()
    p.stop()

    result.put({"news": out_text})


def get_sports_news(result: Queue().queue, sports):
    url = f"https://sports.news.naver.com/{sports}/news/index?isphoto=N"
    # url = "https://sports.news.naver.com/wfootball/news/index?isphoto=N"

    p = sync_playwright().start()
    browser = p.chromium.launch(headless=True).new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"
    )
    page = browser.new_page()
    page.goto(url)

    soup = BeautifulSoup(page.content(), "lxml")
    news_list = soup.find("div", class_="news_list")
    news_list = news_list.find_all("li")
    news_list = news_list[:3]

    out_text = f"스포츠 - {SPORTS[sports]}\n"

    for news in news_list:
        a = news.find("a", class_="title")
        title = a.text
        link = "https://sports.news.naver.com/" + a["href"]
        # print(f"{title} {link=}")
        out_text += f"{title}\n{link}\n"

    out_text += "\n"

    browser.close()
    p.stop()

    result.put({"sports": out_text})


def get_eClass(result: Queue().queue, id, pw):
    pass


def get_weather(result: Queue().queue, location):
    url = f"https://search.naver.com/search.naver?sm=tab_hty.top&where=nexearch&query={location}+날씨"
    # url = "https://search.naver.com/search.naver?sm=tab_hty.top&where=nexearch&query=안산+중앙동+날씨"

    p = sync_playwright().start()
    browser = p.chromium.launch(headless=True).new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"
    )
    page = browser.new_page()
    page.goto(url)

    soup = BeautifulSoup(page.content(), "lxml")
    weather = soup.find("section", class_="sc_new cs_weather_new _cs_weather")

    if weather is None:
        result.put("날씨 정보를 가져올 수 없습니다.")
        return

    # 미세먼지 정보
    dust = weather.find("ul", class_="today_chart_list")
    dust = dust.find_all("li")

    dust = dust[:2]

    dust1 = dust[0].find("span", class_="txt")
    dust2 = dust[1].find("span", class_="txt")

    # print(f"미세먼지 {dust1.text} 초미세먼지 {dust2.text}")

    # 날씨 정보
    weather = weather.find("li", class_="week_item today")
    rainfall = weather.find_all("span", class_="rainfall")
    rainfall1 = rainfall[0].text
    rainfall2 = rainfall[1].text

    # print(f"강수확률 {rainfall1} {rainfall2}")

    temp = weather.find("span", class_="temperature_inner")
    temp1 = temp.find("span", class_="lowest").text
    temp2 = temp.find("span", class_="highest").text

    # print(f"{temp1} {temp2}")

    out_text = "날씨\n"
    out_text += f"미세먼지 {dust1.text} 초미세먼지 {dust2.text}\n"
    out_text += f"강수확률 오전{rainfall1} 오후{rainfall2}\n"
    out_text += f"{temp1} {temp2}\n"

    out_text += "\n"

    browser.close()
    p.stop()

    result.put({"weather": out_text})


def location_check(result, location):
    url = f"https://search.naver.com/search.naver?sm=tab_hty.top&where=nexearch&query={location}+날씨"

    p = sync_playwright().start()
    browser = p.chromium.launch(headless=True).new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"
    )
    page = browser.new_page()
    page.goto(url)

    soup = BeautifulSoup(page.content(), "lxml")
    weather = soup.find("section", class_="sc_new cs_weather_new _cs_weather")

    browser.close()
    p.stop()

    if weather is None:
        result.put(False)
        return
    result.put(True)
