#!/usr/bin/env bash

ISS_TEMPLATE="../Benedat2_instalator/Benedat2_instalator.template.iss"
ISS_FILE="../Benedat2_instalator/Benedat2_instalator.iss"

if (( $# < 3 )); then
  echo "usage: $0 APPNAME VERSION BUILD"
  exit 1
fi
APPNAME=${1}
VERSION=${2}
BUILD=${3}

echo
echo "APPNAME=${APPNAME}"
echo "VERSION=${VERSION}"
echo "BUILD=${BUILD}"
echo
echo
echo

cat ${ISS_TEMPLATE} | sed "s|APPNAME|${APPNAME}|" | \
                      sed "s|VERSION|${VERSION}|" | \
                      sed "s|BUILD|${BUILD}|" > ${ISS_FILE}


wine /home/dahorak/.wine/drive_c/InnoSetup5/Compil32.exe /cc \
  "H:\Personal\programovani\Benedat2_instalator\Benedat2_instalator.iss"

