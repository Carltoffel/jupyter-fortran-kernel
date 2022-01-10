from queue import Queue
from threading import Thread
import subprocess


class RealTimeSubprocess(subprocess.Popen):
    """
    A subprocess that allows to read its stdout and stderr in real time
    """

    def __init__(self, cmd, write_to_stdout, write_to_stderr):
        """
        :param cmd: the command to execute
        :param write_to_stdout: a callable that will be called with chunks of data from stdout
        :param write_to_stderr: a callable that will be called with chunks of data from stderr
        """
        self._write_to_stdout = write_to_stdout
        self._write_to_stderr = write_to_stderr

        super().__init__(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=0)

        self._stdout_queue = Queue()
        self._stdout_thread = Thread(target=RealTimeSubprocess._enqueue_output, args=(self.stdout, self._stdout_queue))
        self._stdout_thread.daemon = True
        self._stdout_thread.start()

        self._stderr_queue = Queue()
        self._stderr_thread = Thread(target=RealTimeSubprocess._enqueue_output, args=(self.stderr, self._stderr_queue))
        self._stderr_thread.daemon = True
        self._stderr_thread.start()

    @staticmethod
    def _enqueue_output(stream, queue):
        """
        Add chunks of data from a stream to a queue until the stream is empty.
        """
        for line in iter(lambda: stream.read(4096), b''):
            queue.put(line)
        stream.close()

    def write_contents(self):
        """
        Write the available content from stdin and stderr where specified when the instance was created
        :return:
        """

        def read_all_from_queue(queue):
            res = b''
            size = queue.qsize()
            while size != 0:
                res += queue.get_nowait()
                size -= 1
            return res

        stdout_contents = read_all_from_queue(self._stdout_queue)
        if stdout_contents:
            self._write_to_stdout(stdout_contents)
        stderr_contents = read_all_from_queue(self._stderr_queue)
        if stderr_contents:
            self._write_to_stderr(stderr_contents)
