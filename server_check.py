# coding: utf-8

import datetime
import os
import json


class ServerCheck:
    def get_all_untest_merchant_files(self, path):
        """
        获取所有未测试商户的商户信息文件
        :param path:
        :return: 所有未测试商户的商户信息文件列表
        """
        merchant_files = []
        test_files = []
        for (dirpath, dirnames, filenames) in os.walk(path):
            for name in filenames:
                file_name, file_extension = os.path.splitext(name)

                if name.endswith('.txt'):
                    merchant_files.append(file_name)
                elif name.endswith('.xlsx'):
                    test_files.append(file_name)
            break

        return [item for item in merchant_files if item not in test_files]

    def get_merchant_info(self, path):
        """
        获取指定的未测试商户的商户信息
        :param path:
        :return: 指定的未测试商户的商户信息
        """
        with open(path) as f:
            lines = f.readlines()

        if len(lines) == 3:
            mer_name, mer_id, mer_key = lines[0].strip(), lines[1].strip(), lines[2].strip()
            return mer_name, mer_id, mer_key
        else:
            return None

    def get_all_untest_merchant_json(self, root_path):
        """
        获取所有未测试商户的商户信息（JSON格式），并记录到log文件中
        :param root_path:
        :return:所有未测试商户的商户信息（JSON格式）
        """
        paths = self.search_test_dir(root_path)
        if paths is None:
            return None

        data = dict()
        merchants = list()
        temp_merchants = list()
        data['count'] = 0

        for path in paths:
            file_names = self.get_all_untest_merchant_files(path)
            data['count'] += len(file_names)

            for fname in file_names:
                mer_file = os.path.join(path, fname + '.txt')
                mer_name, mer_id, mer_sk = self.get_merchant_info(mer_file)
                merchant = dict()
                merchant['name'] = mer_name
                merchant['id'] = mer_id
                merchant['sk'] = mer_sk
                merchant['path'] = path
                merchant['file'] = fname + '.txt'
                temp_merchants.append(merchant.copy())

                # 客户端不接收敏感数据
                del merchant['sk']
                del merchant['path']
                del merchant['file']
                merchants.append(merchant)

        # 将未测试商户数据记录到文件
        data['merchants'] = temp_merchants
        with open('untest_merchant.txt', 'w') as f:
            f.write(json.dumps(data))

        # 将部分数据发送给客户端
        data['merchants'] = merchants

        return data

    def search_test_dir(self, root_path):
        """
        获取按当前年月为路径的目录
        :param root_path:
        :return:
        """
        # 获取当前年月
        date = datetime.date.today().strftime("%Y/%m")

        path = os.path.join(root_path, date)

        # 获取测试目录
        for (dirpath, dirnames, filenames) in os.walk(path):
            return [os.path.join(dirpath, dirname) for dirname in dirnames]

    def get_merchant_info_from_log(self, mer_id):
        """
        从log文件中获取商户信息
        :param mer_id: UPMP商户ID
        :return:
        """
        with open('untest_merchant.txt') as f:
            json_data = f.readline()

        data = json.loads(json_data)

        for item in data['merchants']:
            if item['id'] == mer_id:
                return item

        return None

    def is_merchant_test_done(self, log_path):
        """
        检查商户是否已完成测试
        :param log_path: 商户log路径
        :return: True or False
        """
        for _, _, filenames in os.walk(log_path):
            temp = ['charge.txt', 'void.txt', 'refund.txt', 'charge_query.txt', 'void_query.txt', 'refund_query.txt']
            return sorted(filenames) == sorted(temp)


if __name__ == "__main__":
    root_path = "./data"
    sc = ServerCheck()
    sc.is_merchant_test_done(root_path+'/2014/09/1/log/')
    # data = sc.get_all_untest_merchant_json(root_path)
    # import json
    # print(json.dumps(data))
