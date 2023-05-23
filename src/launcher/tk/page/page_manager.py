from launcher.tk.page.page_frame import PageFrame


class PageManager:
    def __init__(self) -> None:
        self.pages: dict[str, PageFrame] = {}
        self.current_page: PageFrame | None = None

    def add_page(self, page_frame: PageFrame) -> None:
        self.pages[type(page_frame).__name__] = page_frame

    def get_page(self, page_name: str) -> PageFrame:
        page_frame = self.pages.get(page_name)
        if page_frame is None:
            raise Exception(f'page name: {page_name} is not a valid id')
        return page_frame

    def set_current_page(self, page: PageFrame) -> None:
        self.current_page = page

    def show_page(self, page_name: str) -> None:
        if self.current_page is not None:
            self.current_page.pack_forget()

        page: PageFrame = self.get_page(page_name)
        self.set_current_page(page)
        page.pack(fill="both", expand=True)
