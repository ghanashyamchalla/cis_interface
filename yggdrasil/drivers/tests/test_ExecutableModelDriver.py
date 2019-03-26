import unittest
from yggdrasil import platform
from yggdrasil.tests import assert_raises
from yggdrasil.drivers.ExecutableModelDriver import ExecutableModelDriver
import yggdrasil.drivers.tests.test_ModelDriver as parent


def test_error_valgrind_strace():
    r"""Test error if both valgrind and strace set."""
    assert_raises(RuntimeError, ExecutableModelDriver, 'test', 'test',
                  with_strace=True, with_valgrind=True)


@unittest.skipIf(not platform._is_win, "Platform is not windows")
def test_error_valgrind_strace_windows():  # pragma: windows
    r"""Test error if strace or valgrind called on windows."""
    assert_raises(RuntimeError, ExecutableModelDriver, 'test', 'test',
                  with_strace=True)
    assert_raises(RuntimeError, ExecutableModelDriver, 'test', 'test',
                  with_valgrind=True)

    
class TestExecutableModelParam(parent.TestModelParam):
    r"""Test parameters for ExecutableModelDriver class."""

    driver = 'ExecutableModelDriver'

            
class TestExecutableModelDriverNoStart(TestExecutableModelParam,
                                       parent.TestModelDriverNoStart):
    r"""Test runner for ExecutableModelDriver class without start."""
    pass


class TestExecutableModelDriver(TestExecutableModelParam,
                                parent.TestModelDriver):
    r"""Test runner for ExecutableModelDriver class."""
    pass
                           

@unittest.skipIf(platform._is_win, "Platform is windows")
class TestExecutableModelDriver_valgrind(TestExecutableModelDriver):
    r"""Test with valgrind."""

    @property
    def inst_kwargs(self):
        r"""dict: Keyword arguments for creating a class instance."""
        out = super(TestExecutableModelDriver_valgrind, self).inst_kwargs
        out['with_valgrind'] = True
        return out


@unittest.skipIf(platform._is_win, "Platform is windows")
class TestExecutableModelDriver_strace(TestExecutableModelDriver):
    r"""Test with strace."""

    @property
    def inst_kwargs(self):
        r"""dict: Keyword arguments for creating a class instance."""
        out = super(TestExecutableModelDriver_strace, self).inst_kwargs
        out['with_strace'] = True
        return out
