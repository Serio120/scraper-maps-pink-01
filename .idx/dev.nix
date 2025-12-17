# To learn more about how to use Nix to configure your environment
# see: https://developers.google.com/idx/guides/customize-idx-env
{ pkgs, ... }:
# This is the final and correct configuration. It is based on the explicit
# error messages provided by Playwright, which lists all missing dependencies.
{
  channel = "stable-24.05";

  # The strategy is to let Playwright manage its own browsers (`playwright install`)
  # and use Nix to provide the complete set of required system libraries.
  packages = [
    # 1. Python environment with the Playwright library.
    (pkgs.python3.withPackages (ps: [ ps.playwright ]))

    # 2. The complete list of libraries required by the browser, as reported by
    #    Playwright's own error message. No more, no less.
    pkgs.glib
    pkgs.nss
    pkgs.nspr
    pkgs.cups
    pkgs.atk
    pkgs.at-spi2-core
    pkgs.at-spi2-atk
    pkgs.dbus
    pkgs.libdrm
    pkgs.expat
    pkgs.libxcb
    pkgs.libxkbcommon
    pkgs.mesa
    pkgs.pango
    pkgs.cairo
    pkgs.gdk-pixbuf
    pkgs.gtk3
    pkgs.alsa-lib
    pkgs.xorg.libX11
    pkgs.xorg.libXcomposite
    pkgs.xorg.libXdamage
    pkgs.xorg.libXext
    pkgs.xorg.libXfixes
    pkgs.xorg.libXrandr
  ];

  env = {
    # 3. This environment variable tells the Playwright-installed browsers where to
    #    find all the Nix-provided libraries listed above.
    LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath (with pkgs; [
      glib nss nspr cups atk at-spi2-core at-spi2-atk dbus libdrm expat libxcb
      libxkbcommon mesa pango cairo gdk-pixbuf gtk3 alsa-lib xorg.libX11
      xorg.libXcomposite xorg.libXdamage xorg.libXext xorg.libXfixes
      xorg.libXrandr
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
      # 4. On every workspace start, automatically install the browsers into a
      #    known location, where the LD_LIBRARY_PATH can do its work.
      onStart = {
        install-browsers = "playwright install";
      };
    };
  };
}
