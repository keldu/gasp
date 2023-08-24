{ pkgs ? import <nixpkgs> {}
}:

let

in rec {
  gasp = pkgs.callPackage .nix/derivation.nix {};
  gasp-sphinx-example = pkgs.callPackage .nix/docs-derivation.nix {
    inherit gasp;
  };
}
