# account class


class Account:
    def __init__(self, acct_id, fn, ln, addr, reads_in, master):
        self.acct_id = acct_id
        self.fn = fn
        self.ln = ln
        self.addr = addr
        self.reads_in = reads_in
        self.master = master
        self.previous_reading = -999
        self.latest_reading = -999
        self.current_usage = -999
        self.current_usage_percent = -999
        self.ttl_usage = -999

        self.pge_bill_share = -999
        self.savings_assessment = -999

    def calculate_current_usage(self):
        self.current_usage = self.latest_reading - self.previous_reading
        if self.reads_in == 'cubic feet':
            self.current_usage *= 7.48052
            self.current_usage = round(self.current_usage, 2)
        self.current_usage = round(self.current_usage, 2)

    def __setattr__(self, name, value):
        super().__setattr__(name, value)
