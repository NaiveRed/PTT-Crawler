# PTT-Crawler

A web crawler for PTT Web BBS.

因專題需求用來爬取 PTT Web 的內容，應適用於大部分看板。  
(e.g. Gossiping, C_Chat)

## 環境配置

主要基於 Python3 ，並利用 pip 安裝其他套件：

* [beautifulsoup4](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#)
* [requests](http://docs.python-requests.org/en/master/)
* [lxml](https://pypi.python.org/pypi/lxml)

## 使用說明

`python ptt_crawler.py <board_name> <start_page> <pages> <file_name>`  

`board_name`: 看板名稱，例如："Gossiping","C_Chat"。  
`start_page`: 起始頁面，計算方式為看板網頁(<https://www.ptt.cc/bbs/Gossiping/index.html>)，往前數第幾頁。例如當前 index 為 25126 ， `start_page = 4` 就是從 index 25123 開始抓取。  
`pages`: 總共抓幾頁。  
`file_name`: 抓取下來的檔案名稱為 `<file_name>_pages_<pages>_start_index_<start_page>.json` 。

抓取內容：

* 標題
* 作者
* 內文
* 下方推文
  * 推文 ID
  * 推、噓、箭頭
  * 內容
* 推噓統計
* 網址

### 格式

以 json 格式儲存。

    [{
    "a_no": 1,
    "b_title": "[問卦] 範例標題",
    "c_author": "oooo (暱稱)",
    "d_content": "這是一篇範例文章",
    "e_comments": [
        {
            "a_id": "xxxx",
            "b_type": "推",
            "c_content": "這是一句範例推文"
        },
        ...
    ],
    "f_statistics": {
        "a_total": -2,
        "b_good": 10,
        "c_boo": 12,
        "d_arrow": 8
        },
    "g_url": "https://www.ptt.cc/bbs/Gossiping/oooo.html"
    },
    ...
    ]

### 範例

`python ptt_crawler.py gossiping 4 3 test`

當前最新 index 為 25126 ，將會抓取 25123 到 25125 共三頁的文章內容。  
檔案存在當前目錄下，名稱為：`test_pages_3_start_index_25123.json` 。  

p.s. 通常最後一頁會有各式置底文(如板規)，所以並不會抓取最後一頁

執行畫面(略過部分)：

![runtime_pic1](https://imgur.com/sM6H9AQ.png)

![runtime_pic2](https://imgur.com/RTThkwh.png)

## 特殊狀況

1. 當文章顯示被刪除或是內容缺少標題等項目時，該文章將會被 **跳過**。
2. 內文解析方法有待修改。有 **簽名檔** 的狀況，可能會導致內文包含簽名檔、提早將文章切斷或是誤抓簽名檔內的推文等狀況。
3. 其他特殊的文章格式，可能會有非預期的狀況(目前我還沒遇過)。

此外為避免被 PTT 當作攻擊，程式碼內有數次刻意延遲，但由於不太清楚此方面的運作機制，了解的人可依需求自行調整。

## 程式編寫

網路上已有許多關於 PTT 爬蟲的相關教學，以下提供幾個當初撰寫時所參考的網站和 repo。

Crawler:

* [leVirve/CrawlerTutorial](https://github.com/leVirve/CrawlerTutorial)
* [twtrubiks/PTTcrawler](https://github.com/twtrubiks/PTTcrawler)
* [zake7749/PTT-Crawler](https://github.com/zake7749/PTT-Crawler)

requests:

* [Python HTTP 库：requests 快速入门](https://liam0205.me/2016/02/27/The-requests-library-in-Python/)

處理 over18 的頁面(我已滿 18 歲)：

* https://www.youtube.com/watch?v=G5MDpnGsE-k

編碼：

* <https://www.ptt.cc/bbs/Python/M.1380034106.A.553.html>
* <https://www.ptt.cc/bbs/Python/M.1412756706.A.390.html>

## 備註

此程式主要用於練習 Python 及專題資料抓取，如有發現問題還煩請告知。

除了上面範例測試的，以下提供之前抓取 **八卦版(Gossiping)** 的檔案：

* [4999 頁](https://drive.google.com/open?id=0B2oDNcJUcAmxanZscUwxZXg1NlE) 約為 500 MB
* [9999 頁](https://drive.google.com/open?id=0B2oDNcJUcAmxc3Z3cnVkQnowSzg) 約為 1 GB

(Google drive)