import json


class Record(object):
    """记录模块，用于记录断点和将抓取的结果写入文件"""
    def __init__(self):
        # 断点记录文件路径
        self.breakpoint = r'E:\20190320\taobao\breakpoint.txt'
        # 抓取结果文件路径
        self.result = r'E:\20190320\taobao\result.json'
        # 无搜索结果文件路径
        self.no_result = r'E:\20190320\taobao\no_result.txt'

    def record_breakpoint(self, keyword, page):
        """
        记录当前抓取失败的关键字和页号，以便后期重新采集
        :param keyword:
        :param page:
        :return:
        """
        with open(self.breakpoint, 'a+', encoding='utf-8', errors='ignore') as f:
            # 将关键字和页号写入文件
            f.write(keyword + '----' + str(page) + "\n")

    def record_result(self, data):
        """
        data:为字典的数据格式，转换为json存储
        :param data:
        :return:
        """
        with open(self.result, 'a+', encoding="utf-8", errors='ignore') as f:
            # 将数据转换为json
            result_ = json.dumps(data, ensure_ascii=False)
            f.write(result_ + "\n")

    def no_search_result(self, keyword):
        """
        将无搜索结果的关键字写入文件
        :param keyword:
        :return:
        """
        with open(self.no_result, 'a+', encoding="utf-8") as f:
            f.write(keyword + "\n")
