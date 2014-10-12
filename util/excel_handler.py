# coding: utf-8
import os

from xlrd import open_workbook
from xlutils.copy import copy


class ExcelHandler:
    def save(self, template_path, target_path, merchant):
        rb = open_workbook(template_path)
        wb = copy(rb)

        self.db_to_excel(wb, merchant)

        wb.save(target_path)

    def db_to_excel(self, workbook, merchant):
        """
        keys = [
                    'charge_req', 'charge_res', 'charge_notify', 'charge_query_req', 'charge_query_res',
                    'void_req', 'void_res', 'void_notify', 'void_query_req', 'void_query_res',
                    'refund_req', 'refund_res', 'refund_notify', 'refund_query_req', 'refund_query_res'
            ]
        :param workbook:
        :param machent:
        :return:
        """
        keys = [
            'charge_req', 'charge_res', 'charge_notify', 'charge_query_req', 'charge_query_res',
            'void_req', 'void_res', 'void_notify', 'void_query_req', 'void_query_res',
            'refund_req', 'refund_res', 'refund_notify', 'refund_query_req', 'refund_query_res'
        ]

        self._set_cell(workbook, 3, 3, 3, merchant['charge_req'])
        self._set_cell(workbook, 3, 4, 3, merchant['charge_res'])
        self._set_cell(workbook, 3, 5, 3, merchant['charge_query_req'])
        self._set_cell(workbook, 3, 6, 3, merchant['charge_query_res'])
        self._set_cell(workbook, 3, 7, 3, merchant['charge_notify'])

        self._set_cell(workbook, 3,  8, 3, merchant['void_req'])
        self._set_cell(workbook, 3,  9, 3, merchant['void_res'])
        self._set_cell(workbook, 3, 10, 3, merchant['void_query_req'])
        self._set_cell(workbook, 3, 11, 3, merchant['void_query_res'])
        self._set_cell(workbook, 3, 12, 3, merchant['void_notify'])

        self._set_cell(workbook, 3, 13, 3, merchant['refund_req'])
        self._set_cell(workbook, 3, 14, 3, merchant['refund_res'])
        self._set_cell(workbook, 3, 15, 3, merchant['refund_query_req'])
        self._set_cell(workbook, 3, 16, 3, merchant['refund_query_res'])
        self._set_cell(workbook, 3, 17, 3, merchant['refund_notify'])

    def _set_cell(self, workbook, sheet, col, row, content):
        workbook.get_sheet(sheet).write(col, row, content.decode('utf-8').strip())

    def log_to_excel(self, workbook, merchant):
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
