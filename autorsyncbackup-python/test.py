#!/usr/bin/python

import subprocess

try:
  output = subprocess.check_output("ls -l; sleep 4; exit 255", stderr=subprocess.STDOUT, shell=True)
except subprocess.CalledProcessError as exc:
  print "error code", exc.returncode, exc.output
  output = exc.output

print 'Have %d bytes in output' % len(output)
print output
