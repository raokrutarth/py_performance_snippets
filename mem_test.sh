#/bin/bash -ex

#
# Script to compare memory usage of python programs.
# Resources:
#   - http://fa.bianp.net/blog/2014/plot-memory-usage-as-a-function-of-time/
#   - https://pypi.org/project/memory-profiler/
#   - https://docs.python.org/3.7/library/timeit.html
#   - https://pympler.readthedocs.io/en/latest/
#   - https://docs.python.org/3/library/resource.html
#   - https://manpages.debian.org/buster/manpages-dev/getrusage.2.en.html

# sample the memory usage every mem_sample_sec seconds
mem_sample_sec="0.0005"

mprof run --interval ${mem_sample_sec} --multiprocess ./mem.py 1
mprof plot --title="New class object per call" -o mem_obj_per.jpg

echo

mprof run --interval ${mem_sample_sec} --multiprocess ./mem.py 2
mprof plot --title="Decorator per call" -o mem_decorator_per.jpg


rm -rf *.dat