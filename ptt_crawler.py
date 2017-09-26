# coding=utf-8
'''
$ python ptt_crawler.py gossiping 10000 9999 ptt
'''
import sys
import urllib
import json
import time

import requests
from bs4 import BeautifulSoup as BS

# POST 給驗證年齡的資料
LOAD = {
    "from": "/bbs/Gossiping/index.html",
    "yes": "yes"
}


def get_all_articles(base_index, start_pages, pages):
    '''

    base_index: 看板的原始網址 (e.g. "https://www.ptt.cc/bbs/Gossiping/index.html")
    start_pages: 從倒數第幾頁開始, 1 = 從最後一頁開始抓
    pages: 總共抓幾頁, 向最後一頁前進
    (base,5,2): 從倒數第五頁開始抓兩頁
    return: Article list
    '''

    if pages > start_pages:
        print("pages error!")
        return None
    rs = requests.session()
    re = rs.get(base_index)

    # 處理 18 禁同意頁面
    if "over18" in re.url:
        rs.post("https://www.ptt.cc/ask/over18", data=LOAD)

    re = rs.get(base_index)
    soup = BS(re.text, "lxml")  # parse a document by XML parser

    # 利用網頁內 "上頁" 按鈕的網址來得知當前 index
    prev_page = soup.find_all("a", "btn wide")[1].get("href")
    prev_index = prev_page[(prev_page.find("index") + 5): prev_page.find(".html")]
    start_index = int(prev_index) + 1 - (start_pages - 1)
    # 有時會有上一頁剛好是最後一頁的情形, 此時算出來的要再減一
    if BS(rs.get(base_index[:-5] + str(start_index) + ".html").text, "lxml").find(text="500 - Internal Server Error"):
        start_index -= 1

    article_list = []

    # 先存下全部所要頁面的 index 數字 (.../index12345.html)
    index_list = [i for i in range(start_index, start_index + pages)]
    no = 1

    comma = False
    for idx in index_list:

        cur_url = base_index[:-5] + str(idx) + ".html"
        re = rs.get(cur_url)
        soup = BS(re.text, "lxml")

        bs_title_list = soup.find_all("div", "r-ent")  # 獲取標題列表,用來進去各篇文章

        print("---- start index {0} ----\n".format(idx))

        for ar in bs_title_list:
            title_link = ar.find("a")
            # 不合規格的文章判斷(如:"本文已被刪除")
            if title_link:
                title_link = title_link.get("href")  # 文章網址
                url = urllib.parse.urljoin(cur_url, title_link)
                article_data = get_article(rs.get(url))  # dict
                if article_data:
                    print("no.{0} {1} ok".format(no, url))
                    article_data["a_no"] = no
                    json_data = ("," if comma else "") + json.dumps(article_data, ensure_ascii=False, indent=4,
                                                                    sort_keys=True)
                    article_list.append(json_data)
                    if not comma:
                        comma = True

                    no += 1

            # 避免被當作攻擊
            time.sleep(0.1)

        print("\n---- finish index {0} ----\n".format(idx))

        time.sleep(0.5)

    rs.close()

    return start_index, article_list


def get_article(re):
    soup = BS(re.text, "lxml")
    metalines = soup.find_all("div", "article-metaline")

    try:
        # 文章作者
        author = check_data(metalines[0].find("span", "article-meta-value"))

        # 文章標題
        title = check_data(metalines[1].find("span", "article-meta-value"))

        # 文章時間
        a_time = check_data(metalines[2].find("span", "article-meta-value"))
    except Exception as e:
        print("error infomation(e.g. author,title,time) at", re.url)
        print(repr(e))
        return None

    # 文章內容
    try:

        bs_main_content = soup.find("div", id="main-content")
        # 利用時間和文章結尾來做分割
        sp1 = bs_main_content.get_text().split("--\n※ 發信站")
        sp2 = sp1[0].split(a_time)
        content = sp2[1]
    except Exception as e:
        print("error content at", re.url)
        print(repr(e))
        return None

    # 回應內容
    good = 0
    boo = 0
    arrow = 0
    bs_comments = soup.find_all("div", "push")
    comments = []
    if bs_comments:
        for c in bs_comments:

            # 處理 "檔案過大！部分文章無法顯示" 的 "warning-box" class
            if "warning-box" in c.get("class"):
                continue

            c_type = c.find("span", class_="push-tag").get_text().strip()
            if c_type == "→":
                arrow += 1
            elif c_type == "推":
                good += 1
            elif c_type == "噓":
                boo += 1
            c_id = c.find("span", class_="push-userid").get_text()
            c_content = c.find("span", class_="push-content").get_text()

            comments.append({"a_id": c_id, "b_type": c_type, "c_content": c_content.strip(": ")})

    statistics = {"a_total": good - boo, "b_good": good, "c_boo": boo, "d_arrow": arrow}
    data = {"b_title": title, "c_author": author, "d_content": content, "e_comments": comments,
            "f_statistics": statistics,
            "g_url": re.url}

    return data


def check_data(bs_tag):
    if bs_tag:
        return bs_tag.get_text()
    else:
        print("format error")
        return None


def main(board, start_pages, pages, filename):
    base_index = "https://www.ptt.cc/bbs/" + board + "/index.html"
    LOAD["form"] = "/bbs/" + board + "/index.html"

    start_index, article_list = get_all_articles(base_index, start_pages, pages)  # return (start_index,string list)

    # open 時要以 UTF-8 開啟,否則在 windows 下以 cp950 去做解碼會有誤
    with open("{0}_pages_{1}_start_index_{2}.json".format(filename, pages, start_index), "w", encoding="UTF-8") as f:
        f.write("[\n")  # json array
        for ar in article_list:
            f.write(ar)
        f.write("\n]")

    print("==== Complete! ====")


if __name__ == "__main__":
    sec = time.time()
    main(board=sys.argv[1], start_pages=int(sys.argv[2]), pages=int(sys.argv[3]), filename=sys.argv[4])
    print("{0:.2f} sec".format(time.time() - sec))
