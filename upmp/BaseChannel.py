__author__ = 'edwin'

from collections import OrderedDict
import string, random

class BaseChannel:
    def gen_sign_string(self, para, filter_para=[]):
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

# d = {'k2': 1, 'k1': 'www.ex.com/dfs?fd=fd&df=fd', 'k0': '', '4': 0, 'k5': False, 'k4': 0}
#
# filter_para = ['k2']
# print(gen_sign_string(d, filter_para))
# print(urllib.parse.urlencode(d, True, '', None))

# protected function genSignString(&$para, $filter = NULL)
# {
# if (!empty($filter))
# {
# $para = $this->paraFilter($para, $filter);
# }
# ksort($para);
# reset($para);
#
# return $this->createLinkstring($para);
# }
# protected function createLinkstring($para)
# {
#     $arg = "";
#     while (list ($key, $val) = each($para))
#     {
#         $arg .= $key."=".$val."&";
#     }
#     $arg = substr($arg, 0, count($arg) - 2);
#
#     if (get_magic_quotes_gpc())
#     {
#         $arg = stripslashes($arg);
#     }
#
#     return $arg;
# }