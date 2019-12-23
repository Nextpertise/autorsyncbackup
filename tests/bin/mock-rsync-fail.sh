#!/bin/bash

cat <<EOF
sending incremental file list
EOF

cat <<EOF >&2
rsync: link_stat "/non-existent" failed: No such file or directory (2)
EOF

cat <<EOF

Number of files: 0
Number of created files: 0
Number of deleted files: 0
Number of regular files transferred: 0
Total file size: 0 bytes
Total transferred file size: 0 bytes
Literal data: 0 bytes
Matched data: 0 bytes
File list size: 0
File list generation time: 0.001 seconds
File list transfer time: 0.000 seconds
Total bytes sent: 18
Total bytes received: 12

sent 18 bytes  received 12 bytes  60.00 bytes/sec
total size is 0  speedup is 0.00
EOF

cat <<EOF >&2
rsync error: some files/attrs were not transferred (see previous errors) (code 23) at main.c(1207) [sender=3.1.3]
EOF

exit 1
