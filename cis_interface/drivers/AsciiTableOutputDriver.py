from cis_interface.drivers.AsciiFileOutputDriver import AsciiFileOutputDriver
from cis_interface.tools import eval_kwarg


class AsciiTableOutputDriver(AsciiFileOutputDriver):
    r"""Class to handle output of received messages to an ASCII table.

    Args:
        name (str): Name of the output queue to receive messages from.
        args (str or dict): Path to the file that messages should be written to
            or dictionary containing the filepath and other keyword arguments
            to be passed to the created AsciiTable object.
        format_str (str): Format string that should be used to format
            output in the case that the io_mode is 'w' (write). It is not
            required if the io_mode is any other value.
        dtype (str): Numpy structured data type for each row. If not
            provided it is set using format_str. Defaults to None.
        column_names (list, optional): List of column names. Defaults to
            None.
        use_astropy (bool, optional): If True, astropy is used to determine
            a table's format if it is installed. If False, a format string
            must be contained in the table. Defaults to False.
        column (str, optional): String that should be used to separate
            columns. Default set by :class:`AsciiTable`.
        comment (str, optional): String that should be used to identify
            comments. Default set by :class:`AsciiFile`.
        newline (str, optional): String that should be used to identify
            the end of a line. Default set by :class:`AsciiFile`.
        as_array (bool, optional): If True, the table contents are sent all at
            once as an array. Defaults to False.
        \*\*kwargs: Additional keyword arguments are passed to parent class's
            __init__ method.

    Attributes (in additon to parent class's):
        file (:class:`AsciiTable.AsciiTable`): Associated special class for
            ASCII table.
        as_array (bool): If True, the table contents are received all at once
            as an array. Defaults to False.

    """
    def __init__(self, name, args, **kwargs):
        file_keys = ['format_str', 'dtype', 'column_names', 'use_astropy',
                     'column', 'as_array']
        # icomm_kws = kwargs.get('icomm_kws', {})
        ocomm_kws = kwargs.get('ocomm_kws', {})
        ocomm_kws.setdefault('comm', 'AsciiTableComm')
        for k in file_keys:
            if k in kwargs:
                ocomm_kws[k] = kwargs.pop(k)
                if k in ['column_names', 'use_astropy', 'as_array']:
                    ocomm_kws[k] = eval_kwarg(ocomm_kws[k])
        ocomm_kws.setdefault('format_str', 'temp')
        kwargs['ocomm_kws'] = ocomm_kws
        super(AsciiTableOutputDriver, self).__init__(name, args, **kwargs)
        self.debug('(%s)', args)

    def before_loop(self):
        r"""Receive format string and then write it to the file."""
        super(AsciiTableOutputDriver, self).before_loop()
        fmt = self.recv_message()
        if not fmt:
            raise RuntimeError('Did not receive format string')
        with self.lock:
            self.ocomm.file.update_format_str(fmt)
            self.ocomm.file.writeformat()

    def recv_message(self):
        r"""Get a new message to send.

        Returns:
            str, bool: False if no more messages, message otherwise.

        """
        return super(AsciiTableOutputDriver, self).recv_message(nolimit=True)
