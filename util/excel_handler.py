# coding: utf-8
import os

from xlrd import open_workbook
from xlutils.copy import copy


class ExcelHandler:
    def save(self, template_path, target_path, log_path):
        rb = open_workbook(template_path)
        wb = copy(rb)

        self.log_to_excel(wb, log_path)

        wb.save(target_path)

    def _set_cell(self, workbook, sheet, col, row, content):
        workbook.get_sheet(sheet).write(col, row, content.decode('utf-8').strip())

    def log_to_excel(self, workbook, log_path):
        files = [
            ('charge.txt', 3),
            ('charge_query.txt', 5),
            ('void.txt', 8),
            ('void_query.txt', 10),
            ('refund.txt', 13),
            ('refund_query.txt', 15)
        ]
        for (file, start_line) in files:
            with open(os.path.join(log_path, file)) as f:
                lines = f.readlines()

            if lines == 11:
                req, res, notify, _ = lines
                self._set_cell(workbook, 3, start_line, 3, req)
                self._set_cell(workbook, 3, start_line + 1, 3, res)
                self._set_cell(workbook, 3, start_line + 4, 3, notify)
            elif lines == 7:
                req, res, _ = lines
                self._set_cell(workbook, 3, start_line, 3, req)
                self._set_cell(workbook, 3, start_line + 1, 3, res)


if __name__ == '__main__':
    eh = ExcelHandler()
    eh.save('./test.xlsx', './output.xlsx', '../data/upmp-merchant-files/2014/09/1/log/')
