 _____              _    _                 _ _           
|  __ \            | |  | |               | | |          
| |  | |_ __  ___  | |__| | __ _ _ __   __| | | ___ _ __ 
| |  | | '_ \/ __| |  __  |/ _` | '_ \ / _` | |/ _ \ '__|
| |__| | | | \__ \ | |  | | (_| | | | | (_| | |  __/ |   
|_____/|_| |_|___/ |_|  |_|\__,_|_| |_|\__,_|_|\___|_|   

this a python module for handling DNS basic operations:
usage is simple:

 1. DNS secret key:
--------------
first of all: add your DNS secret key file under the name /etc/bind/keys
file content of this kind:

    key "my-key" {
            algorithm hmac-md5;
            secret "QJc08cnP1xkoF4a/eSZZbw==";
    };


 2. add DNS entry:
--------------

to add a dns entry; A (direct) and PTR (reverse) types:

    from dnshandler import dns
          
    print dns.add_entry("mydomain", "machine1", "10.1.0.4", "dns.mydomain")

 3. delete DNS entry:
--------------
to delete a dns entry; A (direct) and PTR (reverse) types:

    print dns.delete_entry("test", "machine2", "10.2.0.4")


 3. basic DNS lookups:
--------------

    print dns.get_address("machine1.mydomain")
    print dns.get_host("10.2.0.4")

