from buli_parser import BuliParser

if __name__ == '__main__':
    SEASON = "1516"
    BuliParser1A = BuliParser(SEASON, "1", "Gruppe+A", "1A_schedule", "1A_competitions", "1A_table", "1. Bundesliga - Gruppe A", "2")
    BuliParser1B = BuliParser(SEASON, "1", "Gruppe+B", "1B_schedule", "1B_competitions", "1B_table", "1. Bundesliga - Gruppe B", "3")
    BuliParser2South = BuliParser(SEASON, "2", "S%FCdwest", "2South_schedule", "2South_competitions", "2South_table", u"2. Bundesliga - Staffel S\u00fcdwest", "5")
    BuliParser2North = BuliParser(SEASON, "2", "Nordost", "2North_schedule", "2North_competitions", "2North_table", "2. Bundesliga - Staffel Nordost", "6")
    BuliParser2Middle = BuliParser(SEASON, "2", "Mitte", "2Middle_schedule", "2Middle_competitions", "2Middle_table", "2. Bundesliga - Staffel Mitte", "7")

    for parser in [BuliParser1A, BuliParser1B, BuliParser2South, BuliParser2North, BuliParser2Middle]:
        parser.create_buli_files()