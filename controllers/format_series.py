INPUT_VALUES = ['103', '103.', '104', '104.', '119', '119.', '467', '467.', '602', '602.', 'Čehu', 'Čehu pr', 'Hrušč', 'Hruščova laika', 'Jaun', 'Jaunceltne', 'Lietuviešu', 'LT proj', 'M. ģim', 'Mazģimeņu', 'P. kara', 'Pirmskara', 'Priv. m', 'Rekonstruēts', 'Renov', 'Specpr', 'Specprojekts', 'Staļina', 'Staļina laika', 'Hruščova', 'Jaunais']
OUTPUT_VALUES = ['103', '103', '104', '104', '119', '119', '467', '467', '602', '602', 'Čehu pr', 'Čehu pr', 'Hruščova laika', 'Hruščova laika', 'Jaun', 'Jaun', 'Lietuviešu', 'Lietuviešu', 'Mazģimeņu', 'Mazģimeņu', 'Pirmskara', 'Pirmskara', 'Priv. m', 'Rekonstruēts', 'Rekonstruēts', 'Specprojekts', 'Specprojekts', 'Staļina laika', 'Staļina laika', 'Hruščova laika', 'Jaun']


def format_series(input):
    if input in INPUT_VALUES:
        return OUTPUT_VALUES[INPUT_VALUES.index(input)]
    else:
        return input
