# coding: utf-8
from os.path import join

from xlrd import open_workbook
from xlutils.copy import copy


class ExcelHandler:
    def save(self, from_path, to_path, log_path):
        rb = open_workbook(from_path)
        wb = copy(rb)

        self.txt_to_excel(wb, log_path)

        wb.save(to_path)

    def _set_cell(self, workbook, sheet, col, row, content):
        workbook.get_sheet(sheet).write(col, row, content.decode('utf-8').strip())

    def txt_to_excel(self, workbook, log_path):
        files = [
            ('sale.txt', 3),
            ('sale_query.txt', 5),
            ('void.txt', 8),
            ('void_query.txt', 10),
            ('refund.txt', 13),
            ('refund_query.txt', 15)
        ]
        for (file, start_line) in files:
            with open(log_path + file) as f:
                lines = f.readlines()

            if lines == 11:
                _, _, req, _, _, _, res, _, _, _, notify = lines
                self._set_cell(workbook, 3, start_line, 3, req)
                self._set_cell(workbook, 3, start_line + 1, 3, res)
                self._set_cell(workbook, 3, start_line + 4, 3, notify)
            elif lines == 7:
                _, _, req, _, _, _, res = lines
                self._set_cell(workbook, 3, start_line, 3, req)
                self._set_cell(workbook, 3, start_line + 1, 3, res)


if __name__ == '__main__':
    eh = ExcelHandler()
    eh.save('./思创无限科技（北京）有限公司.xlsx', './output.xlsx', '../log/')
