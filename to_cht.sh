#!/bin/bash

if [[ $# -lt 1 ]]; then
    echo "Usage: $0 input-directory" >&2
    exit 1
fi

if [ ! -d "$1" ]; then
    echo "$1 is not a directory"
    exit 1
fi

pushd "$1"

for text_file in *; do
    mime_encoding="$(file -b --mime-encoding "${text_file}")"
    if [[ "${mime_encoding}" != utf-8 ]]; then
        echo "the encoding of "${text_file}" is "${mime_encoding}""
        tmp="iconv-utf8-${text_file}"
        iconv -f "${mime_encoding}" -t UTF-8 "${text_file}" >"${tmp}"
        echo "$(cat "${tmp}")"
        read -p "[iconv] Are the contents as expected?" yn
        case $yn in
        [Yy]*) mv "${tmp}" "${text_file}" ;;
        [Nn]*) rm "${tmp}" ;;
        *) echo "Please answer yes or no." ;;
        esac
    fi
    tmp="opencc-convert-${text_file}"
    opencc -i "${text_file}" -o "${tmp}" -c s2twp.json
    echo "$(cat "${tmp}")"
    read -p "[opencc] Are the contents as expected?" yn
    case $yn in
    [Yy]*) mv "${tmp}" "${text_file}" ;;
    [Nn]*) rm "${tmp}" ;;
    *) echo "Please answer yes or no" ;;
    esac
done

popd
