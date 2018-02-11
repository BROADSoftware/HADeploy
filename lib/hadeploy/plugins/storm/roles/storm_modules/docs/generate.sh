
ansible-doc -M ../library/ storm_topology 2>/dev/null | sed 's/[(].*storm_modules[/]library.*[)]//' >storm_topology.txt
