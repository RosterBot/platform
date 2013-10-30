
def compare_versions(minimum, current, program_name):
    # test the version of the program, we are aiming to require greater than or equal to the minimum version
    print "\t" + program_name + " is installed, checking version..."
    from distutils.version import StrictVersion
    if StrictVersion(current) < StrictVersion(minimum):
        raise Exception("\t" + program_name + " is installed, but version is not " + minimum + ", we require version " +
                        current)
    # all good.
    print "\tGood, " + current + " is greater than " + minimum

def module_version_check(minimum_version, program_name, readable_name=None):
    """Tests for the existence of a particular version of a library."""
    printable_name = program_name
    if readable_name:
        printable_name = readable_name
    print "...Checking if " + printable_name + " library is installed..."
    try:
        module = __import__(program_name)
    except ImportError:
        raise Exception("\t" + printable_name + " is missing. Install it.")
    compare_versions(minimum_version, module.__version__, printable_name)
