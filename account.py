# account class


class Account:
    def __init__(self, acct_id, fn, ln, addr, reads_in, master):
        self.acct_id = acct_id
        self.fn = fn
        self.ln = ln
        self.addr = addr
        self.reads_in = reads_in
        self.master = master
        self.__previous_reading = -999
        self.__latest_reading = -999
        self.current_usage = -999
        self.current_usage_percent = -999
        self.ttl_usage = -999

        self.pge_bill_share = -999
        self.savings_assessment = -999

    #
    # def __setattr__(self, name, value):
    #     super().__setattr__(name, value)

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

    def calculate_current_usage(self):
        self.current_usage = self.latest_reading - self.previous_reading
        if self.reads_in == 'cubic feet':
            self.current_usage = self.current_usage * 7.4805
            # print(f"current_usage: {self.current_usage}")
            # self.current_usage = round(self.current_usage, 2)
            # print(f"current_usage, rounded: {self.current_usage}")
        self.current_usage = round(self.current_usage, 2)
