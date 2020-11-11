from scraping.gktoday_quiz import quiz_run
from scraping.gktoday_magazine import magazine_run
from scraping.app_md import init_app_metadata


try:
    quiz_run()
except TypeError:
    try:
        quiz_run(True)
    # temporary: if quiz fails, magazine would still function correctly
    except Exception:
        pass
magazine_run()
init_app_metadata()
