{ pkgs ? import <nixpkgs> {}
}:

let

in rec {
  gasp = pkgs.callPackage .nix/derivation.nix {};
  gasp-sphinx-example = pkgs.callPackage examples/sphinx/derivation.nix {
    inherit gasp;
  };
}
