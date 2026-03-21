import os
import tempfile


_TEST_DB_PATH = os.path.join(tempfile.gettempdir(), "erh_security_test_suite.db")
os.environ.setdefault("DATABASE_URL", f"sqlite:///{_TEST_DB_PATH}")
