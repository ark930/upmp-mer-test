# coding=utf-8

import sqlite3


class Sqlite:
    table_name = 'upmp-test.db'

    def __init__(self):
        self.conn = sqlite3.connect(self.table_name, check_same_thread=False)
        self.c = self.conn.cursor()
        if not self.is_table_exist():
            self.create_table()

    def close(self):
        self.conn.close()

    def create_table(self):
        self.c.execute('''CREATE TABLE upmp
             (name TEXT, merid TEXT UNIQUE , merkey TEXT,
              charge_req TEXT, charge_res TEXT, charge_notify TEXT, charge_query_req TEXT, charge_query_res TEXT,
              void_req TEXT, void_res TEXT, void_notify TEXT, void_query_req TEXT, void_query_res TEXT,
              refund_req TEXT, refund_res TEXT, refund_notify TEXT, refund_query_req TEXT, refund_query_res TEXT
              )
              ''')

    def drop_table(self):
        self.c.execute("DROP TABLE upmp")

    def is_table_exist(self):
        self.c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='upmp';")
        if self.c.fetchone():
            return True

        return False

    def set_upmp_basic_info(self, name, merid, merkey):
        self.c.execute("INSERT INTO upmp (name, merid, merkey) VALUES (?, ?, ?)", (name, merid, merkey))
        self.conn.commit()

    def set_upmp_charge_data(self, merid, charge_req, charge_res):
        self.c.execute("UPDATE upmp SET charge_req=?, charge_res=? WHERE merid=?", (charge_req, charge_res, merid))
        self.conn.commit()

    def set_upmp_charge_notify_data(self, merid, charge_notify):
        self.c.execute("UPDATE upmp SET charge_notify=? WHERE merid=?", (charge_notify, merid))
        self.conn.commit()

    def set_upmp_charge_query_data(self, merid, charge_query_req, charge_query_res):
        self.c.execute("UPDATE upmp SET charge_query_req=?, charge_query_res=? WHERE merid=?",
                       (charge_query_req, charge_query_res, merid))
        self.conn.commit()

    def set_upmp_void_data(self, merid, void_req, void_res):
        self.c.execute("UPDATE upmp SET void_req=?, void_res=? WHERE merid=?", (void_req, void_res, merid))
        self.conn.commit()

    def set_upmp_void_notify_data(self, merid, void_notify):
        self.c.execute("UPDATE upmp SET void_notify=? WHERE merid=?", (void_notify, merid))
        self.conn.commit()

    def set_upmp_void_query_data(self, merid, void_query_req, void_query_res):
        self.c.execute("UPDATE upmp SET void_query_req=?, void_query_res=? WHERE merid=?",
                       (void_query_req, void_query_res, merid))
        self.conn.commit()

    def set_upmp_refund_data(self, merid, refund_req, refund_res):
        self.c.execute("UPDATE upmp SET refund_req=?, refund_res=? WHERE merid=?", (refund_req, refund_res, merid))
        self.conn.commit()

    def set_upmp_refund_notify_data(self, merid, refund_notify):
        self.c.execute("UPDATE upmp SET refund_notify=? WHERE merid=?", (refund_notify, merid))
        self.conn.commit()

    def set_upmp_refund_query_data(self, merid, refund_query_req, refund_query_res):
        self.c.execute("UPDATE upmp SET refund_query_req=?, refund_query_res=? WHERE merid=?",
                       (refund_query_req, refund_query_res, merid))
        self.conn.commit()

    def get_upmp_data_by_merid(self, merid):
        self.c.execute("SELECT * FROM upmp WHERE merid=?", (merid,))
        values = self.c.fetchone()
        if values:
            keys = ['name', 'id', 'sk',
                    'charge_req', 'charge_res', 'charge_notify', 'charge_query_req', 'charge_query_res',
                    'void_req', 'void_res', 'void_notify', 'void_query_req', 'void_query_res',
                    'refund_req', 'refund_res', 'refund_notify', 'refund_query_req', 'refund_query_res'
            ]
            return dict(zip(keys, values))

        return None

    def is_upmp_data_complete(self, merid):
        merchant = self.get_upmp_data_by_merid(merid)
        if None in merchant.values():
            return False

        return True


if __name__ == '__main__':
    s = Sqlite()
    s.drop_table()
    s.__init__()

    s.set_upmp_basic_info('app', '123', 'key2323443')
    s.set_upmp_charge_notify_data('123', 'notify123123')
    data = s.get_upmp_data_by_merid('123')
    s.close()

    print len(data)

    print data