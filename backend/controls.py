"""Atomic SQLite quota reservations. All costs are integer micro-USD."""
import sqlite3
from contextlib import contextmanager
import uuid
from datetime import datetime, timezone
from pathlib import Path

class BudgetExceeded(Exception):
    pass

class Ledger:
    def __init__(self,path):
        Path(path).parent.mkdir(parents=True,exist_ok=True)
        self.path=str(path)
        with self.connect() as db:
            db.execute('PRAGMA journal_mode=WAL')
            db.execute('CREATE TABLE IF NOT EXISTS reservations (id TEXT PRIMARY KEY, day TEXT NOT NULL, month TEXT NOT NULL, amount INTEGER NOT NULL)')
            db.execute('CREATE INDEX IF NOT EXISTS periods ON reservations(month,day)')
            db.execute('CREATE TABLE IF NOT EXISTS rates (identity TEXT PRIMARY KEY, window INTEGER NOT NULL, count INTEGER NOT NULL)')
    @contextmanager
    def connect(self):
        db=sqlite3.connect(self.path,timeout=3,isolation_level=None)
        try:
            yield db
        finally:
            db.close()
    def reserve(self,amount,daily,monthly,now=None):
        now=now or datetime.now(timezone.utc)
        day=now.strftime('%Y-%m-%d');month=day[:7]
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            d=db.execute('SELECT COALESCE(SUM(amount),0) FROM reservations WHERE day=?',(day,)).fetchone()[0]
            m=db.execute('SELECT COALESCE(SUM(amount),0) FROM reservations WHERE month=?',(month,)).fetchone()[0]
            if amount<=0 or d+amount>daily or m+amount>monthly:
                db.rollback();raise BudgetExceeded()
            token=uuid.uuid4().hex
            db.execute('INSERT INTO reservations VALUES (?,?,?,?)',(token,day,month,amount))
            db.commit()
        # Never refund: includes successes, refusals, timeouts and process crashes.
        return token
    def rate(self,identity,per_client,global_limit,now):
        window=int(now)//60
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            db.execute('DELETE FROM rates WHERE window<>?',(window,))
            keys=[('global',global_limit)]
            if identity is not None:keys.append(('client:'+identity,per_client))
            for key,limit in keys:
                row=db.execute('SELECT count FROM rates WHERE identity=?',(key,)).fetchone()
                if row and row[0]>=limit:db.rollback();return False
            for key,_ in keys:
                db.execute('INSERT INTO rates VALUES (?,?,1) ON CONFLICT(identity) DO UPDATE SET count=count+1',(key,window))
            db.commit();return True
    def ready(self):
        with self.connect() as db:db.execute('SELECT COUNT(*) FROM reservations').fetchone()
