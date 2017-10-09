import nose.tools as nt
from cis_interface.communication.tests import test_CommBase as parent


class TestFileComm(parent.TestCommBase):
    r"""Test for FileComm communication class."""
    def __init__(self, *args, **kwargs):
        super(TestFileComm, self).__init__(*args, **kwargs)
        self.comm = 'FileComm'
        self.attr_list += ['fd', 'read_meth', 'append']

    def teardown(self):
        r"""Remove the file."""
        super(TestFileComm, self).teardown()
        self.send_instance.remove_file()

    def test_eof(self):
        r"""Test send/recv of EOF message."""
        flag = self.send_instance.send(self.send_instance.eof_msg)
        assert(not flag)
        assert(self.send_instance.is_closed)
        flag, msg_recv = self.recv_instance.recv()
        assert(not flag)
        nt.assert_equal(msg_recv, self.send_instance.eof_msg)
        assert(self.recv_instance.is_closed)

    def test_eof_nolimit(self):
        r"""Test send/recv of EOF message through nolimit."""
        flag = self.send_instance.send_nolimit(self.send_instance.eof_msg)
        assert(not flag)
        assert(self.send_instance.is_closed)
        flag, msg_recv = self.recv_instance.recv_nolimit()
        assert(not flag)
        nt.assert_equal(msg_recv, self.send_instance.eof_msg)
        assert(self.recv_instance.is_closed)
