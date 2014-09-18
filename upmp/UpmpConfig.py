class UpmpConfig:
    VERTION = '1.0.0'
    CHARSET = 'UTF-8'
    SIGN_METHOD = 'MD5'
    CURRENCY_TYPE = '156'

    TRANS_TYPE_TRADE = "01"
    TRANS_TYPE_VOID = "31"
    TRANS_TYPE_REFUND = "04"

    QUERY_URL = 'http://202.101.25.178:8080/gateway/merchant/query'
    TRADE_URL = 'http://202.101.25.178:8080/gateway/merchant/trade'
    NOTIFY_URL = 'http://121.199.36.178:8085/api/v1/notify'

    sale_type_file = {
        TRANS_TYPE_TRADE: 'charge.txt',
        TRANS_TYPE_VOID: 'void.txt',
        TRANS_TYPE_REFUND: 'refund.txt'
    }

    query_type_file = {
        TRANS_TYPE_TRADE: 'charge_query.txt',
        TRANS_TYPE_VOID: 'void_query.txt',
        TRANS_TYPE_REFUND: 'refund_query.txt'
    }