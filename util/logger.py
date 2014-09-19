# coding: utf-8

import os


class Logger(object):
    """
    日志记录
    """

    # @staticmethod
    # def config(log_path, log_file):
    # """
    #     日志记录配置
    #     """
    #     logging.basicConfig(filename=os.path.join(log_path, log_file),
    #                         format='%(message)s',
    #                         level=logging.INFO)

    @staticmethod
    def logging(log_path, log_file, msg):
        """
        记录一行消息
        """
        # logging.info(msg)

        # 若log_path不存在，则创建该目录
        if not os.path.isdir(log_path):
            os.mkdir(log_path)

        with open(os.path.join(log_path, log_file), 'a') as f:
            f.write(msg + '\n')

if __name__ == '__main__':
    Logger.logging('./log', 'log.txt', 'test')
