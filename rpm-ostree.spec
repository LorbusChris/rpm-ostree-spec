Summary: Client side upgrade program and server side compose tool
Name: rpm-ostree
Version: 2014.100
Release: 1%{?dist}
#VCS: https://github.com/cgwalters/rpm-ostree
# This tarball is generated via "make -f Makefile.dist-packaging dist-snapshot"
Source0: rpm-ostree-%{version}.tar.xz
License: LGPLv2+
URL: https://github.com/cgwalters/rpm-ostree
# We always run autogen.sh
BuildRequires: autoconf automake libtool
# For docs
BuildRequires: gtk-doc
BuildRequires: gnome-common
BuildRequires: pkgconfig(ostree-1) >= 2014.4
BuildRequires: pkgconfig(libgsystem)
BuildRequires: pkgconfig(json-glib-1.0)
BuildRequires: pkgconfig(rpm)
BuildRequires: pkgconfig(hawkey)

# For now only treecompose requires this
#Requires: /usr/bin/yum
Requires: ostree >= 2014.3

%description
This tool binds together the world of RPM packages with the OSTree
model of bootable filesystem trees.  It provides commands usable both
on client systems as well as server-side composes.

%prep
%setup -q -n %{name}-%{version}

%build
env NOCONFIGURE=1 ./autogen.sh
%configure --disable-silent-rules
make %{?_smp_mflags}

%install
make install DESTDIR=$RPM_BUILD_ROOT INSTALL="install -p -c"

%files
%doc COPYING README.md
%{_bindir}/rpm-ostree
%{_libdir}/%{name}/
%{_mandir}/man*/*.gz

%changelog
* Fri May 23 2014 Colin Walters <walters@verbum.org>
- Previous autobuilder code is split off into rpm-ostree-toolbox

* Sun Apr 13 2014 Colin Walters <walters@verbum.org>
- New upstream release

* Tue Apr 08 2014 Colin Walters <walters@verbum.org>
- Drop requires on yum to allow minimal images without it

* Mon Mar 31 2014 Colin Walters <walters@verbum.org>
- New upstream release

* Sat Mar 22 2014 Colin Walters <walters@verbum.org> - 2014.6.3.g5707fa7-2
- Bump ostree version requirement

* Sat Mar 22 2014 Colin Walters <walters@verbum.org> - 2014.6.3.g5707fa7-1
- New git snapshot, add rpm-ostree-sign to file list

* Sat Mar 22 2014 Colin Walters <walters@verbum.org> - 2014.6-1
- New upstream version

* Fri Mar 07 2014 Colin Walters <walters@verbum.org> - 2014.5-1
- Initial package

