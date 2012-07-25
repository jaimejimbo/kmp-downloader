#!/usr/bin/python
# Downloads kernel from http://kernel.ubuntu.com/~kernel-ppa/mainline/
# Requires: python-bs4
import urlparse
import urllib
import os
import urllib2
import platform
from bs4 import BeautifulSoup
import re
import sys

url = "http://kernel.ubuntu.com/~kernel-ppa/mainline/"
print("Contacting {0}".format(url))
source = urllib.urlopen(url).read()
#print(source)

soup = BeautifulSoup(source)
kernels = list()

rel = platform.release().replace("-generic","")
for link in soup.find_all('a'):
    href = link.get('href')
    if re.search("rc\d", href):
        #If release candidate
        continue
    if href[0] == "v":
        kver = href[1:-1] #strip first and last characters
        rel = platform.release().replace("-generic","")
        if kver > rel:
            # If kernel newer than current one
            #print("{0} > {1}".format(kver, rel))
            kernels.append(href)

# SELECT KERNEL
i = 0
for k in kernels:
    i += 1
    print("{0}. {1}".format(i, k))
selk = -1
while not 0 < selk <= len(kernels):
    try:
        defaultk = len(kernels)
        sel = raw_input("Please enter an integer [{0}]: ".format(defaultk))
        if sel == "":
            selk = defaultk
            break
        selk = int(sel)
    except ValueError:
        continue
print("You chose: {0}".format(kernels[selk-1]))

# SELECT ARCH
i = 0
archs = ("i386", "amd64")
sysarch = platform.machine().replace(
    "x86_64", "amd64").replace("i686", "i386")
print("Your system architecture: {0}".format(sysarch))
try:
    defaultarch = archs.index(sysarch)+1
except:
    defaultarch = 1
for a in archs:
    i += 1
    print("{0}. {1}".format(i, a))
sel = -1
while not 0 < sel <= len(archs):
    try:
        sel = raw_input("Please enter an integer [{0}]: ".format(defaultarch))
        if sel == "":
            sela = defaultarch
            break
        sela = int(sel)
    except ValueError:
        continue
print("You chose: {0}".format(archs[sela-1]))

# SELECT PACKAGES
sel = -1
while True:
    sel = raw_input("Would you like to install kernel headers [Y/n]: ")
    if sel == "":
        selkh = True
        break
    if not sel in tuple("yYnN"):
        continue
    else:
        if sel in tuple("yY"):
            selkh = True
        else:
            selkh = False
        break

sel = -1
while True:
    sel = raw_input("Would you like to install kernel image [Y/n]: ")
    if sel == "":
        selki = True
        break
    if not sel in tuple("yYnN"):
        continue
    else:
        if sel in tuple("yY"):
            selki = True
        else:
            selki = False
        break

sel = -1
while True:
    sel = raw_input("Would you like to install kernel extras [Y/n]: ")
    if sel == "":
        selke = True
        break
    if not sel in tuple("yYnN"):
        continue
    else:
        if sel in tuple("yY"):
            selke = True
        else:
            selke = False
        break

print("Kernel headers: {0}, Kernel image: {1}, Kernel extras: {2}".
        format(selkh, selki, selke))

#21-Jul-2012 22:49 	5 	 
#[ ]	linux-headers-3.5.0-030500-generic_3.5.0-030500.201207211835_amd64.deb	21-Jul-2012 22:42 	912K	 
#[ ]	linux-headers-3.5.0-030500-generic_3.5.0-030500.201207211835_i386.deb	21-Jul-2012 22:49 	901K	 
#[ ]	linux-headers-3.5.0-030500_3.5.0-030500.201207211835_all.deb	21-Jul-2012 22:35 	12M	 
#[ ]	linux-image-3.5.0-030500-generic_3.5.0-030500.201207211835_amd64.deb	21-Jul-2012 22:42 	12M	 
#[ ]	linux-image-3.5.0-030500-generic_3.5.0-030500.201207211835_i386.deb	21-Jul-2012 22:49 	11M	 
#[ ]	linux-image-extra-3.5.0-030500-generic_3.5.0-030500.201207211835_amd64.deb	21-Jul-2012 22:42 	27M	 
#[ ]	linux-image-extra-3.5.0-030500-generic_3.5.0-030500.201207211835_i386.deb

# selk = selected kernel
# sela = selected arch
# selkh = kernel headers? T/F
# selki = kernel image? T/F
# selke = kernel extra? T/F
link = "http://kernel.ubuntu.com/~kernel-ppa/mainline/{0}".format(kernels[selk-1])
print("Contacting {0}".format(link))
source = urllib.urlopen(link).read()
soup = BeautifulSoup(source)
files = list()
for l in soup.find_all('a'):
    href = l.get('href')
    rxstr = "linux-headers.*_(?:{0}|all)\.deb".format(archs[sela-1])
    if selkh and re.search(rxstr, href):
        url = "{0}{1}".format(link, href)
        files.append(url)
    rxstr = "linux-image.*_{0}\.deb".format(archs[sela-1])
    if selki and re.search(rxstr, href):
        url = "{0}{1}".format(link, href)
        files.append(url)
    rxstr = "linux-image-extra.*_{0}\.deb".format(archs[sela-1])
    if selke and re.search(rxstr, href):
        url = "{0}{1}".format(link, href)
        files.append(url)

for url in files:
    #Using /tmp
    os.chdir("/tmp/")
    file_name = url.split('/')[-1]
    u = urllib2.urlopen(url)
    f = open(file_name, 'wb')
    meta = u.info()
    file_size = int(meta.getheaders("Content-Length")[0])
    print("Downloading: {0} Bytes: {1}".format(url, file_size))

    file_size_dl = 0
    block_sz = 8192
    while True:
        buffer = u.read(block_sz)
        if not buffer:
            break

        file_size_dl += len(buffer)
        f.write(buffer)
        p = float(file_size_dl) / file_size
        status = r"{0}  [{1:.2%}]".format(file_size_dl, p)
        status = status + chr(8)*(len(status)+1)
        sys.stdout.write(status)

    f.close()