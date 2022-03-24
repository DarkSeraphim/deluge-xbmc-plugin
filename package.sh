rm plugin.program.deluge.zip
rm /mnt/d/plugin.program.deluge-*.zip
zip -r plugin.program.deluge.zip plugin.program.deluge/
h=$(sha256sum plugin.program.deluge.zip | awk '{print $1}')
    
cp plugin.program.deluge.zip /mnt/d/plugin.program.deluge-$h.zip
