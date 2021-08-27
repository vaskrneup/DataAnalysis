from utils.words import get_python_var_syntax


class NepseColumnExtractorMixin:
    @staticmethod
    def get_nepse_column(soup, pre_data=None, post_data=None):
        pre_data = pre_data or []
        post_data = post_data or []

        return pre_data + [get_python_var_syntax(td.text.strip()) for td in soup.select("tr.unique td")] + post_data


class NepseTableDataExtractorMixin:
    @staticmethod
    def get_nepse_row_data(soup, start, end_offset, table_rows_exit_threshold=10, pre_data=None, post_data=None):
        pre_data = pre_data or []
        post_data = post_data or []

        table_rows = soup.select("tr")

        if len(table_rows) <= table_rows_exit_threshold:
            return None

        data = []

        for i in range(start, len(table_rows) - end_offset):
            scraped_data = [td.text.strip() for td in table_rows[i].select("td")]
            data.append(
                [(_pre_data(scraped_data) if callable(_pre_data) else _pre_data) for _pre_data in pre_data] +
                scraped_data +
                [(_post_data(scraped_data) if callable(_post_data) else _post_data) for _post_data in post_data]
            )

        return data
