{ pkgs ? import <nixpkgs> {}
, clang ? pkgs.clang_15
, clang-tools ? pkgs.clang-tools_15
}:

let
  forstio = (import ((builtins.fetchGit {
    url = "git@git.keldu.de:forstio/forstio";
    ref = "dev";
  }).outPath + "/default.nix"){
    inherit clang;
    inherit clang-tools;
  }).forstio;

in pkgs.callPackage ./.nix/derivation.nix {
  inherit forstio;
  inherit clang;
  inherit clang-tools;
}
