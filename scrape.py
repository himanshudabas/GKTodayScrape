from scraping.gktoday_quiz import quiz_run
from scraping.gktoday_magazine import magazine_run
from scraping.app_md import init_app_metadata

try:
    quiz_run()
except TypeError:
    quiz_run(True)
magazine_run()
init_app_metadata()
