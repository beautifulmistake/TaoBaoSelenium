import time
from pyquery import PyQuery as pq
from selenium.webdriver.common.keys import Keys
from record.record import Record
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, InvalidElementStateException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class TaoBaoStartRequest(object):
    """
    使用selenium+chrome模拟登陆淘宝
    采取的策略为当当前账号被检测到时，更换账号模拟登陆
    """
    def __init__(self, username, password):
        # 记录对象
        self.record = Record()
        # 手动输入账号密码的登陆界面,登录成功后跳转到搜索页面
        self.url = "https://login.taobao.com/member/login.jhtml?redirectURL=https%3A%2F%2Fwww.taobao.com%2F"
        # 浏览器对象
        self.browser = webdriver.Chrome()
        # 浏览器加载对象
        self.wait = WebDriverWait(self.browser, 20)
        # 淘宝账号
        self.username = username
        # 淘宝登陆密码
        self.password = password

    def login(self):
        """
        请求获取登陆界面，自动化输入账号密码，完成登陆，获取搜索界面
        :return:
        """
        # 删除所有的cookies， 请求获取登录界面
        self.browser.delete_all_cookies()
        self.browser.get(self.url)
        # 转换手动输入账号密码界面
        password_login = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'login-switch')))
        if password_login:
            password_login.click()
            time.sleep(1)
        # 获取用户名的输入框
        username = self.wait.until(EC.presence_of_element_located((By.ID, 'TPL_username_1')))
        # 获取账号的输入框
        password = self.wait.until(EC.presence_of_element_located((By.ID, 'TPL_password_1')))
        # 获取登陆按钮
        submit = self.wait.until(EC.element_to_be_clickable((By.ID, 'J_SubmitStatic')))
        # 填写表单内容
        username.send_keys(self.username)
        password.send_keys(self.password)
        time.sleep(1)
        # 提交表单
        submit.click()

    def password_error(self):
        """
        判断是否密码错误
        :return:
        """
        try:
            return WebDriverWait(self.browser, 5).until(EC.text_to_be_present_in_element_value(
                (By.CLASS_NAME, 'error'), '你输入的密码和账户名不匹配'))
        except TimeoutException:
            return False

    def login_successfully(self):
        """
        判断是否登陆成功
        :return:
        """
        try:
            return bool(WebDriverWait(self.browser, 5).until(EC.presence_of_element_located(
                (By.CLASS_NAME, 'site-nav-login-info-nick '))))
        except TimeoutException:
            return False

    def get_input(self, keyword):
        """
        获取搜索框，输入关键字，搜索
        :param keyword:
        :return:
        """
        # 如果登陆成成功
        if self.login_successfully():
            # 获取搜索框
            search_key = self.wait.until(EC.presence_of_element_located((By.ID, 'q')))
            # 获取搜索按钮
            # search_click = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'btn-search tb-bg')))
            # 首先清空输入框
            search_key.clear()
            # 填写表单内容
            search_key.send_keys(keyword)
            time.sleep(1)
            # 提交表单
            # search_click.click()
            # 不知道为何搜索按钮就无法获得了，总是报错，故修改成使用键盘 ENTER 键来操作
            search_key.send_keys(Keys.ENTER)
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
                        self.record.record_breakpoint(keyword, page)
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
    t = TaoBaoStartRequest('penggeilove', 'pengfei38')
    # 模拟登陆
    t.login()
    # 搜索
    t.get_input("土豆")
