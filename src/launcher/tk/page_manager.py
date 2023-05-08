from launcher.tk.page_frame import PageFrame


class PageManager:
    def __init__(self) -> None:
        self.pages: dict[str, PageFrame] = {}

    def add_page(self, page_frame: PageFrame) -> None:
        self.pages[type(page_frame).__name__] = page_frame

    def get_page(self, page_name: str) -> PageFrame:
        page_frame = self.pages.get(page_name)
        if page_frame is None:
            raise Exception(f'page name: {page_name} is not a valid id')
        return page_frame

    def show_page(self, page_name: str) -> None:
        self.get_page(page_name).tkraise()
