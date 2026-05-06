#!/bin/bash

pthtop="$(cd "$(dirname "${0}")/../../../.." && pwd)"
source "${pthtop}"/manage/lib/params.sh
source "${pthtop}"/manage/lib/shared.sh
source "${pthcrr}"/params.sh

pthkey="${HOME}"/sec/key/.envath_oai.txt

if test ! -e "${pthkey}"
then
  cnfrtn "manual: ${pthkey}: OPENAI_API_KEY=XXX"
fi
addimg ${imgtgt} "${cnfimg}" "${pthdoc}"
