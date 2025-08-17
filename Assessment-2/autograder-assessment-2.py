"""
Autograder for Context Managers, Decorators, and DB Guardrails
----------------------------------------------------------------
Contract: The student's submission must be importable as a module (default name: `submission`),
exposing—at minimum—the following callables/types:

1) class FileOpenerCM(path, mode)
2) function file_opener_cm(path, mode)  # contextlib.contextmanager version
3) class TempEnviron(var, value)  # sets/restores an env var
4) class Locked(lock, timeout=None)  # acquires/releases a threading.Lock
5) class Timer()  # context manager with .elapsed (float seconds)
6) decorator timer(func=None, *, logger=None, level=None)  # preserves metadata via functools.wraps
7) decorator catch_and_log(func=None, *, logger=None, reraise=True)
8) function run_query(db_path, sql, params=None) -> rows (list[tuple]) using safe binding
9) decorator autocommit_sqlite(func)  # expects decorated fn signature: (conn, *args, **kwargs)
10) decorator retry_on_operational_error(retries=3, backoff=0.01, jitter=False)
11) decorator db_guardrail(func=None, *, logger=None, retries=2, backoff=0.01)  # composed: timing+retry+logging

This autograder runs a focused test battery (100 points). It is intentionally pragmatic and opinionated.
Run: `python autograder.py [optional_module_name]`

Outputs a human-readable summary and a JSON blob for programmatic capture.
"""

from __future__ import annotations

import importlib
import importlib.util
import io
import json
import logging
import os
import sqlite3
import sys
import tempfile
import threading
import time
import types
import unittest
from contextlib import redirect_stdout

# ---------------------
# Utility: import target
# ---------------------

def import_submission(module_name: str | None = None) -> types.ModuleType:
    if module_name:
        return importlib.import_module(module_name)
    # Default to `submission`
    try:
        return importlib.import_module("submission")
    except Exception as e:
        raise ImportError(
            "Could not import module 'submission'. Pass an explicit module name as CLI arg, or provide submission.py."
        ) from e


# ---------------------
# Utility: log capture
# ---------------------
class LogCapture:
    def __init__(self, name: str = "autograder.capture", level=logging.DEBUG):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        self.stream = io.StringIO()
        self.handler = logging.StreamHandler(self.stream)
        self.handler.setLevel(level)
        # Compact format
        self.handler.setFormatter(logging.Formatter("%(levelname)s %(message)s"))
        # Avoid duplicate handlers if reused
        for h in list(self.logger.handlers):
            self.logger.removeHandler(h)
        self.logger.addHandler(self.handler)

    def flush_text(self) -> str:
        self.handler.flush()
        return self.stream.getvalue()


# ---------------------
# Shared temp sqlite DB
# ---------------------
class TempSQLite:
    def __init__(self):
        self._td = tempfile.TemporaryDirectory()
        self.path = os.path.join(self._td.name, "db.sqlite3")
        self.conn = sqlite3.connect(self.path)

    def setup_basic_schema(self):
        cur = self.conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, name TEXT)")
        self.conn.commit()

    def close(self):
        try:
            self.conn.close()
        finally:
            self._td.cleanup()


# ---------------------
# Test Suite
# ---------------------
class CMDecoratorGrader(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        mod_name = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1].endswith(".py") is False and sys.argv[1] != "-k" else None
        # Heuristic: if first arg looks like module name (no .py), use it
        if len(sys.argv) > 1 and mod_name is None and sys.argv[1] not in ("-q", "-v"):
            mod_name = sys.argv[1]
        cls.SUB = import_submission(mod_name)

    # 1. FileOpenerCM
    def test_01_file_opener_cm_class(self):
        SUB = self.SUB
        self.assertTrue(hasattr(SUB, "FileOpenerCM"), "Missing FileOpenerCM class")
        with tempfile.NamedTemporaryFile(delete=False) as tf:
            tmp = tf.name
        try:
            # write
            with SUB.FileOpenerCM(tmp, "w") as f:
                f.write("hello")
            # ensure closed
            self.assertTrue(f.closed, "File handle should be closed after context exit")
            # read
            with open(tmp, "r") as r:
                self.assertEqual(r.read(), "hello")
        finally:
            try:
                os.remove(tmp)
            except FileNotFoundError:
                pass

    # 2. file_opener_cm (generator)
    def test_02_file_opener_cm_generator(self):
        SUB = self.SUB
        self.assertTrue(hasattr(SUB, "file_opener_cm"), "Missing file_opener_cm function")
        with tempfile.NamedTemporaryFile(delete=False) as tf:
            tmp = tf.name
        try:
            with SUB.file_opener_cm(tmp, "w") as f:
                f.write("hi")
            with open(tmp) as r:
                self.assertEqual(r.read(), "hi")
        finally:
            try:
                os.remove(tmp)
            except FileNotFoundError:
                pass

    # 3. TempEnviron
    def test_03_temp_environ(self):
        SUB = self.SUB
        self.assertTrue(hasattr(SUB, "TempEnviron"), "Missing TempEnviron class")
        key = "AUTOGRADER_TEST_ENV"
        prev = os.environ.get(key)
        try:
            with SUB.TempEnviron(key, "XYZ"):
                self.assertEqual(os.environ.get(key), "XYZ")
            self.assertEqual(os.environ.get(key), prev)
        finally:
            # restore to original
            if prev is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = prev

    # 4. Locked
    def test_04_locked(self):
        SUB = self.SUB
        self.assertTrue(hasattr(SUB, "Locked"), "Missing Locked class")
        lock = threading.Lock()
        with SUB.Locked(lock):
            self.assertTrue(lock.locked(), "Lock should be acquired inside context")
        self.assertTrue(lock.acquire(blocking=False), "Lock should be released after context exit")
        lock.release()

    # 5. Timer context manager
    def test_05_timer_cm(self):
        SUB = self.SUB
        self.assertTrue(hasattr(SUB, "Timer"), "Missing Timer class")
        with SUB.Timer() as t:
            time.sleep(0.01)
        self.assertTrue(hasattr(t, "elapsed"))
        self.assertGreater(t.elapsed, 0.0)

    # 6. timer decorator metadata + output
    def test_06_timer_decorator(self):
        SUB = self.SUB
        self.assertTrue(hasattr(SUB, "timer"), "Missing timer decorator")

        @SUB.timer
        def sample(x, y):
            s = 0
            for _ in range(1000):
                s += x + y
            return s

        self.assertEqual(sample.__name__, "sample", "functools.wraps likely missing; name was not preserved")
        out = io.StringIO()
        with redirect_stdout(out):
            res = sample(2, 3)
        self.assertEqual(res, 5000)
        msg = out.getvalue()
        self.assertTrue("elapsed" in msg.lower() or "ms" in msg.lower() or "sec" in msg.lower(), "Timer should emit timing info to stdout or logs")

    # 7. catch_and_log decorator: logs and re-raises
    def test_07_catch_and_log(self):
        SUB = self.SUB
        self.assertTrue(hasattr(SUB, "catch_and_log"), "Missing catch_and_log decorator")
        cap = LogCapture()

        @SUB.catch_and_log(logger=cap.logger, reraise=True)
        def boom():
            raise ValueError("kaboom")

        with self.assertRaises(ValueError):
            boom()
        logs = cap.flush_text()
        self.assertIn("kaboom", logs)
        self.assertTrue("ValueError" in logs or "exception" in logs.lower())

    # 8. run_query safe binding + results
    def test_08_run_query(self):
        SUB = self.SUB
        self.assertTrue(hasattr(SUB, "run_query"), "Missing run_query function")
        db = TempSQLite()
        try:
            db.setup_basic_schema()
            db.conn.execute("INSERT INTO users(name) VALUES (?)", ("alice",))
            db.conn.execute("INSERT INTO users(name) VALUES (?)", ("bob",))
            db.conn.commit()
            rows = SUB.run_query(db.path, "SELECT name FROM users WHERE name = ?", params=("alice",))
            self.assertEqual(rows, [("alice",)])
        finally:
            db.close()

    # 9. autocommit_sqlite commit/rollback
    def test_09_autocommit_sqlite(self):
        SUB = self.SUB
        self.assertTrue(hasattr(SUB, "autocommit_sqlite"), "Missing autocommit_sqlite decorator")
        db = TempSQLite()
        try:
            db.setup_basic_schema()

            @SUB.autocommit_sqlite
            def add_user(conn, name):
                conn.execute("INSERT INTO users(name) VALUES (?)", (name,))
                return True

            ok = add_user(db.conn, "carol")
            self.assertTrue(ok)
            rows = list(db.conn.execute("SELECT name FROM users WHERE name='carol'"))
            self.assertEqual(len(rows), 1)

            @SUB.autocommit_sqlite
            def add_user_then_fail(conn, name):
                conn.execute("INSERT INTO users(name) VALUES (?)", (name,))
                raise RuntimeError("fail after insert")

            with self.assertRaises(RuntimeError):
                add_user_then_fail(db.conn, "dave")
            # Should be rolled back
            rows = list(db.conn.execute("SELECT name FROM users WHERE name='dave'"))
            self.assertEqual(len(rows), 0, "Insert must be rolled back on exception")
        finally:
            db.close()

    # 10. retry_on_operational_error
    def test_10_retry_on_operational_error(self):
        SUB = self.SUB
        self.assertTrue(hasattr(SUB, "retry_on_operational_error"), "Missing retry_on_operational_error decorator")
        attempts = {"n": 0}

        @SUB.retry_on_operational_error(retries=3, backoff=0.001)
        def flaky():
            attempts["n"] += 1
            if attempts["n"] < 3:
                raise sqlite3.OperationalError("database is locked")
            return 42

        self.assertEqual(flaky(), 42)
        self.assertEqual(attempts["n"], 3)

    # 11. db_guardrail composition + logging
    def test_11_db_guardrail(self):
        SUB = self.SUB
        self.assertTrue(hasattr(SUB, "db_guardrail"), "Missing db_guardrail decorator")
        cap = LogCapture()
        calls = {"n": 0}

        @SUB.db_guardrail(logger=cap.logger, retries=2, backoff=0.001)
        def sometimes_ok():
            calls["n"] += 1
            if calls["n"] == 1:
                raise sqlite3.OperationalError("locked")
            return "ok"

        out = sometimes_ok()
        self.assertEqual(out, "ok")
        logs = cap.flush_text().lower()
        # We accept either structured or unstructured timing hints
        self.assertTrue("elapsed" in logs or "ms" in logs or "sec" in logs or "retry" in logs,
                        "db_guardrail should emit timing/retry/logging signals")
        self.assertEqual(sometimes_ok.__name__, "sometimes_ok", "Must preserve metadata with functools.wraps")


# ---------------------
# Runner + Scoring
# ---------------------
class ScoringTestResult(unittest.TextTestResult):
    # Each test worth equal points (100 / N)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.details = []

    def addSuccess(self, test):
        super().addSuccess(test)
        self.details.append({"test": test.id(), "status": "passed", "message": ""})

    def addFailure(self, test, err):
        super().addFailure(test, err)
        msg = self._exc_info_to_string(err, test)
        self.details.append({"test": test.id(), "status": "failed", "message": msg})

    def addError(self, test, err):
        super().addError(test, err)
        msg = self._exc_info_to_string(err, test)
        self.details.append({"test": test.id(), "status": "error", "message": msg})


class ScoringTestRunner(unittest.TextTestRunner):
    resultclass = ScoringTestResult


def main():
    # Build suite explicitly to control ordering/weighting if needed later
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(CMDecoratorGrader)

    runner = ScoringTestRunner(verbosity=2)
    result: ScoringTestResult = runner.run(suite)

    total_tests = result.testsRun
    failed = len(result.failures)
    errored = len(result.errors)
    passed = total_tests - failed - errored

    # Points per test
    per_test = 100.0 / total_tests if total_tests else 0.0
    score = max(0.0, min(100.0, round(passed * per_test, 2)))

    summary = {
        "score": score,
        "max_score": 100.0,
        "tests": total_tests,
        "passed": passed,
        "failed": failed,
        "errored": errored,
        "details": result.details,
    }

    print("\n===== AUTOGRADER SUMMARY =====")
    print(f"Score: {score}/100  (Passed: {passed}, Failed: {failed}, Errors: {errored})")
    print("JSON:")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
