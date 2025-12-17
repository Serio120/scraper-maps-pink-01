# Este archivo sirve como un puente para que `nix-shell` pueda usar la configuración
# definida en el archivo específico de IDX, `.idx/dev.nix`.
# `nix-shell` buscará este archivo por defecto.

let
  # 1. Importamos la librería de paquetes de Nix.
  pkgs = import <nixpkgs> { system = "x86_64-linux"; };

  # 2. Importamos la configuración de IDX. `.idx/dev.nix` es una función
  #    que espera `pkgs` como argumento, así que se lo pasamos.
  idxConfig = (import ./.idx/dev.nix) { inherit pkgs; };

in
  # 3. Usamos `mkShell` para crear el entorno de shell.
  pkgs.mkShell {
    # 4. Usamos los paquetes definidos en nuestro archivo de configuración.
    buildInputs = idxConfig.packages;

    # 5. Esta es la pieza clave. `shellHook` es un script que se ejecuta en cuanto
    #    `nix-shell` arranca. Usamos esto para exportar la variable de entorno
    #    que hemos definido en la configuración. Esto hace que los navegadores
    #    de Playwright encuentren las librerías del sistema.
    shellHook = ''
      export LD_LIBRARY_PATH="${idxConfig.env.LD_LIBRARY_PATH}:${pkgs.lib.makeLibraryPath [ pkgs.stdenv.cc.cc.lib ]}"
    '';
  }
