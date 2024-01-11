%global nm_version 1.2
%global nma_version 1.0
%global glib_required_version 2.53.0
%global gtk_required_version 3.11.3
%global geoclue_version 2.3.1

Name:           gnome-initial-setup
Version:        3.28.0
Release:        11%{?dist}
Summary:        Bootstrapping your OS

License:        GPLv2+
URL:            https://wiki.gnome.org/Design/OS/InitialSetup
Source0:        https://download.gnome.org/sources/%{name}/3.28/%{name}-%{version}.tar.xz
Source1:        vendor.conf
Patch0:         honor-firstboot-disabled.patch
# https://bugzilla.gnome.org/show_bug.cgi?id=793501 and https://bugzilla.gnome.org/show_bug.cgi?id=794166
Patch1:         reduce-initial-setup-redundancy.patch
# https://bugzilla.gnome.org/show_bug.cgi?id=754213
Patch2:         allow-weak-passwords.patch
# https://bugzilla.redhat.com/show_bug.cgi?id=1655150
Patch3:         quacks-like-fedora.patch
# https://bugzilla.redhat.com/show_bug.cgi?id=1703333
Patch4:         gnome-initial-setup-3.28.0-fix-japanese-defaults.patch
# https://bugzilla.redhat.com/show_bug.cgi?id=1838088
Patch5:         gnome-initial-setup-3.28.0-fix-legacy-faces-missing-icon.patch
# https://bugzilla.redhat.com/show_bug.cgi?id=2097848
Patch6:         timezones.patch

BuildRequires:  git
BuildRequires:  krb5-devel
BuildRequires:  desktop-file-utils
BuildRequires:  intltool
BuildRequires:  libpwquality-devel
BuildRequires:  pkgconfig(libnm) >= %{nm_version}
BuildRequires:  pkgconfig(libnma) >= %{nma_version}
BuildRequires:  pkgconfig(accountsservice)
BuildRequires:  pkgconfig(gnome-desktop-3.0)
BuildRequires:  pkgconfig(gstreamer-1.0)
BuildRequires:  pkgconfig(cheese)
BuildRequires:  pkgconfig(cheese-gtk) >= 3.3.5
BuildRequires:  pkgconfig(fontconfig)
BuildRequires:  pkgconfig(geocode-glib-1.0)
BuildRequires:  pkgconfig(gweather-3.0)
BuildRequires:  pkgconfig(goa-1.0)
BuildRequires:  pkgconfig(goa-backend-1.0)
BuildRequires:  pkgconfig(gtk+-3.0) >= %{gtk_required_version}
BuildRequires:  pkgconfig(glib-2.0) >= %{glib_required_version}
BuildRequires:  pkgconfig(gio-2.0) >= %{glib_required_version}
BuildRequires:  pkgconfig(gio-unix-2.0) >= %{glib_required_version}
BuildRequires:  pkgconfig(gdm)
BuildRequires:  pkgconfig(iso-codes)
BuildRequires:  pkgconfig(libgeoclue-2.0) >= %{geoclue_version}
BuildRequires:  pkgconfig(packagekit-glib2)
BuildRequires:  pkgconfig(webkit2gtk-4.0)
BuildRequires:  krb5-devel
BuildRequires:  ibus-devel
BuildRequires:  rest-devel
BuildRequires:  polkit-devel
BuildRequires:  libsecret-devel
# Needed to run autoreconf, for patches that touch autotools bits
BuildRequires:  autoconf
BuildRequires:  gnome-common

# gnome-initial-setup is being run by gdm
Requires: gdm
Requires: geoclue2-libs%{?_isa} >= %{geoclue_version}
Requires: glib2%{?_isa} >= %{glib_required_version}
# we install a rules file
Requires: polkit-js-engine
Requires: /usr/bin/gkbd-keyboard-display

Requires(pre): shadow-utils

Provides: user(%name)

%description
GNOME Initial Setup is an alternative to firstboot, providing
a good setup experience to welcome you to your system, and walks
you through configuring it. It is integrated with gdm.

%prep
%autosetup -p1 -Sgit

%build
# patches touch am files
autoreconf -i
%configure \
  --enable-software-sources \
  --with-vendor-conf-file=%{_datadir}/gnome-initial-setup/vendor.conf
make %{?_smp_mflags}

%install
%make_install
find %{buildroot} -name '*.la' -exec rm -f {} ';'

# Desktop file does not (and probably will not) ever validate, as it uses
# an absolute path /tmp/-style trigger to determine whether to autostart.
# desktop-file-validate %%{buildroot}/%%{_sysconfdir}/xdg/autostart/gnome-welcome-tour.desktop
desktop-file-validate %{buildroot}%{_sysconfdir}/xdg/autostart/gnome-initial-setup-copy-worker.desktop
desktop-file-validate %{buildroot}%{_datadir}/gdm/greeter/applications/gnome-initial-setup.desktop
desktop-file-validate %{buildroot}%{_datadir}/gdm/greeter/applications/setup-shell.desktop

mkdir -p %{buildroot}%{_datadir}/gnome-initial-setup
cp %{SOURCE1} %{buildroot}%{_datadir}/gnome-initial-setup/

%find_lang %{name}

%pre
useradd -rM -d /run/gnome-initial-setup/ -s /sbin/nologin %{name} &>/dev/null || :

%files -f %{name}.lang
%license COPYING
%doc README
%{_libexecdir}/gnome-initial-setup
%{_libexecdir}/gnome-initial-setup-copy-worker
%{_libexecdir}/gnome-welcome-tour
%{_sysconfdir}/xdg/autostart/gnome-welcome-tour.desktop
%{_sysconfdir}/xdg/autostart/gnome-initial-setup-copy-worker.desktop
%{_sysconfdir}/xdg/autostart/gnome-initial-setup-first-login.desktop

%{_datadir}/gdm/greeter/applications/gnome-initial-setup.desktop
%{_datadir}/gdm/greeter/applications/setup-shell.desktop
%{_datadir}/gnome-session/sessions/gnome-initial-setup.session
%{_datadir}/gnome-shell/modes/initial-setup.json
%{_datadir}/polkit-1/rules.d/20-gnome-initial-setup.rules

%dir %{_datadir}/gnome-initial-setup
%{_datadir}/gnome-initial-setup/vendor.conf

%changelog
* Tue Jun 21 2022 Michael Catanzaro <mcatanzaro@redhat.com> - 3.28.0-11
- Remove timezone boundaries
  Related: #2097849
 
* Tue Nov 23 2021 David King <dking@redhat.com> - 3.28.0-10
- Fix missing icon for legacy faces (#1838088)

* Mon Oct 19 2020 David King <dking@redhat.com> - 3.28.0-9
- Fix Japanese language default (#1703333)

* Mon Feb 18 2019 Ray Strode <rstrode@redhat.com> - 3.28.0-8
- Ensure vendora logo gets used instead of foot
  Resolves: #1655150

* Mon Apr 30 2018 Adam Williamson <awilliam@redhat.com> - 3.28.0-7
- Drop unnecessary pkgconfig(NetworkManager) BuildRequire
- Run autoreconf to avoid automake version mismatch

* Wed Apr 11 2018 Michael Catanzaro <mcatanzaro@gnome.org> - 3.28.0-6
- Allow setting weak passwords

* Mon Apr 02 2018 Michael Catanzaro <mcatanzaro@gnome.org> - 3.28.0-5
- Move vendor.conf to /usr/share

* Sat Mar 31 2018 Michael Catanzaro <mcatanzaro@gnome.org> - 3.28.0-4
- Forgot to update vendor.conf in the previous build

* Sat Mar 31 2018 Michael Catanzaro <mcatanzaro@gnome.org> - 3.28.0-3
- Update reduce initial setup redundancy patch again

* Sat Mar 31 2018 Michael Catanzaro <mcatanzaro@gnome.org> - 3.28.0-2
- Update reduce initial setup redundancy patches

* Tue Mar 13 2018 Kalev Lember <klember@redhat.com> - 3.28.0-1
- Update to 3.28.0

* Fri Feb 16 2018 Michael Catanzaro <mcatanzaro@gnome.org> - 3.27.90-2
- Install vendor.conf to conditionally suppress certain pages

* Fri Feb 16 2018 Michael Catanzaro <mcatanzaro@gnome.org> - 3.27.90-1
- Upgrade to 3.27.90 and add reduce initial setup redundancy patches

* Tue Feb 13 2018 Björn Esser <besser82@fedoraproject.org> - 3.26.0-5
- Rebuild against newer gnome-desktop3 package

* Wed Feb 07 2018 Fedora Release Engineering <releng@fedoraproject.org> - 3.26.0-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Mon Feb 05 2018 Kalev Lember <klember@redhat.com> - 3.26.0-3
- Rebuilt for libgweather soname bump

* Sat Jan 20 2018 Björn Esser <besser82@fedoraproject.org> - 3.26.0-2
- Rebuilt for switch to libxcrypt

* Thu Sep 14 2017 Kalev Lember <klember@redhat.com> - 3.26.0-1
- Update to 3.26.0

* Thu Sep 07 2017 Kalev Lember <klember@redhat.com> - 3.25.92-1
- Update to 3.25.92

* Mon Jul 31 2017 Kalev Lember <klember@redhat.com> - 3.25.4-1
- Update to 3.25.4

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 3.25.3-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Sun Jun 25 2017 Kalev Lember <klember@redhat.com> - 3.25.3-1
- Update to 3.25.3

* Wed May 10 2017 Kalev Lember <klember@redhat.com> - 3.24.2-1
- Update to 3.24.2

* Tue Mar 21 2017 Rui Matos <rmatos@redhat.com> - 3.24.0-1
- Update to 3.24.0

* Tue Mar 14 2017 Florian Müllner <fmuellner@redhat.com> - 3.23.92-1
- Update to 3.23.92

* Fri Feb 10 2017 Fedora Release Engineering <releng@fedoraproject.org> - 3.23.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Tue Jan 31 2017 Rui Matos <rmatos@redhat.com> - 3.23.1-2
- Honor anaconda's firstboot being disabled

* Sun Oct 30 2016 Kalev Lember <klember@redhat.com> - 3.23.1-1
- Update to 3.23.1

* Wed Oct 12 2016 Kalev Lember <klember@redhat.com> - 3.22.1-1
- Update to 3.22.1

* Mon Sep 19 2016 Kalev Lember <klember@redhat.com> - 3.22.0-1
- Update to 3.22.0

* Tue Sep 13 2016 Kalev Lember <klember@redhat.com> - 3.21.92-1
- Update to 3.21.92

* Mon Sep 05 2016 Kalev Lember <klember@redhat.com> - 3.21.91-2
- Build the software sources page

* Sat Sep 03 2016 Kalev Lember <klember@redhat.com> - 3.21.91-1
- Update to 3.21.91
- Update project URL

* Wed Apr 13 2016 Kalev Lember <klember@redhat.com> - 3.20.1-1
- Update to 3.20.1

* Tue Mar 22 2016 Kalev Lember <klember@redhat.com> - 3.20.0-1
- Update to 3.20.0

* Tue Mar 15 2016 Kalev Lember <klember@redhat.com> - 3.19.92-1
- Update to 3.19.92

* Tue Mar 01 2016 Richard Hughes <rhughes@redhat.com> - 3.19.91-1
- Update to 3.19.91

* Tue Feb 16 2016 Richard Hughes <rhughes@redhat.com> - 3.19.2-1
- Update to 3.19.2

* Wed Feb 03 2016 Fedora Release Engineering <releng@fedoraproject.org> - 3.19.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Wed Oct 28 2015 Kalev Lember <klember@redhat.com> - 3.19.1-1
- Update to 3.19.1

* Mon Sep 21 2015 Kalev Lember <klember@redhat.com> - 3.18.0-1
- Update to 3.18.0

* Mon Aug 31 2015 Kalev Lember <klember@redhat.com> - 3.17.91-1
- Update to 3.17.91

* Mon Aug 17 2015 Kalev Lember <klember@redhat.com> - 3.17.90-1
- Update to 3.17.90
- Use make_install macro

* Mon Aug 17 2015 Kalev Lember <klember@redhat.com> - 3.17.4-2
- Rebuilt for libcheese soname bump

* Mon Jul 27 2015 David King <amigadave@amigadave.com> - 3.17.4-1
- Update to 3.17.4

* Wed Jul 22 2015 David King <amigadave@amigadave.com> - 3.16.3-3
- Bump for new gnome-desktop3

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.16.3-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Mon May 18 2015 Matthias Clasen <mclasen@redhat.com> - 3.16.3-1
- Update to 3.16.3

* Tue May 12 2015 Kalev Lember <kalevlember@gmail.com> - 3.16.2-1
- Update to 3.16.2

* Wed Apr 15 2015 Kalev Lember <kalevlember@gmail.com> - 3.16.1-1
- Update to 3.16.1

* Mon Mar 23 2015 Kalev Lember <kalevlember@gmail.com> - 3.16.0-1
- Update to 3.16.0

* Wed Mar 18 2015 Kalev Lember <kalevlember@gmail.com> - 3.15.92-1
- Update to 3.15.92

* Thu Mar 05 2015 Kalev Lember <kalevlember@gmail.com> - 3.15.91.1-1
- Update to 3.15.91.1

* Mon Mar 02 2015 Kalev Lember <kalevlember@gmail.com> - 3.15.91-1
- Update to 3.15.91
- Use the %%license macro for the COPYING file

* Thu Feb 19 2015 Matthias Clasen <mclasen@redhat.com> - 3.15.90.1-1
- Update to 3.15.90.1

* Tue Dec 16 2014 Rui Matos <rmatos@redhat.com> - 3.14.2.1-2
- Resolves: rhbz#1172363

* Tue Nov 11 2014 Rui Matos <rmatos@redhat.com> - 3.14.2.1-1
- Update to 3.14.2.1

* Mon Nov 10 2014 Rui Matos <rmatos@redhat.com> - 3.14.2-1
- Update to 3.14.2
- Resolves: rhbz#1158442

* Fri Oct 31 2014 Rui Matos <rmatos@redhat.com> - 3.14.1-3
- Resolves: rhbz#1151519

* Tue Oct 21 2014 Rui Matos <rmatos@redhat.com> - 3.14.1-2
- Resolves: rhbz#1154206

* Sat Oct 11 2014 Kalev Lember <kalevlember@gmail.com> - 3.14.1-1
- Update to 3.14.1

* Tue Sep 23 2014 Kalev Lember <kalevlember@gmail.com> - 3.14.0-1
- Update to 3.14.0

* Wed Sep 17 2014 Kalev Lember <kalevlember@gmail.com> - 3.13.7-1
- Update to 3.13.7

* Tue Sep 16 2014 Kalev Lember <kalevlember@gmail.com> - 3.13.6-1
- Update to 3.13.6

* Mon Sep 08 2014 Adam Williamson <awilliam@redhat.com> - 3.13.5-2
- backport upstream patch to offer full list of keyboard layouts (BGO #729208)

* Wed Sep 03 2014 Kalev Lember <kalevlember@gmail.com> - 3.13.5-1
- Update to 3.13.5

* Sat Aug 16 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.13.4-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Wed Aug 13 2014 Matthias Clasen <mclasen@redhat.com> - 3.13.4-2
- Drop the yelp focus patch (we've dropped the yelp patch it depends on)

* Fri Jul 25 2014 Kalev Lember <kalevlember@gmail.com> - 3.13.4-1
- Update to 3.13.4

* Thu Jul 24 2014 Matthias Clasen <mclasen@redhat.com> - 3.12.1-3
- Fix a memory corruption crash (#1116478)

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.12.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Thu May 15 2014 Kalev Lember <kalevlember@gmail.com> - 3.12.1-1
- Update to 3.12.1

* Tue Mar 25 2014 Kalev Lember <kalevlember@gmail.com> - 3.12.0-1
- Update to 3.12.0

* Thu Mar 20 2014 Richard Hughes <rhughes@redhat.com> - 3.11.92-1
- Update to 3.11.92

* Sat Mar 08 2014 Richard Hughes <rhughes@redhat.com> - 3.11.91-1
- Update to 3.11.91

* Fri Feb 28 2014 Richard Hughes <rhughes@redhat.com> - 3.11.90-1
- Update to 3.11.90

* Wed Feb 19 2014 Kalev Lember <kalevlember@gmail.com> - 3.10.1.1-5
- Rebuilt for libgnome-desktop soname bump

* Fri Nov 29 2013 Rui Matos <rmatos@redhat.com> - 3.10.1.1-4
- Resolves: rhbz#1035548 - Disables the GOA page in new user mode

* Thu Nov 28 2013 Rui Matos <rmatos@redhat.com> - 3.10.1.1-3
- Resolves: rhbz#1027507 - [abrt] gnome-initial-setup-3.10.1.1-2.fc20: magazine_chain_pop_head

* Fri Nov  1 2013 Matthias Clasen <mclasen@redhat.com> - 3.10.1.1-2
- Fix goa add dialog to not be empty

* Mon Oct 28 2013 Richard Hughes <rhughes@redhat.com> - 3.10.1.1-1
- Update to 3.10.1.1

* Thu Sep 26 2013 Kalev Lember <kalevlember@gmail.com> - 3.10.0.1-1
- Update to 3.10.0.1

* Wed Sep 25 2013 Kalev Lember <kalevlember@gmail.com> - 3.10.0-1
- Update to 3.10.0

* Tue Sep 03 2013 Kalev Lember <kalevlember@gmail.com> - 0.12-7
- Rebuilt for libgnome-desktop soname bump

* Fri Aug 23 2013 Kalev Lember <kalevlember@gmail.com> - 0.12-6
- Rebuilt for gnome-online-accounts soname bump

* Fri Aug 09 2013 Kalev Lember <kalevlember@gmail.com> - 0.12-5
- Rebuilt for cogl 1.15.4 soname bump

* Tue Aug 06 2013 Adam Williamson <awilliam@redhat.com> - 0.12-4
- rebuild for new libgweather

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.12-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Fri Jun 21 2013 Kalev Lember <kalevlember@gmail.com> - 0.12-2
- Rebuilt for libgweather 3.9.3 soname bump

* Mon Jun 17 2013 Rui Matos <rmatos@redhat.com> - 0.12-1
- Update to 0.12

* Fri Jun  7 2013 Matthias Clasen <mclasen@redhat.com> - 0.11-2
- Require polkit-js-engine

* Tue May 28 2013 Matthias Clasen <mclasen@redhat.com> - 0.11-1
- Update to 0.11

* Tue May 14 2013 Rui Matos <rmatos@redhat.com> - 0.10-1
- Update to 0.10
- Add BuildRequires on polkit-devel
- Update files list

* Thu May  2 2013 Rui Matos <rmatos@redhat.com> - 0.9-2
- Remove unused patches
- Add build requires for ibus

* Tue Apr 16 2013 Matthias Clasen <mclasen@redhat.com> - 0.9-1
- Update to 0.9

* Tue Apr 16 2013 Ray Strode <rstrode@redhat.com> 0.8-4
- Add requires for keyboard viewer app

* Wed Mar 20 2013 Ray Strode <rstrode@redhat.com> 0.8-3
- Add cosimoc fix for gd page transitions

* Wed Mar 20 2013 Ray Strode <rstrode@redhat.com> 0.8-2
- Disable gd page transitions for now since they don't
  completely work right (ask adamw).
- Fix crasher when realmd goes away

* Tue Mar 19 2013 Matthias Clasen <mclasen@redhat.com> - 0.8-1
- Update to 0.8

* Tue Mar 12 2013 Matthias Clasen <mclasen@redhat.com> - 0.7-1
- Update to 0.7

* Thu Feb 21 2013 Kalev Lember <kalevlember@gmail.com> - 0.6-4
- Rebuilt for cogl soname bump

* Wed Feb 20 2013 Kalev Lember <kalevlember@gmail.com> - 0.6-3
- Rebuilt for libgnome-desktop soname bump

* Fri Jan 25 2013 Peter Robinson <pbrobinson@fedoraproject.org> 0.6-2
- Rebuild for new cogl

* Wed Jan 16 2013 Matthias Clasen <mclasen@redhat.com> - 0.6-1
- 0.6

* Fri Jan 11 2013 Matthias Clasen <mclasen@redhat.com> - 0.5-1
- 0.5

* Fri Dec 21 2012 Kalev Lember <kalevlember@gmail.com> - 0.4-2
- Rebuilt for libgweather soname bump

* Thu Nov 22 2012 Matthias Clasen <mclasen@redhat.com> - 0.4-1
- 0.4

* Fri Oct 26 2012 Jasper St. Pierre <jstpierre@mecheye.net> - 0.3-3
- Add krb5

* Fri Oct 26 2012 Jasper St. Pierre <jstpierre@mecheye.net> - 0.3-2
- 0.3-2

* Thu Oct 18 2012 Matthias Clsaen <mclasen@redhat.com> - 0.3-1
- 0.3

* Fri Sep 14 2012 Matthias Clasen <mclasen@redhat.com> - 0.2-2
- Add Requires: gdm

* Wed Aug 29 2012 Jasper St. Pierre <jstpierre@mecheye.net> - 0.2-1
- Update to 0.2

* Fri Jun 08 2012 Jasper St. Pierre <jstpierre@mecheye.net> - 0.1
- Initial packaging.
