
# Copyright (c) 2016, 2022, Oracle and/or its affiliates.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License, version 2.0,
# as published by the Free Software Foundation.
#
# This program is also distributed with certain software (including
# but not limited to OpenSSL) that is licensed under separate terms, as
# designated in a particular file or component or in included license
# documentation.  The authors of MySQL hereby grant you an additional
# permission to link the program and your derivative works with the
# separately licensed software that they have included with MySQL.
# This program is distributed in the hope that it will be useful,  but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See
# the GNU General Public License, version 2.0, for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA

# Disable "reproducible builds"
%global source_date_epoch_from_changelog 0

# Injected binaries breaks build-id links
%undefine _missing_build_ids_terminate_build

%{?with_static: %global static 1}

%global commercial  0
%global cloud  0

%if 0%{?commercial} || 0%{?cloud}
%global product_suffix 
%endif

# define v8_includedir and v8_libdir for rpmbuild when building static

Summary:        Command line shell and scripting environment for MySQL
Name:           mysql-shell
Version:        8.0.30
Release:        1%{?dist}
License:        GPLv2
URL:            http://dev.mysql.com/
Source0:        https://cdn.mysql.com/Downloads/%{name}-8.0.30-src.tar.gz
Source1:        https://github.com/Loongson-Cloud-Community/protobuf/releases/download/3.9.14/protobuf-3.19.4-static.tar.gz
Source2:        https://github.com/Loongson-Cloud-Community/mysql-server/archive/refs/tags/v8.0.30.tar.gz
Source3:        http://cloud.loongnix.cn/releases/loongarch64abi1/mysql/8.0.30/mysql-8.0.30-build-release.tar.gz

# Dependencies for the cloud version
%if 0%{?cloud}
Requires:       lapack libgfortran5
%endif

%if 0%{?rhel} && 0%{?rhel} <= 7
BuildRequires: cmake3
%else
BuildRequires: cmake
%endif
%if 0%{!?with_protobuf:1} && 0%{!?with_mysql_source:1}
BuildRequires:  protobuf-devel
BuildRequires:  protobuf-compiler
%endif
%if 0%{?bundled_python:1}
# Override __python, else "/usr/lib/rpm/brp-python-bytecompile"
# will use "/usr/bin/python" and may fail
%global __python %{bundled_python}/bin/python
%else
%if 0%{?rhel} == 8
BuildRequires:  python38-devel
%else
BuildRequires:  python3-devel >= 3.8
%endif
%endif
%if 0%{!?bundled_ssh:1}
BuildRequires:  libssh-devel >= 0.9.2
%endif
%if 0%{!?static}
BuildRequires:  mysql-devel
%if 0%{!?bundled_openssl:1}
BuildRequires:  openssl-devel
%endif
%if 0%{!?bundled_curl:1}
BuildRequires:  libcurl-devel
%endif
#BuildRequires:  v8-devel
#BuildRequires:  v8-python
%endif
%if 0%{?commercial} || %{?cloud}
Provides:      mysql-shell = %{version}-%{release}
Obsoletes:     mysql-shell < %{version}-%{release}
%endif

# For rpm => 4.9 only: https://fedoraproject.org/wiki/Packaging:AutoProvidesAndRequiresFiltering
%global __provides_exclude_from ^(%{_datadir}/mysqlsh/.*|%{_prefix}/lib/mysqlsh/.*)$

%if 0%{?rhel} && 0%{?rhel} < 7
# https://fedoraproject.org/wiki/EPEL:Packaging#Generic_Filtering_on_EPEL6
%filter_provides_in %{_datadir}/mysqlsh
%filter_provides_in %{_prefix}/lib/mysqlsh
%endif

%if 0%{?bundled_openssl:1}
%global _openssllibs libcrypto.*|libssl.*
%if 0%{?rhel} && 0%{?rhel} < 7
%filter_from_requires /libcrypto/d
%filter_from_requires /libssl/d
%endif
%else
%global _openssllibs %{nil}
%endif

%if 0%{?bundled_python:1}
%global _pythonlibs libpython.*
%if 0%{?rhel} && 0%{?rhel} < 7
%filter_from_requires /libpython/d
%endif
%else
%global _pythonlibs %{nil}
%endif

%if 0%{?bundled_ssh:1}
%global _sshlibs libssh.*
%if 0%{?rhel} && 0%{?rhel} < 7
%filter_from_requires /libssh/d
%endif
%else
%global _sshlibs %{nil}
%endif

%global __requires_exclude ^(%{_openssllibs}|%{_pythonlibs}|%{_sshlibs})$

%if 0%{?rhel} && 0%{?rhel} < 7
%filter_setup
%endif

%description
MySQL Shell (part of MySQL Server) 8.0
a query and administration shell client and framework.

%if 0%{?suse_version}
%debug_package
%endif

%prep
mkdir -p protobuf-release
tar -xf %{SOURCE1} -C protobuf-release
mkdir -p mysql-source
tar -xf %{SOURCE2} -C mysql-source
mkdir -p mysql-build
tar -xf %{SOURCE3} -C mysql-build
%setup -q -n %{name}-8.0.30-src

%build
rm -rf build && mkdir build && cd build
%if 0%{?rhel} && 0%{?rhel} <= 7
cmake3 .. \
%else
cmake .. \
%endif
    -DMYSQL_BUILD_DIR="/root/rpmbuild/BUILD/mysql-build/mysql-8.0.30-build-release" \
    -DMYSQL_SOURCE_DIR="/root/rpmbuild/BUILD/mysql-source/mysql-server-8.0.30" \
    -DProtobuf_INCLUDE_DIR="/root/rpmbuild/BUILD/protobuf-release/protobuf-3.19.4-static" \
    -DCMAKE_INSTALL_PREFIX=%{_prefix} -DPython_ADDITIONAL_VERSIONS=3.9 \
    -DCMAKE_BUILD_TYPE=RelWithDebInfo \
    -DUSE_LD_LLD=0 \
%if 0%{?commercial} || %{?cloud}
    -DEXTRA_NAME_SUFFIX="%{?product_suffix}" \
%endif
%if "%{_lib}" == "lib64"
    -DLIB_SUFFIX=64 \
%endif
%if 0%{?bundled_mysql_config_editor:1}
    -DBUNDLED_MYSQL_CONFIG_EDITOR=%{bundled_mysql_config_editor} \
%endif
%if 0%{?bundled_ssh:1}
    -DBUNDLED_SSH_DIR=%{bundled_ssh} \
%endif
%if 0%{?static}
    -DMYSQLCLIENT_STATIC_LINKING=ON \
    -DV8_INCLUDE_DIR=%{v8_includedir} \
    -DV8_LIB_DIR=%{v8_libdir} \
%else
    -DMYSQLCLIENT_STATIC_LINKING=ON \
    -DHAVE_V8=OFF \
%endif
%if 0%{?with_protobuf:1}
    -DWITH_PROTOBUF=%{with_protobuf} \
%endif
%if 0%{?with_gmock:1}
    -DWITH_TESTS=ON \
    -DWITH_GMOCK=%{with_gmock} \
%endif
%if 0%{!?with_gmock:1} && 0%{?with_tests:1}
    -DENABLE_DOWNLOADS=1 \
    -DWITH_TESTS=ON \
%endif
%if 0%{?python_deps:1}
    -DPYTHON_DEPS=%{python_deps} \
%endif
%if 0%{?with_mysql_source:1}
    -DMYSQL_SOURCE_DIR="%{with_mysql_source}" \
    -DMYSQL_BUILD_DIR="%{with_mysql_source}/bld" \
    %if 0%{!?with_protobuf:1}
      -DPROTOBUF_INCLUDE_DIR="%{?with_mysql_source}/extra/protobuf/protobuf-3.19.4/src" \
      -DPROTOBUF_LIBRARY="%{?with_mysql_source}/bld/extra/protobuf/protobuf-3.19.4/cmake/libprotobuf.a" \
      -DPROTOBUF_LIBRARY_DEBUG="%{?with_mysql_source}/bld/extra/protobuf/protobuf-3.19.4/cmake/libprotobuf.a"\
    %endif
%endif
%if 0%{?bundled_openssl:1}
    -DBUNDLED_OPENSSL_DIR="%{bundled_openssl}" \
%endif
%if 0%{?bundled_curl:1}
    -DWITH_CURL="%{bundled_curl}" \
%endif
%if 0%{?bundled_python:1}
    -DBUNDLED_PYTHON_DIR="%{bundled_python}" \
%endif
    -DHAVE_PYTHON=1 \
    -DLIBEXECDIR=`basename %{_libexecdir}`


# Supported V8 versions are limited, disable
# V8 in non static for now.
# -DV8_INCLUDE_DIR=%{_includedir}/v8 \
# -DV8_LIB_DIR=%{_libdir} \
# Shared linking don't work
# -DMYSQLCLIENT_STATIC_LINKING=ON \

make %{?_smp_mflags}

%install
cd build
make DESTDIR=%{buildroot} install
# FIXME at this moment only headers are installed but no
# "mysqlshdk" library. It is also unclear if eventually we
# want the lib and headers, in that case likely in a separate
# package. Using a work-around removing all the "dev" files
rm -rf %{buildroot}%{_includedir} 2>/dev/null
rm -f %{buildroot}%{_prefix}/lib*/*.{so*,a} 2>/dev/null
# License and readme are included using %%doc below
rm -f %{buildroot}%{_datadir}/mysqlsh/{LICENSE,README}

%files
# FIXME EL6 doesn't like 'license' macro here, so we use 'doc'
%doc LICENSE
%doc README
%{_bindir}/mysqlsh
%{_bindir}/mysql-secret-store-login-path
%if 0%{?bundled_mysql_config_editor:1}
%{_libexecdir}/mysqlsh/mysql_config_editor
%endif
%{_datadir}/mysqlsh/prompt/*
%{_datadir}/mysqlsh/adminapi-metadata/*
%{_datadir}/mysqlsh/upgrade_checker.msg
%{_datadir}/mysqlsh/Docs/INFO_SRC
%{_datadir}/mysqlsh/Docs/INFO_BIN
%if 0%{?bundled_openssl:1}
%{_prefix}/lib/mysqlsh/libcrypto*
%{_prefix}/lib/mysqlsh/libssl*
%endif
%if 0%{?bundled_python:1}
%{_prefix}/lib/mysqlsh/include/python*
%if 0%{?bundled_shared_python:1}
%{_prefix}/lib/mysqlsh/libpython*
%endif
%endif
%if 0%{?python_deps:1}%{?bundled_python:1}
%{_prefix}/lib/mysqlsh/lib/python*
%endif
%if 0%{?bundled_ssh:1}
%{_prefix}/lib/mysqlsh/libssh*
%endif
%{_prefix}/lib/mysqlsh/plugins/*
%{_prefix}/lib/mysqlsh/python-packages/*

%changelog
* Mon Jun 14 2021 Alfredo Kojima <alfredo.kengi.kojima@oracle.com> - 8.0.27
- Install adminapi-metadata

* Tue Jan 26 2021 Rene Ramirez <j.rene.ramirez@oracle.com> - 8.0.24
- Relocating python dependencies to the embedded site-packages folder

* Thu May 16 2019 Balasubramanian Kandasamy <balasubramanian.kandasamy@oracle.com> - 8.0.17-1
- Enable debug binaries for sles12 and opensuse15

* Mon Oct 8 2018 Rene Ramirez <j.rene.ramirez@oracle.com> - 8.0.14
- Update to use mysql server bundled protobuf if no specific is defined.

* Fri May 18 2018 Pawel Andruszkiewicz <pawel.andruszkiewicz@oracle.com> - 8.0.12
- Add login-path helper.

* Sun Dec 17 2017 Kent Boortz <kent.boortz@oracle.com> - 8.0.4-1
- License file is now always named "LICENSE"

* Wed Nov 01 2017 Alfredo Kojima <alfredo.kengi.kojima@oracle.com> - 8.0.4-1
- Remove Connector/Python dependency

* Thu May 04 2017 Alfredo Kojima <alfredo.kengi.kojima@oracle.com> - 1.0.8-1
- Remove libedit dependency, add sample prompt files

* Mon Mar 13 2017 Alfredo Kojima <alfredo.kengi.kojima@oracle.com> - 1.0.8-1
- Updated for mysqlprovision build change

* Thu Sep 01 2016 Balasubramanian Kandasamy <balasubramanian.kandasamy@oracle.com> - 1.0.5-0.1
- Updated for 1.0.5 labs release

* Wed Mar 23 2016 Alfredo Kojima <alfredo.kengi.kojima@oracle.com> - 1.0.3-1
- updated for 1.0.3, bug fixes

* Mon Mar 14 2016 Kent Boortz <kent.boortz@oracle.com> - 1.0.2.8-1
- initial package
