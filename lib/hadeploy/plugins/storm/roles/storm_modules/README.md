# storm_modules

This ansible role host a module aimed to manage topology lifecycle using Storm UI REST API

[Parameters reference here](./docs/storm_topology.txt)

## Requirements

These modules need the `python-requests` package to be present on the remote node.

To be able to access kerberos protected cluster, `python-requests-kerberos` is also required 

# Example Playbook

The following example kill all topologies defined in a list.
	
	- hosts: en1
	  vars:
	    topologies:
	    - { name: "storm1", wt: 10 }
	    - { name: "storm2", wt: 12 }
	    - { name: "storm3", wt: 10 }
	  
	  roles:
	  - storm_modules
	  tasks:
	  
	  - name: Kill
	    storm_topology:
	      ui_url: http://en1.mycluster.com:8744/
	      name: "{{item.name}}"
	      state: killed
	      wait_time_secs: "{{item.wt}}"
	      timeout_secs: 20
	    with_items: "{{ topologies }}"
	    
	  - name: And wait
	    storm_topology:
	      ui_url: http://en1.mycluster.com:8744/
	      name: "{{item.name}}"
	      state: nonexistent
	      wait_time_secs: "{{item.wt}}"
	      timeout_secs: 20
	    with_items: "{{ topologies }}"
	    
Note we first set all topologies in `killed` state, then we wait for the kill to be completed (state `nonexistent`). 

Doing this way allow to shutdown all topologies in parallel, thus reducing drastically shutdown duration.	  

# License

GNU GPL

Click on the [Link](COPYING) to see the full text.

