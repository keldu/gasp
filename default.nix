{ pkgs ? import <nixpkgs> {}
}:

let

in {
  sphinx-example = pkgs.callPackage examples/sphinx/derivation.nix {
  };
}
