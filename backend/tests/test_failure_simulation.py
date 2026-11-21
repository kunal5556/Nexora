import pytest

from app.failure_simulation import parse_simulation_header

KEY_IDS = ["key_1", "key_2"]


@pytest.mark.parametrize("header_value", [None, ""])
def test_empty_header_returns_no_failures(header_value):
    assert parse_simulation_header(header_value, KEY_IDS) == {}


def test_single_pair_is_parsed():
    assert parse_simulation_header("key_1=429", KEY_IDS) == {"key_1": 429}


def test_multiple_pairs_are_parsed():
    assert parse_simulation_header("key_1=429,key_2=500", KEY_IDS) == {"key_1": 429, "key_2": 500}


def test_wildcard_applies_to_every_key():
    assert parse_simulation_header("*=503", KEY_IDS) == {"key_1": 503, "key_2": 503}


@pytest.mark.parametrize("header_value", ["*=429,key_2=500", "key_2=500,*=429"])
def test_explicit_key_overrides_wildcard(header_value):
    assert parse_simulation_header(header_value, KEY_IDS) == {"key_1": 429, "key_2": 500}


def test_spaces_are_ignored():
    assert parse_simulation_header(" key_1 = 502 , key_2= 503 ", KEY_IDS) == {"key_1": 502, "key_2": 503}


@pytest.mark.parametrize("header_value", ["key_1=404", "key_1=200", "key_1=abc"])
def test_unsupported_status_is_ignored(header_value):
    assert parse_simulation_header(header_value, KEY_IDS) == {}


def test_unknown_key_is_ignored():
    assert parse_simulation_header("key_9=429", KEY_IDS) == {}


@pytest.mark.parametrize("header_value", ["key_1", "=429", ",,", "key_1==429"])
def test_malformed_parts_are_ignored(header_value):
    assert parse_simulation_header(header_value, KEY_IDS) == {}
