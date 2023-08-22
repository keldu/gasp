{ lib
, stdenvNoCC
, python310
, python310Packages
}:

stdenvNoCC.mkDerivation {
  pname = "gasp";
  version = "0.0.0";

  src = ./..;

  nativeBuildInputs = [
    python310
  ];

  buildPhase = ''
  '';

  installPhase = ''
    mkdir -p $out/bin
    mkdir -p $out/templates
    cp $src/python/gasp.py $out/bin
    cp $src/python/make_rst.py $out/bin
    cp -r $src/templates/rst $out/templates/rst
  '';
}
