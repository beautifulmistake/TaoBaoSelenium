"""运行的主逻辑"""
import time
from selenium.common.exceptions import TimeoutException, InvalidElementStateException
from process_keyword.process_keyword import ProcessKeyword
from start_requests.start_request import TaoBaoStartRequest
from start_search.start_search import TaoBaoStartSearch

if __name__ == "__main__":
    #################################################################
    # /******这是在不用模拟登录的情况下使用的******/
    # 创建爬虫对象
    # t = TaoBaoStartSearch()
    # # 创建数据库链接对象
    # p = ProcessKeyword()
    # # 获取所有的关键字
    # keywords = p.get_keyword()
    # # 遍历关键字，发起请求抓取数据
    # for keyword in keywords:
    #     try:
    #         t.index_page(keyword)
    #         # 调整抓取的速率
    #         # time.sleep(30)
    #     except (TimeoutException, InvalidElementStateException):
    #         t.browser.refresh()
    # print("所有的关键字抓取完成，关闭浏览器")
    # t.browser.close()
    #######################################################################
    # /*******以下代码是在模拟登录后使用的代码******/
    # 创建爬虫对象
    t = TaoBaoStartRequest('penggeilove', 'pengfei38')
    # 创建数据库链接对象
    p = ProcessKeyword()
    # 获取所有的关键字
    keywords = p.get_keyword()
    # 模拟登录
    t.login()
    # 遍历关键字，发起请求抓取数据
    for keyword in keywords:
        try:
            t.get_input(keyword)
            # 调整抓取的速率
            # time.sleep(30)
        except (TimeoutException, InvalidElementStateException):
            t.browser.refresh()
    print("所有的关键字抓取完成，关闭浏览器")
    t.browser.close()
