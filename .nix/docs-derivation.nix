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
    # C++ API generation
    doxygen Doxyfile_cpp
    python3 ${gasp.outPath}/bin/gasp.py doxygen_cpp/xml --namespace duke > cpp_map.json
    # C API generation
    doxygen Doxyfile_c
    python3 ${gasp.outPath}/bin/gasp.py doxygen_c/xml > c_map.json
    # Ensure file tree exists in source
    mkdir -p source/cpp_api source/c_api
    # C++ and C template generation
    python3 ${gasp.outPath}/bin/make_rst.py --title="C++" -t ${gasp.outPath}/templates/rst -m cpp_map.json -o source/cpp_api
    python3 ${gasp.outPath}/bin/make_rst.py --title="C" -t ${gasp.outPath}/templates/rst -m c_map.json -o source/c_api
    make html
  '';

  installPhase = ''
    mkdir -p $out
    mv build/html $out/html
  '';
}
