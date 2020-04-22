# ismyarchverifiedyet

**:construction: The results of this script and the script itself are experimental :construction:**

Queries results from [rebuilderd](https://github.com/kpcyrd/rebuilderd) instances and compares it to your local arch system.

## Usage

    ./ismyarchverifiedyet.py

Packages with 0 successful rebuilds are highlighted red, packages that have been successfully rebuilt are yellow, and packages with more than one successful rebuild are displayed green.

## Configuration

You can add additional rebuilders (or remove some of the preconfigured ones) and also tune the threshold of how many rebuilds you want to require.
