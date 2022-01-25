# diff2html

This is a simple tool written in python to covert `git diff` output into HTML with split view of the changes.

## Usage

Redirect output of the git diff through a pipe into python script:
```shell
$ cat diff.patch | diff2html.py
```
If you want the script to output to file instead of dumping HTML into terminal use `-f` option as such:
```shell
$ cat diff.patch | diff2html.py -f
```