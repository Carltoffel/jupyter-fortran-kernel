from ipykernel.kernelbase import Kernel
import re
import tempfile
import os
import os.path as path

from .kernel_subprocess    import RealTimeSubprocess
from .kernel_cleanup       import cleanup_files
from .kernel_code_analyser import analyse

class FortranKernel(Kernel):
    implementation         = 'jupyter_fortran_kernel'
    implementation_version = '0.1.0'
    language               = 'Fortran'
    language_version       = 'F2018'
    language_info          = {'name'           : 'fortran',
                              'mimetype'       : 'text/plain',
                              'file_extension' : '.f90'}
    banner = "Fortran kernel.\n" \
             "Uses gfortran, compiles in F2018, and creates source code files and executables in temporary folder.\n"

    def __init__(self, *args, **kwargs):
        super(FortranKernel, self).__init__(*args, **kwargs)
        self.files = []
        self.output_files = []
        #
        self.build_dir = tempfile.TemporaryDirectory()
        self.source_files = []
        self.object_files = []
        self.module_files = []

    def new_temp_file(self, **kwargs):
        """Create a new temp file to be deleted when the kernel shuts down"""
        kwargs['delete'] = False  # don't delete file after closing
        kwargs['mode'] = 'w'
        file = tempfile.NamedTemporaryFile(**kwargs)
        self.files.append(file.name)
        return file

    def _write_to_stdout(self, contents):
        self.send_response(self.iopub_socket, 'stream',
                           {'name': 'stdout',
                            'text': contents} )

    def _write_to_stderr(self, contents):
        self.send_response(self.iopub_socket, 'stream',
                           {'name': 'stderr',
                            'text': contents} )

    def create_jupyter_subprocess(self, cmd):
        return RealTimeSubprocess(
                cmd,
                lambda contents: self._write_to_stdout(contents.decode()),
                lambda contents: self._write_to_stderr(contents.decode()) )

    def compile_with_gfortran(self, source_filename, binary_filename, magics):
        magics['cflags'] += ['-fPIC']
        args = ['gfortran', source_filename] + ['-o', binary_filename] \
             + magics['cflags'] + magics['ldflags'] \
             + ['-J', self.build_dir.name, '-I', self.build_dir.name]
        if magics['program']:
            args += self.output_files
        else:
            args += ['-c']
            self.output_files.append(binary_filename)
        return self.create_jupyter_subprocess(args)
        # TODO keep track of each cell output and replace output files


    def do_execute(self, code, silent, store_history=True,
                   user_expressions=None, allow_stdin=False):

        magics = analyse(code)

        with self.new_temp_file(suffix='.f90') as source_file:
            source_file.write(code)
            source_file.flush()
            with self.new_temp_file(dir=self.build_dir.name, suffix='.out') \
                    as binary_file:
                p = self.compile_with_gfortran(source_file.name,
                                               binary_file.name,
                                               magics)
                while p.poll() is None:
                    p.write_contents()
                p.write_contents()
                if p.returncode != 0:  # Compilation failed
                    self._write_to_stderr(
                            "[Fortran kernel] gfortran exited with code {}, the executable will not be executed"
                                .format(p.returncode))
                    return {'status'          : 'ok',
                            'execution_count' : self.execution_count,
                            'payload'         : [],
                            'user_expressions': {} }

        if not magics['program']:
            return {'status'          : 'ok',
                    'execution_count' : self.execution_count,
                    'payload'         : [],
                    'user_expressions': {} }

        p = self.create_jupyter_subprocess([binary_file.name] + magics['args'])
        while p.poll() is None:
            p.write_contents()
        p.write_contents()

        if p.returncode != 0:
            self._write_to_stderr("[Fortran kernel] Executable exited with code {}"
                                  .format(p.returncode))
        return {'status'          : 'ok',
                'execution_count' : self.execution_count,
                'payload'         : [],
                'user_expressions': {}}

    def do_shutdown(self, restart):
        """Cleanup the created source code files and executables when shutting down the kernel"""
        cleanup_files(self.files +
                      self.output_files)
