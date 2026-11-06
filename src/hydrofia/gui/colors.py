class Colors:
    hydrofia_container = "#DFE8CC"
    result_container = "#DFF8C9"
    metadata = "#f0e962"
    batch = "#03b1fc"
    path_text = "#303030"
    path_folder = "#505050"

    @staticmethod
    def banner(status="bad"):
        if status == "good":
            return "#3db847"
        elif status == "working":
            return "#e9f562"
        return "#f73131"
