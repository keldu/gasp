{ lib
, stdenvNoCC
, scons
, clang
, clang-tools
, forstio
, cxxopts
}:

stdenvNoCC.mkDerivation {
  pname = "kel-gasp";
  version = "0.0.0";
  src = ./..;

  nativeBuildInputs = [
    scons
    clang
    clang-tools
  ];

  buildInputs = [
    forstio.core
    forstio.async
    forstio.codec
    cxxopts
  ];

  outputs = [ "out" "dev" ];
}
