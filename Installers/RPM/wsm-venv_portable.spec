Name:           wsm-venv_portable
Version:        1.0
Release:        1%{?dist}
Summary:        Workday Session Management Installation Package - Portable

License:        GPL-3.0
URL:            https://github.com/Workday_Session_Management
Source1:        requirements.txt

BuildRequires:  python3.12, python3.12-pip
Requires:       python3.12

# Prevent RPM from scanning the venv for binary dependencies
%global __requires_exclude_from ^/opt/wsm/wsmvenv3.12/.*$

%description
A relocatable Python 3.12 virtual environment pre-installed with WSM dependencies.

%prep
# No Source0 needed

%build
# Create venv in current build dir
python3.12 -m venv wsmvenv3.12

rm wsmvenv3.12/bin/python3.12
ln -s /usr/bin/python3.12 wsmvenv3.12/bin/python3.12

# Install dependencies (offline or wheel support possible)
wsmvenv3.12/bin/pip install --upgrade pip --no-cache-dir
wsmvenv3.12/bin/pip install -r %{SOURCE1} --no-cache-dir --no-compile

# Strip pip/setuptools/wheel if you don't need them at runtime
rm -rf wsmvenv3.12/lib/python3.12/site-packages/pip*
rm -rf wsmvenv3.12/lib/python3.12/site-packages/setuptools*
rm -rf wsmvenv3.12/lib/python3.12/site-packages/wheel*
rm -rf wsmvenv3.12/lib/python3.12/site-packages/__pycache__

# Fix shebangs (important for relocatability)
find wsmvenv3.12/bin -type f -exec sed -i '1s|^#!.*/python.*|#!/usr/bin/env python3.12|' {} +

%install
mkdir -p %{buildroot}/opt/wsm
cp -a wsmvenv3.12 %{buildroot}/opt/wsm/

%files
/opt/wsm/wsmvenv3.12

%changelog
* Wed Apr 16 2025 Jean Michel <jean.michel@ebz.tec.br> - 1.0-1
- Initial portable Python venv packaging
* Wed Apr 16 2025 Jean Michel <jean.michel@ebz.tec.br> - 1.0-0
- Initial packaging