# account class


class Account:
    def __init__(self, acct_id, fn, ln, alias, addr, reads_in, master):
        self.acct_id = acct_id
        self.fn = fn
        self.ln = ln
        self.file_alias = alias
        self.addr = addr
        self.reads_in = reads_in
        self.master = master
        self.__previous_reading = -999
        self.__latest_reading = -999
        self.current_usage = -999
        self.current_usage_percent = -999

        self.pge_bill_share = -999
        self.savings_assessment = -999

        self.__prev_balance = -999999999.99
        self.__payments = 99999999.99
        self.__adjustments = 99999999.99
        self.__new_charges = 99999.99
        self.__current_balance = -99999.99

    #
    # def __setattr__(self, name, value):
    #     super().__setattr__(name, value)
    def __str__(self):
        return f"{self.__prev_balance}"

    @property
    def latest_reading(self):
        return self.__latest_reading

    @latest_reading.setter
    def latest_reading(self, value):
        self.__latest_reading = value

    @property
    def previous_reading(self):
        return self.__previous_reading

    @previous_reading.setter
    def previous_reading(self, value):
        self.__previous_reading = value

    @property
    def new_charges(self):
        return self.__new_charges

    @new_charges.setter
    def new_charges(self, value):
        self.__new_charges = value

    @property
    def current_balance(self):
        return self.__current_balance

    @current_balance.setter
    def current_balance(self, value):
        self.__current_balance = value

    @property
    def prev_balance(self):
        return self.__prev_balance

    @prev_balance.setter
    def prev_balance(self, value):
        self.__prev_balance = value

    @property
    def payments(self):
        return self.__payments

    @payments.setter
    def payments(self, value):
        self.__payments = value

    @property
    def adjustments(self):
        return self.__adjustments

    @adjustments.setter
    def adjustments(self, value):
        self.__adjustments = value

    @property
    def latest_reading(self):
        return self.__latest_reading

    @latest_reading.setter
    def latest_reading(self, value):
        self.__latest_reading = value

    @property
    def previous_reading(self):
        return self.__previous_reading

    @previous_reading.setter
    def previous_reading(self, value):
        self.__previous_reading = value

    @property
    def current_usage_in_gallons(self):
        return self.current_usage

    # @prev_balance.setter
    # def prev_balance(self, value):
    #     print(f"called prev_balance.setter")
    #     self.__prev_balance = value

    def calculate_pge_bill_percent(self, pge_bill):
        self.pge_bill_share = round((pge_bill * self.current_usage_percent) / 10000, 2)

    def calculate_current_usage_percent(self, ttl_monthly_usage):
        self.current_usage_percent = round(
            (self.current_usage / ttl_monthly_usage) * 100, 2
        )

    def calculate_current_usage(self):
        self.current_usage = self.latest_reading - self.previous_reading
        if self.reads_in == "cubic feet":
            self.current_usage = self.current_usage * 7.4805
        self.current_usage = round(self.current_usage, 2)
