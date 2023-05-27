from queue import Queue
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import lxml


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

    out_text = "Keyword News\n"

    for news in news_list:
        a = news.find("a", class_="news_tit")
        title = a["title"]
        link = a["href"]
        # print(f"{title} {link=}")
        out_text += f"{title}\n{link}\n"

    out_text += "\n"

    browser.close()
    p.stop()

    result.put(out_text)


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

    out_text = "Sports News\n"

    for news in news_list:
        a = news.find("a", class_="title")
        title = a.text
        link = "https://sports.news.naver.com/" + a["href"]
        # print(f"{title} {link=}")
        out_text += f"{title}\n{link}\n"

    out_text += "\n"

    browser.close()
    p.stop()

    result.put(out_text)


def get_eClass(result: Queue().queue, id, pw):
    pass


def get_weather(result: Queue().queue, location):
    pass
