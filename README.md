pythondo
========

What is it?
-----------

PythonDo is a Perl module (PythonDo.pm) and a Python script (pydo.py) that work together to allow one to instantiate an instance of a python class from within a Perl script.

How does it work?
-----------------

It works under the same idea of an API where the Perl Module will execute the python script, passing arguments a JSON string and expecting a JSON string reply. Instances are pickled and stored in a file, returning to the Perl module an instance-id to be used in subsequent calls to instance methods.

From the perl script's perspective, new() returns a blessed object which inherits the methods and properties of the python class.

Methods are called like a normal perl method:

$plobj->doCoolStuff('bacon')

Properties/Attributes/etc, however, must be set/get as methods.

e.g.

wrong

 my $food = $plobj->{'food'};
 $plobj->{'food'} = 'bacon';

right

 my $food = $plobj->food;
 $plobj->food('bacon');

Usage
-----

script:

#!/usr/bin/env perl

use PythonDo;

my $devname = 'myswitch.net.com';
my $cmd = 'show version';

my $do = new PythonDo({'class'=>'docommand.do.Do','args'=>{'devices'=>[$devname],'commands'=>[$cmd]}});
$do->run();
my $data = $do->data;
foreach my $dev (keys(%$data)) {
    print "# $dev #\n";
    foreach my $cmdout (@{$data->{$dev}}) {
        my $cmd = $cmdout->{'cmd'};
        my $out = $cmdout->{'out'};
        print "$dev> $cmd\n";
        print $out;
        print "\n";
    }
}

Result:

# myswitch.net.com #
myswitch.net.com> show version
  SW: Version 03.2.00jT1e0 Copyright (c) 1996-2006 Foundry Networks, Inc.
      Compiled on Feb 07 2008 at 15:03:54 labeled as FWXS03200j
      (2313150 bytes) from Primary \NetResources\FWXS03200j.bin
      BootROM: Version 03.0.01T1e5 (FEv2)
  HW: Stackable FWSX448
==========================================================================
      Serial  #: FL04060573
      P-ASIC  0: type 00D1, rev D2
      P-ASIC  1: type 00D1, rev D2
      P-ASIC  2: type 00D1, rev D2
      P-ASIC  3: type 00D1, rev D2
==========================================================================
  300 MHz Power PC processor 8245 (version 129/1014) 66 MHz bus
  512 KB boot flash memory
16384 KB code flash memory
  128 MB DRAM
The system uptime is 520 days 7 hours 22 minutes 36 seconds 
The system started at 08:27:14 GMT+00 Mon Nov 30 2009

The system : started=cold start   

Breakdown
---------

my $do = new PythonDo({'lib'=>'/usr/local/lib/py','class'=>'docommand.do.Do','args'=>{'debug':\0,'devices'=>['myswitch.net.com'],'commands'=>['show version']}});

executes: /usr/local/bin/pydo.py '{"lib":"/usr/local/lib/py","class":"docommand.do.Do","method":"new","args":{"debug":false,"commands":["show version"],"devices":["myswitch.net.com"]},"action":"method"}'

implements:

import sys
sys.path.append("/usr/local/lib/py")
import docommand.do
n = docommand.do.Do(debug=False,commands=["show version"],devices=["myswitch.net.com"])
with open('/tmp.pydo.'+instid+'.data','w') as fw:
  pickle.dump(n,fw,-1)

reply:

    {

        "stat": "ok", 
        "data": true, 
        "instid": "a682645da85e79e4", 
        "methods": [

            "generate_ios_cmd", 
            "run", 
            "eb", 
            "ios_parse", 
            "junos_parse", 
            "set_data", 
            "generate_junos_cmd" 

        ] 

    } 

$do->run();

executes: /usr/local/bin/pydo.py '{"instid":"a682645da85e79e4","class":"docommand.do.Do","method":"run","args":[],"action":"method"}'

implements:

import pickle
with open('/tmp.pydo.'+instid+'.data','w') as fw:
  n = pickle.load(fr)
retval = n.run()

reply:

    {

        "stat": "ok", 
        "instid": "a682645da85e79e4", 
        "data": null 

    } 

my $data = $do->data;

executes: /usr/local/bin/pydo.py '{"instid":"a682645da85e79e4","class":"docommand.do.Do","action":"get","prop":"data","method":"DUMMY"}'

implements:

import pickle
with open('tmp'+instid,'w') as fw:
  n = pickle.load(fr)
retval = n.data

reply:

    {

        "instid": "a682645da85e79e4", 
        "stat": "ok", 
        "data": {

            "myswitch.net.com": [

                {

                    "cmd": "show version", 
                    "dev": "myswitch.net.com", 
                    "out": " SW: Version 03.2.00jT1e0 Copyright (c) 1996-2006 Foundry Networks, Inc.\n Compiled on Feb 07 2008 at 15:03:54 labeled as FWXS03200j\n (2313150 bytes) from Primary \\NetResources\\FWXS03200j.bin\n BootROM: Version 03.0.01T1e5 (FEv2)\n HW: Stackable FWSX448\n==========================================================================\n Serial #: FL04060573\n P-ASIC 0: type 00D1, rev D2\n P-ASIC 1: type 00D1, rev D2\n P-ASIC 2: type 00D1, rev D2\n P-ASIC 3: type 00D1, rev D2\n==========================================================================\n 300 MHz Power PC processor 8245 (version 129/1014) 66 MHz bus\n 512 KB boot flash memory\n16384 KB code flash memory\n 128 MB DRAM\nThe system uptime is 520 days 7 hours 22 minutes 36 seconds \nThe system started at 08:27:14 GMT+00 Mon Nov 30 2009\n\nThe system : started=cold start \n\n" 

                } 

            ] 

        } 

    } 

On Perl exit:

    (this automatically deletes the pickle file that holds the instance data) 

executes: /usr/local/bin/pydo.py '{"instid":"a682645da85e79e4","class":"docommand.do.Do","action":"cleanup","method":"DUMMY"}'

reply:

    {"instid": "a682645da85e79e4", "stat": "ok", "data": true} 
