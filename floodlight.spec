Name:           floodlight
Version:        0.90
Release:        1%{?dist}
Summary:        High performance Java based OpenFlow network controller
License:        ASL 2.0
URL:            http://floodlight.openflowhub.org/
Source0:        http://floodlight.openflowhub.org/files/floodlight-source-%{version}.tar.gz
Source1:        floodlight.logrotate
Source2:        floodlight.service
Source3:        floodlight.sysconf
Source4:        floodlight.logback.xml
Patch0:         floodlight.system-jars.patch
BuildArch:	noarch

BuildRequires:  java-devel
BuildRequires:  jpackage-utils
BuildRequires:  ant
BuildRequires:  jython
BuildRequires:  antlr3-java
BuildRequires:  args4j
BuildRequires:  easymock
BuildRequires:  jackson
BuildRequires:  logback
BuildRequires:  netty
BuildRequires:  slf4j
# For concurrentlinkedhashmap see:
#   https://bugzilla.redhat.com/show_bug.cgi?id=865890
BuildRequires: 	concurrentlinkedhashmap-lru
# For thrift see:
#   https://bugzilla.redhat.com/show_bug.cgi?id=861783
BuildRequires:  thrift
BuildRequires:  java-libthrift
#BuildRequires:  restlet

Requires:       java
Requires:       jpackage-utils
Requires:       jython
Requires: 	antlr3-java
Requires: 	args4j
Requires: 	easymock
Requires: 	jackson
Requires: 	logback
Requires: 	netty
Requires: 	slf4j
Requires: 	concurrentlinkedhashmap-lru
Requires:	java-libthrift
#Requires:	restlet

Requires(pre): /usr/sbin/useradd
Requires(preun): systemd-units
Requires(postun): systemd-units
Requires(post): systemd-units

%description
Floodlight is a high performance Java based OpenFlow controller originally
written by David Erickson at Stanford University.

Floodlight supports a broad range of virtual and physical OpenFlow switches
and has rich support for mixed OpenFlow and non-OpenFlow networks supporting
management of multiple islands of OpenFlow switches.

%package javadoc
Summary:        Javadocs for %{name}
Group:          Documentation
Requires:       jpackage-utils

%description javadoc
This package contains the API documentation for %{name}

%prep
%setup -q
%patch0

# Remove bundled jars
find -name '*.class' -exec rm -f '{}' \;
find -name '*.jar' -exec rm -f '{}' \;

%build
export CLASSPATH=$(build-classpath logback/logback-classic.jar logback/logback-core.jar jackson/jackson-core-asl.jar jackson/jackson-mapper-asl.jar slf4j/api.jar restlet/restlet.jar restlet/jackson.jar restlet/simple.jar restlet/slf4j.jar slf4j/simple.jar netty.jar args4j.jar concurrentlinkedhashmap-lru.jar jython.jar libthrift.jar)
ant gen-thrift
ant
ant javadoc

%install
rm -rf %{buildroot}
install -d -m 755 %{buildroot}%{_bindir}/
%jpackage_script net.floodlightcontroller.core.Main "" "-Dpython.home=/usr/share/jython" floodlight floodlight true
install -d -m 755 %{buildroot}%{_javadir}/
cp -p target/floodlight.jar %{buildroot}%{_javadir}/

# Documentation
install -d -m 755 %{buildroot}%{_javadocdir}/%{name}/
cp -rp target/docs/ %{buildroot}%{_javadocdir}/%{name}/

# Install logrotate config
mkdir -p %{buildroot}/etc/logrotate.d
install -m 644 -p $RPM_SOURCE_DIR/floodlight.logrotate \
	%{buildroot}/etc/logrotate.d/floodlight

# Install systemd service files
mkdir -p %{buildroot}%{_unitdir}
install -p -m 644 $RPM_SOURCE_DIR/floodlight.service \
        %{buildroot}%{_unitdir}/floodlight.service

mkdir %{buildroot}%{_sysconfdir}/sysconfig
install -m 644 -p $RPM_SOURCE_DIR/floodlight.sysconf \
        %{buildroot}%{_sysconfdir}/sysconfig/floodlight


%files
%defattr(-,root,root)
%{_bindir}/*
%{_javadir}/*
%doc README.txt LICENSE.txt NOTICE.txt

%config(noreplace) %{_sysconfdir}/logrotate.d/floodlight
%config(noreplace) %{_sysconfdir}/sysconfig/floodlight

%{_unitdir}/*.service

%files javadoc
%defattr(-,root,root)
%{_javadocdir}/%{name}

%pre
# Add the "floodlight" user
/usr/sbin/useradd -c "Floodlight" \
	-s /sbin/nologin -r floodlight 2> /dev/null || :

%post
%systemd_post floodlight.service

%preun
%systemd_preun floodlight.service

%postun
%systemd_postun

%clean
rm -rf %{buildroot}

%changelog
* Fri Jan 04 2012 Sander Striker <s.striker@striker.nl> 0.90-1
- Initial RPM release
