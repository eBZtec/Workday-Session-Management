Name:           wsm-venv
Version:        1.0
Release:        0%{?dist}
Summary:        Workday Session Management Installation Package

License:        GPL-3.0
URL:            https://github.com/Workday_Session_Management
Source0:        %{name}-%{version}.tar.gz

BuildRequires:  git, python3.12, gcc, tar, rsync, wget, curl
Requires:       wsm, tar, postgresql-contrib, rabbitmq-server, brotli, libbrotli, python3.12, python3.12-pip

%description
Pre-installed python virtualenv for Workday Session Management (WSM).

%pre
# nothing needed

%prep
mkdir -p %{buildroot}/opt/wsm
cd %{buildroot}/opt/wsm
curl -o requirements.txt http://gitea.ebz:3000/eBZ/Workday_Session_Management/raw/branch/main/requirements.txt
chroot %{buildroot}
cd %{buildroot}/opt/wsm
/usr/bin/python3.12 -m venv %{buildroot}/opt/wsm/wsmvenv3.12
%{buildroot}/opt/wsm/wsmvenv3.12/bin/pip install --upgrade pip 
%{buildroot}/opt/wsm/wsmvenv3.12/bin/pip install -r %{buildroot}/opt/wsm/requirements.txt

%build
# nothing needed

%install
chown -R wsm:wsm /opt/wsm/wsmvenv3.12

%files
/opt/wsm/wsmvenv3.12
