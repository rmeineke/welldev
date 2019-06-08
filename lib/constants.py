class Constants:
    def __init__(self):
        self._account_adjustment = 1
        self._administrative_fee_received = 2
        self._administrative_fee_paid = 3
        self._misc_rebate_received = 4
        self._misc_rebate_disbursed = 5
        self._payment_received = 6
        self._pge_bill_received = 7
        self._pge_bill_paid = 8
        self._pge_bill_share = 9
        self._savings_assessment = 10
        self._savings_deposit_made = 11
        self._savings_disbursement = 12
        self._savings_dividend = 13
        # 2019.06.08
        self._administrative_fee_share = 14

        self._assessment_per_gallon = 0.0025
        self._gallons_per_cubic_foot = 7.4805

    @property
    def gallons_per_cubic_foot(self):
        return self._gallons_per_cubic_foot

    @property
    def account_adjustment(self):
        return self._account_adjustment

    @property
    def administrative_fee_paid(self):
        return self._administrative_fee_paid

    @property
    def administrative_fee_received(self):
        return self._administrative_fee_received

    @property
    def administrative_fee_share(self):
        return self._administrative_fee_share

    @property
    def payment_received(self):
        return self._payment_received

    @property
    def pge_bill_paid(self):
        return self._pge_bill_paid

    @property
    def pge_bill_received(self):
        return self._pge_bill_received

    @property
    def pge_bill_share(self):
        return self._pge_bill_share

    @property
    def savings_assessment(self):
        return self._savings_assessment

    @property
    def savings_deposit_made(self):
        return self._savings_deposit_made

    @property
    def savings_disbursement(self):
        return self._savings_disbursement

    @property
    def savings_dividend(self):
        return self._savings_dividend

    @property
    def assessment_per_gallon(self):
        return self._assessment_per_gallon
