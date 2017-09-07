"""Module for sending output to a RabbitMQ server."""
from cis_interface.drivers.RMQDriver import RMQDriver
from cis_interface.drivers.IODriver import IODriver


class RMQOutputDriver(RMQDriver, IODriver):
    r"""Driver for sending output to a RabbitMQ server.

    Args:
        name (str): The name of the local message queue that the driver should
            connect to.
        args (str): The name of the RabbitMQ message queue that the driver
            connect to.
        \*\*kwargs: Additional keyword arguments are passed to parent class's
            __init__ method.

    Attributes (in addition to parent class's):
        -

    """
    
    def __init__(self, name, args, **kwargs):
        super(RMQOutputDriver, self).__init__(
            name, suffix="_OUT", queue=args, **kwargs)
        self.debug()

    def printStatus(self):
        r"""Print the driver status."""
        self.debug('::printStatus():')
        super(RMQOutputDriver, self).printStatus()
        msg = '%-30s' % ('RMQOutputDriver(' + self.name + '):')
        with self.lock:
            if self._q_obj is not None:
                msg += '%-30s' % (str(self._q_obj.method.message_count) +
                                  ' in RMQ server queue')
            else:
                msg += '%-30s' % 'queue not found'
        print(msg)

    def start_communication(self):
        r"""Start publishing messages from the local queue."""
        self.debug('::start_communication')
        self.publish_message()
    
    def publish_message(self):
        r"""Continue receiving messages from the local queue and passing them
        to the RabbitMQ server until the queue is closed."""
        with self.lock:
            if self._closing:  # pragma: debug
                return
        while True:
            self.debug("::publish_message(): IPC recv")
            data = self.ipc_recv()
            if data is None:
                self.debug("::publish_message(): queue closed!")
                break
            elif len(data) == 0:
                self.debug("::publish_message(): no data, reschedule")
                self.connection.add_timeout(self.sleeptime,
                                            self.publish_message)
                break
            self.debug("::publish_message(): IPC recv got %d bytes", len(data))
            self.debug("::publish_message(): send %d bytes to AMQP", len(data))
            with self.lock:
                if self._closing:  # pragma: debug
                    return
                self.channel.basic_publish(
                    exchange=self.exchange, routing_key=self.queue,
                    body=data, mandatory=True)
            self.debug("::publish_message(): sent to AMQP")
        self.debug("::publish_message returns")

    def stop_communication(self, **kwargs):
        r"""Stop sending/receiving messages. Only RMQInputDriver should
        explicitly delete the queue."""
        with self.lock:
            self._closing = True
            if self.channel and self.channel.is_open:
                # self.channel.queue_unbind(queue=self.queue,
                #                           exchange=self.exchange)
                # self.channel.queue_delete(queue=self.queue)
                self.channel.close()

    # def on_model_exit(self):
    #     r"""Delete the driver. Deleting the queue and closing the connection."""
    #     # self.info(".delete()")
    #     self.debug(".delete()")
    #     try:
    #         pass
    #         # self.channel.queue_unbind(exchange=self.exchange, queue=self.queue)
    #         # self.channel.queue_delete(queue=self.queue, if_unused=True)
    #         # self.connection.close()
    #     except:
    #         self.debug(".delete(): exception (IGNORED)")
    #     self.debug(".delete() returns")
