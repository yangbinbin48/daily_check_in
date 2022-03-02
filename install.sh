#!/bin/bash

cur_dir=`pwd`

python=`which python`
if [ -z "$python" ];then
  python=`which python3`
fi

echo "#!/bin/bash
${python} ${cur_dir}/main.py "\$\@"
"> dailycheckin

chmod +x dailycheckin
mv -f dailycheckin /usr/bin/dailycheckin
