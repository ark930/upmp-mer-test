__author__ = 'edwin'

from collections import OrderedDict
import string, random

class BaseChannel:
    def _gen_sign_string(self, para, filter_para=[]):
        filtered_para = self.para_filter(para, filter_para)
        # od = OrderedDict(sorted(filtered_para.items()))

        return self.create_link_string(self.sort_dict(filtered_para))


    def para_filter(self, para, filter_para=[]):
        return {key: para[key] for key in list(set(para.keys()) - set(filter_para)) if para[key] != ''}

    def create_link_string(self, para):
        return '&'.join(['%s=%s' % (key, value) for (key, value) in para.items()])

    def create_linkstring_with_quota(self, para):
        return '&'.join(['%s="%s"' % (key, value) for (key, value) in para.items()])

    def create_linkstring_urlencode(self, para):
        return '&'.join(['%s="%s"' % (key, value) for (key, value) in para.items()])  # bs = BaseChannel();

    def sort_dict(self, para):
        return OrderedDict(sorted(para.items()))

    def random_id(self, length):
        return ''.join(random.choice(string.ascii_letters + string.digits) for i in range(length))
