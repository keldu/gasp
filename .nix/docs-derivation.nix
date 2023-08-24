{ lib
, stdenvNoCC
, python310
, python310Packages
, doxygen
, gasp
, target_src ? { outPath = ./../examples/sphinx; }
}:

stdenvNoCC.mkDerivation {
  pname = "gasp-sphinx-example";
  version = "0.0.0";

  src = target_src;

  nativeBuildInputs = [
    python310
    python310Packages.sphinx
    python310Packages.sphinx-rtd-theme
    doxygen
    gasp
  ];

  buildPhase = ''
    doxygen Doxygen.in
    python3 ${gasp.outPath}/bin/gasp.py doxygen/xml --namespace duke > map.json
    mkdir -p source/api
    python3 ${gasp.outPath}/bin/make_rst.py -t ${gasp.outPath}/templates/rst -m map.json -o source/api
    make html
  '';

  installPhase = ''
    mkdir -p $out
    mv build/html $out/html
  '';
}
