from ipykernel.kernelapp import IPKernelApp
from .kernel import FortranKernel
IPKernelApp.launch_instance(kernel_class=FortranKernel)
