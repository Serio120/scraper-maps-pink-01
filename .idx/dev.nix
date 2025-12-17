# To learn more about how to use Nix to configure your environment
# see: https://developers.google.com/idx/guides/customize-idx-env
{ pkgs, ... }:
# This configuration corrects the Nix syntax error (lists are space-separated, not comma-separated)
# and includes all previously identified dependencies for both Chromium and Firefox.
{
  channel = "stable-24.05";

  packages = [
    # --- Base Environment ---
    (pkgs.python3.withPackages (ps: [ ps.playwright ]))

    # --- Dependencies for Chromium ---
    pkgs.udev pkgs.glib pkgs.nss pkgs.nspr pkgs.cups pkgs.atk
    pkgs.at-spi2-core pkgs.at-spi2-atk pkgs.dbus pkgs.libdrm pkgs.expat
    pkgs.libxkbcommon pkgs.mesa pkgs.pango pkgs.cairo pkgs.gdk-pixbuf
    pkgs.gtk3 pkgs.alsa-lib pkgs.xorg.libX11 pkgs.xorg.libXcomposite
    pkgs.xorg.libXdamage pkgs.xorg.libXext pkgs.xorg.libXfixes
    pkgs.xorg.libXrandr pkgs.xorg.libxcb

    # --- Dependencies for Firefox (as per the latest error) ---
    pkgs.xorg.libXcursor pkgs.xorg.libXi pkgs.xorg.libXtst
    pkgs.xorg.libXrender pkgs.freetype pkgs.fontconfig pkgs.dbus-glib
  ];

  env = {
    # This environment variable tells the Playwright-installed browsers where to
    # find all the Nix-provided libraries listed above.
    LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath (with pkgs; [
      # Chromium paths
      udev glib nss nspr cups atk at-spi2-core at-spi2-atk dbus libdrm expat
      libxkbcommon mesa pango cairo gdk-pixbuf gtk3 alsa-lib xorg.libX11
      xorg.libXcomposite xorg.libXdamage xorg.libXext xorg.libXfixes
      xorg.libXrandr xorg.libxcb
      # Firefox paths
      xorg.libXcursor xorg.libXi xorg.libXtst xorg.libXrender freetype
      fontconfig dbus-glib
    ]);
  };

  idx = {
    extensions = [ "ms-python.python" "google.gemini-cli-vscode-ide-companion" ];
    workspace = {
      onCreate = { default.openFiles = [ ".idx/dev.nix" "README.md" "scraper.py" ]; };
      # We no longer need to run playwright install on every start,
      # as the .nix shell now handles the environment reliably.
      onStart = { };
    };
  };
}
