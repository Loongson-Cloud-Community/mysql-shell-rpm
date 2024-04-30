1. Download the following 3 files and put them in the ~/rpmbuild/SOURCE:
Source1:        https://github.com/Loongson-Cloud-Community/protobuf/releases/download/3.9.14/protobuf-3.19.4-static.tar.gz
Source2:        https://github.com/Loongson-Cloud-Community/mysql-server/archive/refs/tags/v8.0.30.tar.gz
Source3:        http://cloud.loongnix.cn/releases/loongarch64abi1/mysql/8.0.30/mysql-8.0.30-build-release.tar.gz

mysql-8.0.30-build-release is the compilation path of mysql source code.
The mysql-8.0.30-build-release originally provided dynamic protoc binary. Here, the static binary in protobuf-3.19.4-static is used to replace the dynamic binary.

2. build
rpmbuild -ba  mysql-shell.spec

