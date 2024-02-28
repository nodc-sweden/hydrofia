

class Colors:

    @property
    def hydrofia_container(self):
        return '#DFE8CC'

    @property
    def result_container(self):
        return '#6ab080'

    @property
    def option_container(self):
        return '#DFF8C9'

    @property
    def metadata(self):
        return '#f0e962'

    @property
    def batch(self):
        return '#03b1fc'

    @staticmethod
    def banner(status='bad'):
        if status == 'good':
            return '#3db847'
        elif status == 'working':
            return '#e9f562'
        return '#f73131'

