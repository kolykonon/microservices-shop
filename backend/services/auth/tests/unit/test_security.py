import pwdlib
import pytest

from app.domain.utils.security import hash_password, verify_password

test_pwd = "TEST_PASSWORD"


def test_hash_password_is_not_plain():
    assert hash_password(test_pwd) != test_pwd


def test_correct_password_is_verified():
    hashed = hash_password(test_pwd)
    assert verify_password(test_pwd, hashed) == True


def test_incorrect_password_is_not_verified():
    hashed = hash_password("IncorrectPassword")
    assert verify_password(test_pwd, hashed) == False


def test_same_password_gives_diff_hashes():
    assert hash_password(test_pwd) != hash_password(test_pwd)
