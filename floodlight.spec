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
Source5:        floodlight.1
Patch0:         floodlight.system-jars.patch
BuildArch:      noarch

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
BuildRequires:  concurrentlinkedhashmap-lru
BuildRequires:  thrift
BuildRequires:  java-libthrift
#BuildRequires:  restlet

Requires:       java
Requires:       jpackage-utils
Requires:       jython
Requires:       antlr3-java
Requires:       args4j
Requires:       easymock
Requires:       jackson
Requires:       logback
Requires:       netty
Requires:       slf4j
Requires:       concurrentlinkedhashmap-lru
Requires:       java-libthrift
#Requires:       restlet

Requires(pre): shadow-utils
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
%jpackage_script net.floodlightcontroller.core.Main "" "-Dpython.home=/usr/share/jython" .:floodlight:logback/logback-classic:logback/logback-core:jackson/jackson-core-asl:jackson/jackson-mapper-asl:slf4j/api:restlet/restlet:restlet/jackson:restlet/simple:restlet/slf4j:slf4j/simple:netty:args4j:concurrentlinkedhashmap-lru:jython:libthrift floodlight true
install -d -m 755 %{buildroot}%{_javadir}/
cp -p target/floodlight.jar %{buildroot}%{_javadir}/

# Documentation
mkdir -p %{buildroot}%{_mandir}/man1/
install -m 644 %{SOURCE5} %{buildroot}%{_mandir}/man1/
install -d -m 755 %{buildroot}%{_javadocdir}/%{name}/
cp -rp target/docs/ %{buildroot}%{_javadocdir}/%{name}/

# Install logback config
mkdir -p %{buildroot}%{_sysconfdir}/floodlight
install -m 644 -p %{SOURCE4} \
        %{buildroot}%{_sysconfdir}/floodlight/logback.xml

# Install logrotate config
mkdir -p %{buildroot}%{_sysconfdir}/logrotate.d
install -m 644 -p %{SOURCE1} \
        %{buildroot}%{_sysconfdir}/logrotate.d/floodlight

# Install systemd service files
mkdir -p %{buildroot}%{_unitdir}
install -p -m 644 %{SOURCE2} \
        %{buildroot}%{_unitdir}/floodlight.service

mkdir %{buildroot}%{_sysconfdir}/sysconfig
install -m 644 -p %{SOURCE3} \
        %{buildroot}%{_sysconfdir}/sysconfig/floodlight

%pre
getent group floodlight >/dev/null || groupadd -r floodlight
getent passwd floodlight >/dev/null || \
    useradd -r -g floodlight -d %{_sysconfdir}/floodlight -s /sbin/nologin \
    -c "Floodlight daemon" floodlight
exit 0

%post
if [ $1 -eq 1 ] ; then
        # Initial installation
#        /bin/systemctl daemon-reload >/dev/null 2&1 || :
        /bin/systemctl enable floodlight.service >/dev/null 2>&1 || :
fi

%preun
if [ $1 -eq 0 ] ; then
        # Package removal, not upgrade
        /bin/systemctl --no-reload disable floodlight.service >/dev/null 2>&1 || :
        /bin/systemctl stop floodlight.service >/dev/null 2>&1 || :
fi

%postun
/bin/systemctl daemon-reload >/dev/null 2&1 || :
if [ $1 -ge 1 ] ; then
        # Package upgrade, not uninstall
        /bin/systemctl try-restart floodlight.service >/dev/null 2>&1 || :
fi

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%{_bindir}/*
%{_mandir}/man1/*
%{_javadir}/*
%doc README.txt LICENSE.txt NOTICE.txt

%config(noreplace) %{_sysconfdir}/logrotate.d/floodlight
%config(noreplace) %{_sysconfdir}/sysconfig/floodlight
%config(noreplace) %{_sysconfdir}/floodlight/logback.xml

%{_unitdir}/*.service

%files javadoc
%defattr(-,root,root)
%{_javadocdir}/%{name}

%changelog
* Fri Jan 04 2012 Sander Striker <s.striker@striker.nl> 0.90-1
- Initial RPM release
