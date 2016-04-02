from . import db


def setup():
    c = db.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS budget_categories (name)')
    db.commit()
