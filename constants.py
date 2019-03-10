class Constants:
    def __init__(self):
        self._administrative_fee_paid = 1
        self._administrative_fee_received = 2
        self._payment_received = 3
        self._pge_bill_paid = 4
        self._pge_bill_received = 5
        self._savings_assessment = 6
        self._savings_deposit = 7
        self._savings_disbursement = 8
        self._monthly_reading = 9
        self.__account_adjustment = 10

    @property
    def administrative_fee_paid(self):
        return self._administrative_fee_paid

    @property
    def administrative_fee_received(self):
        return self._administrative_fee_received

    @property
    def payment_received(self):
        return self._payment_received

    @property
    def pge_bill_paid(self):
        return self._pge_bill_paid
