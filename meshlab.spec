Summary:	A system for processing and editing unstructured 3D triangular meshes
Name:		meshlab
Version:	1.3.2
Release:	0.1
License:	GPL v2+ and BSD and Public Domain
Group:		Applications/Multimedia
URL:		http://meshlab.sourceforge.net/
Source0:	http://downloads.sourceforge.net/meshlab/MeshLabSrc_AllInc_v132.tgz
# Source0-md5:	3cba61f6d34559f98129d9d0a3126f81
Source1:	%{name}-48x48.xpm
# Meshlab v131 tarball is missing the docs directory. Reported upstream,
# but for now we'll extract them from the v122 tarball.
Source2:	http://downloads.sourceforge.net/meshlab/MeshLabSrc_v122.tar.gz
# Source2-md5:	f06107dd01cbe0d6519dbb759ae84c11
Patch0:		%{name}-1.3.2-sharedlib.patch
Patch1:		%{name}-1.3.2-plugin-path.patch
Patch2:		%{name}-1.3.2-shader-path.patch
Patch3:		%{name}-1.3.2-cstddef.patch
Patch4:		%{name}-1.3.1-ply-numeric.patch
Patch5:		%{name}-1.3.1-glu.patch
Patch6:		%{name}-1.3.2-noctm.patch
Patch9:		%{name}-1.3.2-vert-swap.patch
Patch10:	%{name}-1.3.2-gcc47.patch
Patch11:	%{name}-1.3.2-include-path-double-slash.patch
BuildRequires:	ImageMagick
BuildRequires:	bzip2-devel
BuildRequires:	chrpath
BuildRequires:	desktop-file-utils
BuildRequires:	glew-devel
BuildRequires:	levmar-devel
BuildRequires:	lib3ds-devel
BuildRequires:	muparser-devel
BuildRequires:	qhull-devel
BuildRequires:	qt-devel
BuildRequires:	qtsoap-devel
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
MeshLab is an open source, portable, and extensible system for the
processing and editing of unstructured 3D triangular meshes. The
system is aimed to help the processing of the typical not-so-small
unstructured models arising in 3D scanning, providing a set of tools
for editing, cleaning, healing, inspecting, rendering and converting
these kinds of meshes.

%prep
%setup -q -c %{name}-%{version}

# get the missing docs directory from the old tarball
%setup -q -T -D -a 2

mv meshlab-snapshot-svn3524/meshlab/docs meshlab/docs
rm -rf meshlab-snapshot-svn3524

%patch0 -P 0 -p1
%patch0 -P 1 -p1
%patch0 -P 2 -p1
%patch0 -P 3 -p1
%patch0 -P 4 -p1
%patch0 -P 5 -p1
%patch0 -P 6 -p1
%patch0 -P 9 -p1
%patch0 -P 10 -p1
%patch0 -P 11 -p1

# Turn of execute permissions on source files to avoid rpmlint
# errors and warnings for the debuginfo package
find . \( -name *.h -o -name *.cpp -o -name *.inl \) -a -executable \
	-exec chmod -x {} \;

# Remove bundled library sources, since we use the Fedora packaged libraries
rm -rf vcglib/wrap/system
rm -rf meshlab/src/external/{ann*,bzip2*,glew*,levmar*,lib3ds*,muparser*,ode*,qhull*,qtsoap*}

%build
# Build instructions from the wiki:
#   http://meshlab.sourceforge.net/wiki/index.php/Compiling_V122
# Note that the build instructions in README.linux are out of date.

cd meshlab/src/external
qmake-qt4 -recursive external.pro
# Note: -fPIC added to make jhead link properly; don't know why this wasn't
# also an issue with structuresynth
%{__make} \
	CFLAGS="%{optflags} -fPIC"
cd ..
qmake-qt4 -recursive meshlab_full.pro
%{__make} \
	CFLAGS="%{optflags}" \
	DEFINES="-D__DISABLE_AUTO_STATS__ -DPLUGIN_DIR=\\\"%{_libdir}/%{name}\\\""

# process icon
convert %{SOURCE1} meshlab.png

# create desktop file
cat <<EOF >meshlab.desktop
[Desktop Entry]
Name=meshlab
GenericName=MeshLab 3D triangular mesh processing and editing
Exec=meshlab
Icon=meshlab
Terminal=false
Type=Application
Categories=Graphics;
EOF

# convert doc files from ISO-8859-1 to UTF-8 encoding:
cd ../docs
for f in contrib_Gangemi_Vannini.txt contrib_Buzzelli_Mazzanti.txt; do
	iconv -fiso88591 -tutf8 $f >$f.new
	touch -r $f $f.new
	mv $f.new $f
done

# The QMAKE_RPATHDIR stuff puts in the path to the compile-time location
# of libcommon, which won't work at runtime, so we change the rpath here.
# The use of rpath will cause an rpmlint error, but the Fedora Packaging
# Guidelines specifically allow use of an rpath for internal libraries:
# http://fedoraproject.org/wiki/Packaging:Guidelines#Rpath_for_Internal_Libraries
# Ideally upstream would rename the library to libmeshlab, libmeshlabcommon,
# or the like, so that we could put it in the system library directory
# and avoid rpath entirely.
chrpath -r %{_libdir}/meshlab meshlab/src/distrib/{meshlab,meshlabserver}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_bindir},%{_mandir}/man1,%{_pixmapsdir},%{_desktopdir}} \
	$RPM_BUILD_ROOT%{_libdir}/meshlab/plugins \
	$RPM_BUILD_ROOT%{_datadir}/meshlab/{shaders/shadersrm,textures}

cd meshlab

install -p src/distrib/{meshlab,meshlabserver} $RPM_BUILD_ROOT%{_bindir}
cp -p docs/{meshlab.1,meshlabserver.1} $RPM_BUILD_ROOT%{_mandir}/man1

install -p src/distrib/libcommon.so.1.0.0 $RPM_BUILD_ROOT%{_libdir}/meshlab
ln -s libcommon.so.1.0.0 $RPM_BUILD_ROOT%{_libdir}/meshlab/libcommon.so.1.0
ln -s libcommon.so.1.0.0 $RPM_BUILD_ROOT%{_libdir}/meshlab/libcommon.so.1
ln -s libcommon.so.1.0.0 $RPM_BUILD_ROOT%{_libdir}/meshlab/libcommon.so

install -p src/distrib/plugins/*.so $RPM_BUILD_ROOT%{_libdir}/meshlab/plugins
cp -p src/distrib/shaders/*.{frag,gdp,vert} $RPM_BUILD_ROOT%{_datadir}/meshlab/shaders
cp -p src/distrib/shaders/shadersrm/*.rfx $RPM_BUILD_ROOT%{_datadir}/meshlab/shaders/shadersrm
cp -p src/meshlab.png $RPM_BUILD_ROOT%{_pixmapsdir}
cp -p src/meshlab.desktop $RPM_BUILD_ROOT%{_desktopdir}
desktop-file-validate $RPM_BUILD_ROOT%{_desktopdir}/meshlab.desktop

%clean
rm -rf $RPM_BUILD_ROOT

%post	-p /sbin/ldconfig
%postun	-p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%doc meshlab/docs/contrib_Buzzelli_Mazzanti.txt
%doc meshlab/docs/contrib_Gangemi_Vannini.txt
%doc meshlab/docs/contrib_Latronico_Venturi.txt
%doc meshlab/docs/contrib_Mochi_Portelli_Vacca.txt
%doc meshlab/docs/gpl.txt
%doc meshlab/docs/history.txt
%doc meshlab/docs/privacy.txt
%doc meshlab/docs/README.linux
%doc meshlab/docs/readme.txt
%doc meshlab/docs/ToDo.txt
%doc meshlab/src/distrib/shaders/3Dlabs-license.txt
%doc meshlab/src/distrib/shaders/LightworkDesign-license.txt
%doc meshlab/src/meshlabplugins/filter_poisson/license.txt
%attr(755,root,root) %{_bindir}/meshlab
%attr(755,root,root) %{_bindir}/meshlabserver
%{_libdir}/meshlab
%{_datadir}/meshlab
%{_mandir}/man1/*.1*
%{_desktopdir}/meshlab.desktop
%{_pixmapsdir}/meshlab.png
