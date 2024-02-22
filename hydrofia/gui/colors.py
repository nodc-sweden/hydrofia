

class Colors:

    @property
    def template_path(self):
        return '#DFE8CC'

    @property
    def hydrofia_file_path(self):
        return self.template_path

    @property
    def ctd_directory(self):
        return self.template_path

    @property
    def export_template(self):
        return '#6ec3d4'

    @property
    def export_result(self):
        return '#6ed490'

    @property
    def metadata(self):
        return '#f0e962'

    @staticmethod
    def banner(status='bad'):
        if status == 'good':
            return '#3db847'
        elif status == 'working':
            return '#e9f562'
        return '#f73131'

