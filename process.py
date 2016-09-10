import time
import traceback
from parser.buli_parser import BuliParser
from parser.news_parser import BVDGParser, SpeyerParser, SchwedtParser
from utils import update_repo, update_readme, commit_changes, send_to_slack, get_endpoint, is_production

if __name__ == '__main__':
    print "Endpoint: " + get_endpoint()

    SEASON = "1617"
    BuliParser1A = BuliParser(SEASON, "1", "Gruppe+A", "1. Bundesliga - Staffel A", "4")#, leage_relay="1a")
    BuliParser1B = BuliParser(SEASON, "1", "Gruppe+B", "1. Bundesliga - Staffel B", "5")#, leage_relay="1b")
    BuliParser2A = BuliParser(SEASON, "2", "Gruppe+A", "2. Bundesliga - Staffel A", "7")#, leage_relay="2a")
    BuliParser2B = BuliParser(SEASON, "2", "Gruppe+B", "2. Bundesliga - Staffel B", "8")#, leage_relay="2b")
    BuliParser2C = BuliParser(SEASON, "2", "Gruppe+C", "2. Bundesliga - Staffel C", "9")#, leage_relay="2c")

    blog_parsers_instances = [BVDGParser(), SpeyerParser(), SchwedtParser()]
    while True:
        try:
            if is_production():
                update_repo()

            for parser in [BuliParser1A, BuliParser1B, BuliParser2A, BuliParser2B, BuliParser2C]:
                parser.update_buli()

            for blog_parser_instance in blog_parsers_instances:
                blog_parser_instance.parse_articles()

            update_readme(blog_parsers_instances)
            if is_production():
                commit_changes()
            time.sleep(60 * 60)
        except:
            text = "An error occured:" + traceback.format_exc()
            print text
            send_to_slack(text)
            time.sleep(60 * 30)
