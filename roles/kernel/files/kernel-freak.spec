%global debug_package %{nil}
%define build_name freak
%define variants %{build_name}

# configuration
%define rpm_version 4.14.32
%define rpm_buildnr 1
%define knl_version 4.14.32
%define knl_vername 4.14.32-%{rpm_buildnr}
%define config_version %{rpm_buildnr}-%{build_name}
%define knl_config_version %{knl_vername}-%{build_name}
# Cross compile requested?
%define with_cross    %{?_with_cross:         1} %{?!_with_cross:        0}
%define cross_target %{_target_cpu}


Name:         kernel-%{build_name}
License:      GPLv2
Version:      %{rpm_version}
Release:      %{rpm_buildnr}%{?dist}
Summary:      linux kernel, raspberry pi 3, mainline
Group:        System Environment/Kernel

BuildRequires: bc

Requires:     linux-firmware
Requires:     dracut
Requires:     grubby
Provides:     kernel = %{version}-%{release}

#cross compile make
%if %{with_cross}
%define cross_opts ARCH=arm64 CROSS_COMPILE=%{cross_target}-linux-gnu-
%endif

Source0:      linux-%{knl_version}.tar.bz2
Source1:      config.%{build_name}
Source2:			bcm2710-rpi-3-b-plus.dtb


%description
linux kernel, raspberry pi 3, mainline


%prep
%define make make %{?cross_opts}
%setup -q -n linux-%{knl_version}

%build
# configure
for variant in %{variants}; do
	mkdir build-$variant
	tweaks=""
	case "$variant" in
	*)
		base="defconfig"
		tweaks="$tweaks %{SOURCE1}"
		make="%{make}"
		tbuild="Image modules dtbs"
		tinstall="modules_install dtbs_install install"
		;;
	esac
	echo "make='$make'" > build-$variant/env.sh
	echo "tbuild='$tbuild'" >> build-$variant/env.sh
	echo "tinstall='$tinstall'" >> build-$variant/env.sh
	cat build-$variant/env.sh
	$make O=build-$variant ${base}
	for tweak in $tweaks; do
		cat "$tweak" >> build-$variant/.config
	done
	echo "CONFIG_LOCALVERSION=\"-%{rpm_buildnr}-${variant}\"" \
		>> build-$variant/.config
	$make -C build-$variant olddefconfig
	cp build-$variant/.config build-$variant/config-%{knl_config_version}
done

# build
for variant in %{variants}; do
	source build-$variant/env.sh
	$make -C build-$variant -k %{?_smp_mflags} $tbuild
done

%install
mkdir -p %{buildroot}/boot
for variant in %{variants}; do
	source build-$variant/env.sh
	$make INSTALL_PATH=%{buildroot}/boot \
	     INSTALL_DTBS_PATH=%{buildroot}/boot/dtb-%{knl_vername}-$variant \
	     INSTALL_MOD_PATH=%{buildroot} \
	     INSTALLKERNEL=/bin/true \
	     -C build-$variant \
	     $tinstall
done
rm -rf %{buildroot}/lib/firmware

cp %{buildroot}/boot/dtb-%{knl_config_version}/broadcom/bcm2837-rpi-3-b.dtb \
	%{SOURCE2} \
   %{buildroot}/boot/dtb-%{knl_config_version}/

%post
version="%{config_version}"
kernel="vmlinux-%{knl_config_version}"
initrd="initramfs-%{knl_config_version}.img"
title="kernel-%{knl_config_version}"
if test -f /boot/cmdline.txt; then
	args="$(cat /boot/cmdline.txt)"
else
	args="$(cat /proc/cmdline)"
fi
echo "# creating initrd for $kernel"
dracut "/boot/$initrd" "$version"
echo "# adding $kernel to extlinux"
mkdir -p /boot/extlinux
touch /boot/extlinux/extlinux.conf
grubby --extlinux \
	--add-kernel "/boot/$kernel" \
	--initrd "/boot/$initrd" \
	--devtreedir "/dtb-$version/" \
	--make-default \
	--title "$title" \
	--args "#args#"
# hack to avoid grubby mangle "root=..." in $args
# also: fdt -> fdtdir fixup
sed -i	-e "s|#args#|$args|" \
	-e "s|fdt /dtb-|fdtdir /dtb-|" \
	/boot/extlinux/extlinux.conf
# enable boot menu
if ! grep -q "menu title" /boot/extlinux/extlinux.conf; then
	echo "# enable boot menu"
	sed -i -e '1s|^|menu title select kernel\ntimeout 100\n\n|' \
		/boot/extlinux/extlinux.conf
fi

%preun
version="%{knl_config_version}"
kernel="vmlinux-${version}"
initrd="initramfs-${version}.img"
echo "# removing $kernel from extlinux"
grubby --extlinux --remove-kernel "/boot/$kernel"
rm -f "/boot/$initrd"


%files
%doc build-%{build_name}/config-%{knl_config_version}
/boot/System.map-%{knl_config_version}
/boot/vmlinux-%{knl_config_version}
/boot/dtb-%{knl_config_version}
/lib/modules/%{knl_config_version}

%changelog
* Tue Oct 31 2017 Tianyue Lan <tianyue.lan@oracle.com> [4.9.43-3]
- Initial build
- commit is 84a1781639429747b894f5121476b514a6a20651

# vim: ts=2 sw=2
