# To learn more about how to use Nix to configure your environment
# see: https://developers.google.com/idx/guides/customize-idx-env
{ pkgs, ... }:
# This configuration adds the pandas library for data manipulation and CSV export.
{
  channel = "stable-24.05";

  packages = [
    # Python environment with Playwright for browsing and Pandas for data handling.
    (pkgs.python3.withPackages (ps: [ ps.playwright ps.pandas ]))

    # --- Dependencies for Chromium ---
    pkgs.udev pkgs.glib pkgs.nss pkgs.nspr pkgs.cups pkgs.atk
    pkgs.at-spi2-core pkgs.at-spi2-atk pkgs.dbus pkgs.libdrm pkgs.expat
    pkgs.libxkbcommon pkgs.mesa pkgs.pango pkgs.cairo pkgs.gdk-pixbuf
    pkgs.gtk3 pkgs.alsa-lib pkgs.xorg.libX11 pkgs.xorg.libXcomposite
    pkgs.xorg.libXdamage pkgs.xorg.libXext pkgs.xorg.libXfixes
    pkgs.xorg.libXrandr pkgs.xorg.libxcb

    # --- Dependencies for Firefox ---
    pkgs.xorg.libXcursor pkgs.xorg.libXi pkgs.xorg.libXtst
    pkgs.xorg.libXrender pkgs.freetype pkgs.fontconfig pkgs.dbus-glib
  ];

  env = {
    LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath (with pkgs; [
      # All browser dependencies
      udev glib nss nspr cups atk at-spi2-core at-spi2-atk dbus libdrm expat
      libxkbcommon mesa pango cairo gdk-pixbuf gtk3 alsa-lib xorg.libX11
      xorg.libXcomposite xorg.libXdamage xorg.libXext xorg.libXfixes
      xorg.libXrandr xorg.libxcb xorg.libXcursor xorg.libXi xorg.libXtst
      xorg.libXrender freetype fontconfig dbus-glib
    ]);
  };

  idx = {
    extensions = [ "ms-python.python" "google.gemini-cli-vscode-ide-companion" ];
    workspace = {
      onCreate = { default.openFiles = [ ".idx/dev.nix" "README.md" "scraper.py" ]; };
      onStart = { };
    };
  };
}
