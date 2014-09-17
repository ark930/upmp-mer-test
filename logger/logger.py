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
        with open(os.path.join(log_path, log_file), 'a') as f:
            f.write(msg + '\n')
