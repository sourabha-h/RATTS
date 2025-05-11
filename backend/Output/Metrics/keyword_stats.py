from robot.api import ResultVisitor


class KeywordStats(ResultVisitor):
    total_keywords = 0
    passed_keywords = 0
    failed_keywords = 0

    def __init__(self, ignore_library=None, ignore_type=None):
        self.ignore_library = ignore_library or []
        self.ignore_type = ignore_type or []
        self.total_keywords = 0
        self.passed_keywords = 0
        self.failed_keywords = 0
        

    def start_keyword(self, kw):
        # Ignore library keywords
        keyword_library = kw.libname or ""
        keyword_type = kw.type or ""
             # Debug
        print(f"[DEBUG] kw.libname: {kw.libname}, kw.type: {kw.type}")
        print(f"[DEBUG] ignore_library: {self.ignore_library}")
        print(f"[DEBUG] ignore_type: {self.ignore_type}")
        if any(lib in keyword_library for lib in self.ignore_library):
            return
        if any(t in keyword_type for t in self.ignore_type):
            return

       
        self.total_keywords += 1
        if kw.status == "PASS":
            self.passed_keywords += 1
        else:
            self.failed_keywords += 1
