package PythonDo;

 use JSON;

 our $script = '/opt/bcs/bin/pydo';
 our $j = JSON->new->ascii->pretty(0)->allow_nonref->allow_blessed->convert_blessed;

 our $AUTOLOAD;

 sub new {
    my $class = shift;
    my $args = shift;
    #print "NEW\n";
    #print "ARGS:$args\n";
    $pyclass = $args->{'class'};
    $pylib = $args->{'lib'};
    $pyargs = $args->{'args'};
    my $self = {
        'lib'=>$pylib,
        'class'=>$pyclass,
        'data'=>{}
    };
    #my $closure = sub {
    #    my $field = shift;
    #    if (@_) { $self->{$field} = shift }
    #        return $self->{$field};
    #};
    #my $self = bless $closure, $class;
    bless $self, $class;
    #print "BLESSED\n";
    unless ($args) { return $self; }
    my $res = $self->__runmethod('new',$pyargs);
    $self->{'methods'} = $res->{'methods'};
    $self->__createNewSubs();
    return $self;
 }

 sub AUTOLOAD {
    my $self = shift;
    my $field = $AUTOLOAD;
    $field =~ s/.*://;
    #print "$field(".join(',',@_).")\n";
    if (@_) {
        my $res = $self->__setProp($field,@_);
        if ($res->{'stat'} == 'ok') {
            return $res->{'data'};
        }
        return $res->{'msg'};
    } else {
        my $res = $self->__getProp($field);
        if ($res->{'stat'} == 'ok') {
            return $res->{'data'};
        }
        return $res->{'msg'};
    }
 }

 sub DESTROY {
    my $self = shift;
    #print "__getProp(".join(',',@_)."):\n";
    my $clmethod = 'DUMMY';
    my $args = {};
    #
    # Setup the initial Instance Args
    #
    if ($self->{'instid'}) {
        $args->{'instid'} = $self->{'instid'};
    }
    #
    #  Setup the class and libs
    #   (so pydo can load it)
    #  These are stored in $self
    #   because they won't change
    #
    $args->{'class'} = $self->{'class'};
    if ($self->{'lib'}) { 
        $args->{'lib'} = $self->{'lib'};
    }
    #
    # Set the action to 'method'
    #
    $args->{'action'} = 'cleanup';
    $args->{'method'} = $clmethod;
    $jargs = $j->encode($args);
    my $cmd = $script." '".$jargs."'";
    my $res = $self->__execute($cmd);
    #print "running $cmd\n";
    #my $jres = `$cmd`;
    #print "\t$jres\n";
    #chomp ($jres);
    #my $res = $j->decode($jres);
    return $res;
 }

 sub __createNewSubs {
    my $self = shift;
    foreach my $mname (@{$self->{'methods'}}) {
        *{ $mname } = sub { 
            my $self = shift;
            my @args = @_;
            $res = $self->__runmethod($mname,\@args);
            if ($res->{'stat'} == 'ok') {
                return $res->{'data'};
            }
            return $res->{'msg'};
        };
    }
 }

 sub __getProp {
    my $self = shift;
    #print "__getProp(".join(',',@_)."):\n";
    my $clprop = shift;
    my $clmethod = 'DUMMY';
    my $args = {};
    #
    # Setup the initial Instance Args
    #
    if ($self->{'instid'}) {
        $args->{'instid'} = $self->{'instid'};
    }
    #
    #  Setup the class and libs
    #   (so pydo can load it)
    #  These are stored in $self
    #   because they won't change
    #
    $args->{'class'} = $self->{'class'};
    if ($self->{'lib'}) { 
        $args->{'lib'} = $self->{'lib'};
    }
    #
    # Set the action to 'method'
    #
    $args->{'action'} = 'get';
    $args->{'method'} = $clmethod;
    $args->{'prop'} = $clprop;
    $jargs = $j->encode($args);
    my $cmd = $script." '".$jargs."'";
    my $res = $self->__execute($cmd);
    #print "running $cmd\n";
    #my $jres = `$cmd`;
    #print "\t$jres\n";
    #chomp ($jres);
    #my $res = $j->decode($jres);
    return $res;
 }

 sub __setProp {
    my $self = shift;
    #print "__setProp(".join(',',@_)."):\n";
    my $clprop = shift;
    my $clvalue = shift;
    my $clmethod = 'DUMMY';
    my $args = {};
    #
    # Setup the initial Instance Args
    #
    if ($self->{'instid'}) {
        $args->{'instid'} = $self->{'instid'};
    }
    #
    #  Setup the class and libs
    #   (so pydo can load it)
    #  These are stored in $self
    #   because they won't change
    #
    $args->{'class'} = $self->{'class'};
    if ($self->{'lib'}) { 
        $args->{'lib'} = $self->{'lib'};
    }
    #
    # Set the action to 'method'
    #
    $args->{'action'} = 'set';
    $args->{'method'} = $clmethod;
    $args->{'prop'} = $clprop;
    $args->{'value'} = $clvalue;
    $jargs = $j->encode($args);
    my $cmd = $script." '".$jargs."'";
    my $res = $self->__execute($cmd);
    #print "running $cmd\n";
    #my $jres = `$cmd`;
    ##print "\t$jres\n";
    #chomp ($jres);
    #my $res = $j->decode($jres);
    return $res;
 }

 sub __runmethod {
    #print "__runmethod:\n";
    my $self = shift;
    my $clmethod = shift;
    my $clargs = shift;
    my $args = {};
    #
    # Setup the initial Instance Args
    #
    if ($self->{'instid'}) {
        $args->{'instid'} = $self->{'instid'};
    }
    #
    #  Setup the class and libs
    #   (so pydo can load it)
    #  These are stored in $self
    #   because they won't change
    #
    $args->{'class'} = $self->{'class'};
    if ($self->{'lib'}) { 
        $args->{'lib'} = $self->{'lib'};
    }
    #
    # Set the action to 'method'
    #
    $args->{'action'} = 'method';
    #
    # Setup the methods and args
    #
    $args->{'method'} = $clmethod;
    if ($clargs) { 
        $args->{'args'} = $clargs;
    }
    $jargs = $j->encode($args);
    my $cmd = $script." '".$jargs."'";
    my $res = $self->__execute($cmd);
    #print "running $cmd\n";
    #my $jres = `$cmd`;
    #print "\t$jres\n";
    #chomp ($jres);
    #my $res = $j->decode($jres);
    if (!$self->{'instid'}) {
        $self->{'instid'} = $res->{'instid'};
    }
    return $res;
 }

 sub __execute {
    my $self = shift;
    my $cmd = shift;
    #print "\nCMD: $cmd\n";
    my $jres = `$cmd`;
    #print "REP: $jres\n";
    chomp ($jres);
    my $res = $j->decode($jres);
    if ($res->{'classchat'}) {
        print $res->{'classchat'}
    }
    return $res;
 }


1;

__END__

=head1 NAME

PythonDo.pm - PERL module to implement python classes
pydo.py - python script used to do the implementation

=head1 DESCRIPTION

https://github.com/chepazzo/pythondo

Designed to allow other programming languages to access python classes
This python script is meant to be executed by any language (even bash).
It will take as args (encoded as a json string):
- class (absolute path)
- method
- args

It will return:
- output (return value) of method encoded as a json string
- instance id to be use to run methods on the same instance

Obviously, this works best with static classes, but hopefully, it will 
work out for some subset of instance classes as well.

The idea is to make this work like RPC/API on a web server, which would make 
adding functionality to use such an API relatively simple.

=head1 EXAMPLE Use

#!/opt/bcs/bin/perl

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

=head1 Under the Covers

  my $do = new PythonDo({'class'=>'docommand.do.Do','args'=>{'debug':\0,'devices'=>['myswitch.net.com'],'commands'=>['show version']}});

executes

  /opt/bin/pydo.py '{"lib":"/opt/lib/py","class":"docommand.do.Do","method":"new","args":{"debug":false,"commands":["show version"],"devices":["myswitch.net.com"]},"action":"method"}'

which does the equivalent of:

  import sys
  sys.path.append("/opt/lib/py")
  from docommand.do import Do
  n = Do(debug=False,commands=["show version"],devices=["myswitch.net.com"])
  with open('/tmp'+instid+'.data','w') as fw:
    pickle.dump(n,fw,-1)
  
after which, saves the instance as a pickle to disk and returns a json string like:

  {"instid": "e45e2609182447eb", "stat": "ok", "classchat": "", "data": true, "methods": ["_setup_work", "generate_ios_cmd", "run", "_stop", "_setup_callback", "_Config__children_with_namespace", "eb", "ios_parse", "_decrement_connections", "junos_parse", "set_data", "_add_worker", "_start", "generate_junos_cmd", "__init__"]}

where:
  'stat' : status.  'ok' means it was good.  'fail' means that something failed the details of which should be stored in err.msg
  'classchat' : contains the output of 'print' statements executed by the python class
  'instid' : contains the unique_id used for the next method on the instance.
  'methods' : contains a list of the instance's methods

which is parsed by PythonDo.pm and returns to the calling program a PERL blessed object that has inherited any of the listed methods.

Calling 

  $do->run()

executes

  /opt/bin/pydo.py '{"instid":"e45e2609182447eb","args":[],"action":"method","method":"run","class":"docommand.do.Config"}'

which does the equivalent of:

  import pickle
  with open('/tmp'+instid+'.data','w') as fw:
    n = pickle.load(fr)
  retval = n.run()

etc, etc, etc
