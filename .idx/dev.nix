# To learn more about how to use Nix to configure your environment
# see: https://developers.google.com/idx/guides/customize-idx-env
{ pkgs, lib, ... }:
{
  # Which nixpkgs channel to use.
  channel = "stable-24.05";

  # This is the final, correct, and robust strategy.
  # We let Playwright install its own browsers, and we use Nix to provide the
  # required system-level libraries for those browsers to run.

  packages = [
    # 1. A Python environment with the Playwright library.
    (pkgs.python3.withPackages (ps: [ ps.playwright ]))

    # 2. All the system libraries that the Playwright-downloaded browsers need.
    pkgs.gtk3
    pkgs.nss
    pkgs.nspr
    pkgs.cups
    pkgs.alsa-lib
    pkgs.libxkbcommon
    pkgs.dbus
    pkgs.libxcomposite
    pkgs.libXdamage
    pkgs.libXfixes
    pkgs.libXrandr
    pkgs.libXcomposite
    pkgs.pango
    pkgs.cairo
    pkgs.atk
    pkgs.at-spi2-core
    pkgs.gdk-pixbuf
  ];

  env = {
    # 3. This is the bridge. It tells the browser executables where to find all
    #    the .so files from the packages listed above.
    LD_LIBRARY_PATH = lib.makeLibraryPath (with pkgs; [
      gtk3
      nss
      nspr
      cups
      alsa-lib
      libxkbcommon
      dbus
      libxcomposite
      libXdamage
      libXfixes
      libXrandr
      libXcomposite
      pango
      cairo
      atk
      at-spi2-core
      gdk-pixbuf
    ]);
  };

  idx = {
    extensions = [
      "ms-python.python"
      "google.gemini-cli-vscode-ide-companion"
    ];

    workspace = {
      onCreate = {
        default.openFiles = [ ".idx/dev.nix" "README.md" "scraper.py" ];
      };
      # 4. Ensure browsers are installed every time the workspace starts.
      onStart = {
        install-browsers = "playwright install";
      };
    };
  };
}
