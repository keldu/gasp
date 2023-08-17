{ lib
, stdenvNoCC
, scons
, clang
, clang-tools
, forstio
, cxxopts
, libxml2
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
    libxml2
  ];

  outputs = [ "out" "dev" ];
}
