
# Este es un archivo puente temporal para permitir que el comando `nix-shell`
# entienda el formato de configuración específico de IDX `.idx/dev.nix`.

{ pkgs ? import <nixpkgs> {} }:

let
  # 1. Importa la función de configuración desde el archivo .idx/dev.nix
  idxConfigFile = import ./.idx/dev.nix;

  # 2. Llama a esa función, pasándole el argumento `pkgs` que necesita.
  #    El resultado es el conjunto de configuración que definiste.
  idxConfig = idxConfigFile { pkgs = pkgs; };

in
  # 3. Usa pkgs.mkShell para crear un entorno de terminal real.
  pkgs.mkShell {
    # Usa la lista de paquetes de tu configuración para construir el entorno.
    buildInputs = idxConfig.packages;
  }
