set -e
mkdir -p ~/intervals
tgt=~/intervals
gcc intervals.c -o "$tgt/intervals" -O3 -Wall -Wextra -pedantic
gcc intervals.c -o "$tgt/intervals_dbg" -O3 -Wall -Wextra -pedantic -g -fsanitize=address,undefined
cp tester.py "$tgt/tester.py"
dos2unix "$tgt/tester.py" &>/dev/null
