#!/bin/bash

cur_dir=`pwd`

python=`which python3`
if [ -z "$python" ];then
  python=`which python`
fi

app_name='dailycheckin2'

echo "#!/bin/bash
${python} ${cur_dir}/main.py "\$\@"
"> $app_name

chmod +x $app_name

sh ./uninstall.sh
mv -f $app_name /usr/bin/
