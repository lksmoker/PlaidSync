{pkgs}: {
  deps = [
    pkgs.cacert
    pkgs.libffi
    pkgs.rustc
    pkgs.pkg-config
    pkgs.libxcrypt
    pkgs.libiconv
    pkgs.cargo
    pkgs.unixtools.netstat
    pkgs.openssl
    pkgs.sqlite-interactive
  ];
}
