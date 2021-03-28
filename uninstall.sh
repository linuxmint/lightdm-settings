#!/bin/bash

[ -f /usr/bin/lightdm-settings ] && sudo rm /usr/bin/lightdm-settings
[ -d /usr/lib/lightdm-settings ] && sudo rm -r /usr/lib/lightdm-settings
[ -f /usr/share/applications/lightdm-settings.desktop ] && sudo rm /usr/share/applications/lightdm-settings.desktop

FILES=$(sudo find /usr/share/ -iname "*lightdm-settings*")
for FILE in $FILES; do
   sudo rm $FILE
done

echo "Done"
exit 0
