{pkgs}: {
  deps = [
    pkgs.unixtools.netstat
    pkgs.openssl
    pkgs.sqlite-interactive
  ];
}
