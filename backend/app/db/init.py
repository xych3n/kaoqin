import datetime
import re

import xlrd
from sqlalchemy import select
from tqdm import trange

from ..models import *
from .base import Base
from .session import SessionLocal, engine


def insert_users(filename: str):
    users = []
    book = xlrd.open_workbook(filename)
    sh = book.sheet_by_name("学生信息")
    for i in trange(1, sh.nrows, desc="User"):
        student_number = sh.cell_value(i, 0)
        if not re.match(r"\d{4}(40|79|42|52)", student_number):
            # 40: Ph.D.             79: Direct Ph.D.
            # 42: Academic Master   52: Professional Master
            continue
        name = sh.cell_value(i, 1)
        id_number = sh.cell_value(i, 4)
        if student_number in ["20225227002", "20225227115"]:
            is_superuser = True
        else:
            is_superuser = False
        users.append(User(
            student_number=student_number,
            id_number=id_number,
            name=name,
            is_superuser=is_superuser,
        ))
    with SessionLocal() as db:
        db.add_all(users)
        db.commit()


def insert_particips(filename: str, category: ActivityCategory):
    book = xlrd.open_workbook(filename)
    sh = book.sheet_by_name("记录明细")
    for i in trange(1, sh.nrows, desc=category.value):
        activity_date = datetime.date.fromisoformat(sh.cell_value(i, 3))
        if activity_date < datetime.date(2022, 9, 1):
            continue
        student_number = sh.cell_value(i, 0)
        with SessionLocal() as db:
            db_user = db.scalar(select(User).where(User.student_number == student_number))
        if not db_user:
            continue
        activity_title = sh.cell_value(i, 2)
        involvement = int(sh.cell_value(i, 4))
        with SessionLocal() as db:
            db_activity = db.scalar(
                select(Activity)
                .where((Activity.date == activity_date)
                        & (Activity.title == activity_title))
            )
            if not db_activity:
                db_activity = Activity(
                    title=activity_title,
                    date=activity_date,
                    category=category,
                )
                db.add(db_activity)
                db.commit()
                db.refresh(db_activity)
            db_particip = db.scalar(
                select(Particip)
                .where((Particip.user_id == db_user.id)
                        & (Particip.activity_id == db_activity.id))
            )
            if db_particip:
                db_particip.involvement += involvement
                if db_particip.involvement == 0:
                    db.delete(db_particip)
                    db.commit()
                    continue
            else:
                db_particip = Particip(
                    user_id=db_user.id,
                    activity_id=db_activity.id,
                    involvement=involvement
                )
            db.add(db_particip)
            db.commit()


def involvement_alignment(filename: str, category: ActivityCategory):
    with SessionLocal() as db:
        db_activity = Activity(
            title="旧数据导入（{}）".format(category.value),
            date=datetime.date(2022, 8, 31),
            category=category,
        )
        db.add(db_activity)
        db.commit()
        db.refresh(db_activity)
    book = xlrd.open_workbook(filename)
    sh = book.sheet_by_name("次数统计")
    for i in trange(1, sh.nrows, desc="Alignment"):
        student_number = sh.cell_value(i, 0)
        involvement = int(sh.cell_value(i, 2))
        with SessionLocal() as db:
            db_user = db.scalar(select(User).where(User.student_number == student_number))
            if not db_user or db_user.student_number.startswith("2022"):
                continue
            db_involvement = db_user.involvements[category.value]   # need be bound to a session
        if involvement != db_involvement:
            assert involvement > db_involvement
            db_particip = Particip(
                user_id=db_user.id,
                activity_id=db_activity.id,
                involvement=involvement - db_involvement,
            )
            with SessionLocal() as db:
                db.add(db_particip)
                db.commit()


if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)

    insert_users("学籍信息.xls")
    insert_particips("学术讲座_20230809.xls", ActivityCategory.LECT)
    involvement_alignment("学术讲座_20230809.xls", ActivityCategory.LECT)
    insert_particips("研会活动_20230809.xls", ActivityCategory.ASSN)
    involvement_alignment("研会活动_20230809.xls", ActivityCategory.ASSN)
