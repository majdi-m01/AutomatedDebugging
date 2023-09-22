def assert_equal(a, b):
    # assert that a is equal to b
    assert a == b  # TODO: add the assertion


def assert_not_equal(a, b):
    # assert that a is not equal to b
    assert a != b  # TODO: add the assertion


def assert_true(a):
    # assert that the bool representation of a is True
    # you can get the bool representation by casting a to bool
    assert bool(a)  # TODO: add the assertion


def assert_false(a):
    # assert that the bool representation of a is False
    # you can get the bool representation by casting a to bool.
    assert not bool(a)  # TODO: add the assertion


def assert_is(a, b):
    # assert that a is the same object as b
    assert a is b  # TODO: add the assertion


def assert_is_not(a, b):
    # assert that a is not the same object as b
    assert a is not b  # TODO: add the assertion


def assert_is_none(a):
    # assert that a is None
    assert a is None  # TODO: add the assertion


def assert_is_not_none(a):
    # assert that a is not None
    assert a is not None  # TODO: add the assertion


def assert_is_in(a, b):
    # assert that a is an element of b
    assert a in b  # TODO: add the assertion


def assert_is_not_in(a, b):
    # assert that a is not an element of b
    assert a not in b  # TODO: add the assertion


def assert_is_instance(a, t):
    # assert that a is of type t
    assert isinstance(a, t)  # TODO: add the assertion


def assert_is_not_instance(a, t):
    # assert that a is not of type t
    assert not isinstance(a, t)  # TODO: add the assertion


################################ Tests ################################


def test_triggering_input():
    tests = [
        (assert_equal, (2, 1)),
        (assert_equal, (1, 2)),
        (assert_equal, ("", 'test')),
        (assert_not_equal, (2, 2)),
        (assert_not_equal, ("test", 'test')),
        (assert_true, (None,)),
        (assert_true, ('',)),
        (assert_true, (False,)),
        (assert_false, (True,)),
        (assert_false, (1,)),
        (assert_false, ('test',)),
        (assert_is, (1, 2)),
        (assert_is, ('test', 'test2')),
        (assert_is_not, (None, None)),
        (assert_is_not, ('', '')),
        (assert_is_none, ('test',)),
        (assert_is_none, (1,)),
        (assert_is_not_none, (None,)),
        (assert_is_in, (1, [2, 3])),
        (assert_is_in, ('a', 'test')),
        (assert_is_not_in, (1, [1, 2, 3])),
        (assert_is_not_in, ('e', 'test')),
        (assert_is_instance, (1, str)),
        (assert_is_instance, ('a', float)),
        (assert_is_not_instance, (1, int)),
        (assert_is_not_instance, ('e', str)),
    ]
    for a, args in tests:
        try:
            a(*args)
        except AssertionError:
            pass
        else:
            raise AssertionError('Tests failed')


def test_not_triggering_input():
    tests = [
        (assert_not_equal, (2, 1)),
        (assert_not_equal, (1, 2)),
        (assert_not_equal, ("", 'test')),
        (assert_equal, (2, 2)),
        (assert_equal, ("test", 'test')),
        (assert_false, (None,)),
        (assert_false, ('',)),
        (assert_false, (False,)),
        (assert_true, (True,)),
        (assert_true, (1,)),
        (assert_true, ('test',)),
        (assert_is_not, (1, 2)),
        (assert_is_not, ('test', 'test2')),
        (assert_is, (None, None)),
        (assert_is, ('', '')),
        (assert_is_not_none, ('test',)),
        (assert_is_not_none, (1,)),
        (assert_is_none, (None,)),
        (assert_is_not_in, (1, [2, 3])),
        (assert_is_not_in, ('a', 'test')),
        (assert_is_in, (1, [1, 2, 3])),
        (assert_is_in, ('e', 'test')),
        (assert_is_not_instance, (1, str)),
        (assert_is_not_instance, ('a', float)),
        (assert_is_instance, (1, int)),
        (assert_is_instance, ('e', str)),
    ]
    for a, args in tests:
        a(*args)


if __name__ == '__main__':
    test_triggering_input()
    test_not_triggering_input()
