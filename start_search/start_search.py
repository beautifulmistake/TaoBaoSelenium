import time

from selenium import webdriver
from selenium.common.exceptions import TimeoutException, InvalidElementStateException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pyquery import PyQuery as pq
from record.record import Record


class TaoBaoStartSearch(object):
    """
    尝试在不登录的情况下直接根据关键字进行搜索
    """
    def __init__(self):
        # 在不登陆的情况下：淘宝的搜索页面
        self.index_url = "https://s.taobao.com/search?q={}"
        # 浏览器对象
        self.browser = webdriver.Chrome()
        # 浏览器加载对象
        self.wait = WebDriverWait(self.browser, 20)
        # 记录对象
        self.record = Record()

    def index_page(self, keyword):
        """
        尝试在不登录的情况下获取搜索数据
        :param keyword:
        :return:
        """
        print("正在抓取的关键字：", keyword)
        # 发起请求
        self.browser.get(self.index_url.format(keyword))
        # 查看响应的页面
        # print("查看获取的响应页面：", self.browser.page_source)
        # 首先判断是否有搜索结果
        if not self.is_result():
            # 获取结果的总页数,使用find_element_by_xpath()也可以
            total = self.wait.until(EC.presence_of_element_located(
                (By.XPATH, '//div[@id="J_relative"]/div/div/div[@class="pager"]/ul/li[2]'))).text.split("/")[1]
            # 遍历传入页号采集
            for page in range(1, int(total) + 1):
                try:
                    if page > 1:
                        self.skip_page(page)
                    print("正在采集[%s]关键字的[%s]页" % (keyword, page))
                    # 等待商品信息加载完成
                    self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.m-itemlist .items .item')))
                    # 采集搜索的商品信息
                    self.get_products()
                except TimeoutException:
                    # 增加页面跳转失败时，将当前关键字和页号记录文件
                    self. record.record_breakpoint(keyword, page)
                except InvalidElementStateException:
                    # 首先刷新页面
                    self.browser.refresh()
                    # 等待商品信息加载完成
                    self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.m-itemlist .items .item')))
                    # 采集搜索的商品信息
                    self.get_products()
        else:
            # 没有搜索结果将关键字写入文件
            print("关键字[%s]无搜索结果，写入文件" % keyword)
            self.record.no_search_result(keyword)

    def skip_page(self, num):
        """
        跳转指定的页号
        :param num:
        :return:
        """
        # 跳转页号的输入框
        input_ = self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#mainsrp-pager div.form> input'))
        )
        # 提交按钮
        submit = self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#mainsrp-pager div.form> span.btn.J_Submit'))
        )
        # 清空输入框
        input_.clear()
        # 传入要跳转的页号
        input_.send_keys(num)
        # 提交，跳转
        submit.click()
        # 判断是否跳转成功
        self.wait.until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR,
                                              '#mainsrp-pager li.item.active > span'), str(num))
        )

    def is_result(self):
        """
        判断是否有匹配结果，需要注意的是在捕获异常的时候得是：selenium.common.exceptions import TimeoutException
        如果捕获的是TimeOutError则依然会报错
        这是第一种情况：直接就是无搜索结果
        :return:
        """
        try:
            self.wait.until(EC.presence_of_element_located((By.XPATH, '//div[@id="mainsrp-tips"]//ul')))
            return True
        except TimeoutException:
            return False

    def get_products(self):
        """
        提取商品数据
        :return:
        """
        # 获取加载完成的页面
        html = self.browser.page_source
        # 使用pyquery解析页面
        doc = pq(html)
        # 定位包含商品信息的items
        items = doc('#mainsrp-itemlist .items .item').items()
        # 获取每一个商品项的信息
        for item in items:
            product = {
                'image': item.find('.pic .img').attr('data-src'),
                'price': item.find('.price').text(),
                'deal': item.find('.deal-cnt').text(),
                'title': item.find('.title').text(),
                'product_detail': item.find('.title .J_ClickStat').attr('href'),
                'shop': item.find('.shop').text(),
                'shop_detail': item.find('.shop .shopname').attr('href'),
                'location': item.find('.location').text()
            }
            print("查看商品信息：", product)
            # 将数据写入文件
            self.record.record_result(product)


# 测试代码
if __name__ == "__main__":
    # 创建对象
    t = TaoBaoStartSearch()
    # 发起请求
    t.index_page("土豆法")
    t.browser.quit()
