from queue import Queue
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import lxml
from cryptography.fernet import Fernet


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

    if not news_list:
        browser.close()
        p.stop()
        result.put({"news": f"{keyword}에 대한 오늘 뉴스가 없습니다.\n"})
        return

    out_text = f"뉴스 - {keyword}\n"

    for news in news_list:
        a = news.find("a", class_="news_tit")
        title = a["title"]
        link = a["href"]
        # print(f"{title} {link=}")
        out_text += f"{title}\n{link}\n"

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

    browser.close()
    p.stop()

    result.put({"sports": out_text})


def eClass_check(result: Queue().queue, user):
    url = "https://eclass.tukorea.ac.kr/ilos/main/member/login_form.acl"

    p = sync_playwright().start()
    browser = p.chromium.launch(headless=True).new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"
    )
    page = browser.new_page()
    page.goto(url)

    page.locator('input[name="usr_id"]').fill(user[0])
    page.locator('input[name="usr_pwd"]').fill(user[1])
    page.locator("#login_btn").click()

    page.wait_for_timeout(500)

    browser.close()
    p.stop()

    if page.url == url:
        result.put(False)
        return
    result.put(True)


def get_eClass(result: Queue().queue, user):
    url = "https://eclass.tukorea.ac.kr/ilos/main/member/login_form.acl"

    if user[1] != "":
        key = user[2].encode()
        cipher_suite = Fernet(key)
        password = cipher_suite.decrypt(user[1].encode()).decode()
    else:
        result.put({"eClass": "eClass정보를 등록해주세요.\n"})
        return

    p = sync_playwright().start()
    browser = p.chromium.launch(headless=True).new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"
    )
    page = browser.new_page()
    page.goto(url)

    page.locator('input[name="usr_id"]').fill(user[0])
    page.locator('input[name="usr_pwd"]').fill(password)
    # page.locator('input[name="usr_id"]').fill("2019182003")
    # page.locator('input[name="usr_pwd"]').fill("3183129")
    page.locator("#login_btn").click()

    page.wait_for_timeout(1000)

    if page.url == url:
        browser.close()
        p.stop()
        result.put({"eClass": "로그인 실패\n/eclasslogin 을 통해 다시 입력해주세요.\n"})
        return

    soup = BeautifulSoup(page.content(), "lxml")

    today = soup.find("table", class_="course-datatable")
    subject = today.find_all("td", class_="subject")

    subject_list = set()
    for sub in subject:
        subject_list.add(sub.text)

    # print(subject_list)

    if subject_list:
        out_text = "오늘 수업\n"
        for sub in subject_list:
            out_text += f"{sub}\n"
    else:
        out_text = "오늘은 수업이 없습니다.\n"

    todo = soup.find("div", title="Todo List")
    todo = todo.find("div", id="todoList_cnt")
    if todo:
        out_text += "할일 - "
        out_text += todo.text + "개\n"

    alarm = soup.find("div", title="알림")
    alarm = alarm.find("div", id="notice_cnt")
    if alarm:
        out_text += "알림 - "
        out_text += alarm.text + "개\n"

    browser.close()
    p.stop()

    result.put({"eClass": out_text})


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
        result.put({"weather": "날씨 정보를 가져올 수 없습니다.\n"})
        browser.close()
        p.stop()
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

    out_text = f"날씨 - {location}\n"
    out_text += f"미세먼지 {dust1.text}\n초미세먼지 {dust2.text}\n"
    out_text += f"강수확률 오전{rainfall1} 오후{rainfall2}\n"
    out_text += f"{temp1} {temp2}\n"

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
