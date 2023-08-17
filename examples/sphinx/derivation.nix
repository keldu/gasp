{ lib
, stdenvNoCC
, python310
, python310Packages
}:

stdenvNoCC.mkDerivation {
  pname = "gasp-sphinx-example";
  version = "0.0.0";

  src = ./.;

  nativeBuildInputs = [
    python310
    python310Packages.sphinx
    python310Packages.sphinx-rtd-theme
  ];

  buildPhase = ''
    make html
  '';

  installPhase = ''
    mkdir -p $out
    mv build/html $out/html
  '';
}
