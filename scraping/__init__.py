from scraping.gk_utility import docxToPDF
from scraping.gk_utility import gk_utils

QUIZ_LOG_PATH = '~/gktoday/log/quiz/'
quiz_folder = "~/gktoday/quiz/"
docx_folder = "docx/"
pdf_folder = "pdf/"
product_url = "https://www.gktoday.in/wp-json/wp/v2/product/{product_id}"
main_page_url = "https://www.gktoday.in/page/{page_no}/?orderby=date&post_type=product"
main_page_json = "https://www.gktoday.in/wp-json/wp/v2/product?per_page=10&page={page_no}"
quiz_data_url = "https://www.gktoday.in/wp-content/plugins/wp-quiz-basic/ajax_requests.php"

monthly_folder = "monthly/"
fortnight_folder = "fortnight/"
upsc_prelims_folder = "upsc_prelims/"
month_map = {
    'January': "1",
    "February": "2",
    "March": "3",
    "April": "4",
    "May": "5",
    "June": "6",
    "July": "7",
    "August": "8",
    "September": "9",
    "October": "10",
    "November": "11",
    "December": "12"
}

# magazine data
main_page = "https://currentaffairs.gktoday.in/month/current-affairs-{url_month}-{url_year}"
MAGAZINE_LOG_PATH = '~/gktoday/log/magazine/'
magazine_folder = "~/gktoday/magazine/"

app_folder = "~/gktoday/telebot/"
APP_LOG_PATH = '~/gktoday/log/app/'
__all__ = ['APP_LOG_PATH', 'docxToPDF', 'gk_utils', 'QUIZ_LOG_PATH', 'docx_folder', 'pdf_folder', 'product_url', 'main_page_json',
           'main_page_url', 'quiz_data_url', 'quiz_folder', 'monthly_folder', 'fortnight_folder', 'upsc_prelims_folder',
           'month_map', 'main_page', 'MAGAZINE_LOG_PATH', 'magazine_folder', 'app_folder']
