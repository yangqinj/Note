import subprocess

print('$ date')
r = subprocess.call(['date'])
print('Exit code:', r)



## 子进程需要输入，可以使用communicate方法
print('$ nslookup')
# 首先输入: nsloopup命令
p = subprocess.Popen(['nslookup'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
# 然后依次每行输入：
# set q=mx
# python.org
# exit
output, error = p.communicate(b'set q=mx\npython.org\nexit\n')
print(output.decode('utf-8'))
print("Exit code {}".format(p.returncode))
