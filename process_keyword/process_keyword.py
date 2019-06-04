import redis


class ProcessKeyword(object):
    """处理带抓取关键字的导入导出"""
    def __init__(self):
        # 数据库链接对象   password='pengfeiQDS',
        self.conn = redis.StrictRedis(host='127.0.0.1', port=6379, db=0, decode_responses=True)

    def set_keyword(self, path):
        """
        指定文件的路径，读取文件，将关键字入库
        :param path: 关键字文件路径
        :return:
        """
        with open(path, 'r', encoding='utf-8') as f:
            # 读取所有的关键字
            lines = f.readlines()
            # 关键字总数量
            lenth = len(lines)
            # 遍历，存储
            for index in range(lenth):
                keyword = lines[index].strip()
                self.conn.set(index, keyword)
            print("总共转存[%s]个关键字" % lenth)

    def get_keyword(self):
        """
        获取关键字
        :return:
        """
        # 获取关键字的总数
        size = self.conn.dbsize()
        # for index in range(1, 5):
        for index in range(size):
            yield self.conn.get(str(index))


# 测试代码
if __name__ == "__main__":
    # 关键字文件路径
    path = r'G:\工作\工作计划\9类.txt'
    # 创建对象
    p = ProcessKeyword()
    # 调用存储方法
    p.set_keyword(path)
