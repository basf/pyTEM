import argparse


def my_func(verbose: bool = False):
    if verbose:
        print("My function called with verbose=True.")
    else:
        print("My function called with verbose=False.")


def script_entry():
    print("-- calling from script_entry --")
    parser = argparse.ArgumentParser(description='Description of your program')
    parser.add_argument("-v", "--verbose", help="increase output verbosity",
                        action="store_true")
    args = parser.parse_args()
    print("args: " + str(args))
    my_func(verbose=args.verbose)


if __name__ == "__main__":
    print("-- calling from main --")
    my_func(verbose=True)
