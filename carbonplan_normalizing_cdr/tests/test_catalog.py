import os

from carbonplan_normalizing_cdr import cat_file

def test_catalog_exists():
    assert os.path.exists(cat_file)
