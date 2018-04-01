kernel.md

1. fetch kernel source
```
yum -y installl yum-utils make gcc bc
yumdownloader --source kernel-main-4.9.43-3.el7.aarch64
```
2. install source
```
rpm -ihv kernel-main-4.9.43-3.el7.src.rpm
```
3. unpack build default config
```
make bcmrpi3_defconfig
```
