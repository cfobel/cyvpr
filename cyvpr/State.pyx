cdef class cStateBase:
    def __str__(self):
        return self.baseptr.str()

    def csv_summary(self):
        return self.baseptr.csv_summary()

    def csv_header(self):
        return self.baseptr.csv_header()

    def csv(self):
        return self.baseptr.csv()

    property label:
        def __get__(self):
            return self.baseptr.label()

    property csv_fieldnames:
        def __get__(self):
            return self.baseptr.csv_fieldnames()
