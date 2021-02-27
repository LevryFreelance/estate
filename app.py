from controllers import db

from scripts.ss import main as ss_controller
# from scripts.mm import main as mm_controller
from scripts.latio import main as latio_controller
from scripts.ss_archive import main as archive_controller
from scripts.city24lv import main as city24lv_controller


def refresh_tables():
    print('Refresh')

    try:
        print("ss try")
        ss = ss_controller()
        if ss is not None:
            db.save(ss, 'latvia')
    except Exception as e:
        print("ss except")
        print(e)

    # try:
    #     mm = mm_controller()
    #     if mm is not None:
    #         db.save(mm, 'latvia')
    # except Exception as e:
    #     print(e)

    try:
        print("latio try")
        latio = latio_controller()
        if latio is not None:
            db.save(latio, 'latvia')
    except Exception as e:
        print("latio except")
        print(e)

    try:
        print("city24lv try")
        city24lv = city24lv_controller()
        if city24lv is not None:
            db.save(city24lv, 'latvia')
    except Exception as e:
        print("city24lv except")
        print(e)

    # try:
    #     archive = archive_controller()
    #     if archive is not None:
    #         db.save(archive, 'archive')
    # except Exception as e:
    #     print(e)


    print('Finished refresh')


if __name__ == '__main__':

    while True:
        refresh_tables()
