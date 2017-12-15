#!/usr/bin/env bash

function printUsage() {
    echo "Usage: $execName [ -h ] [ -o <outputFile> ] <inputFile>" 1>&2 
}

execName=$0
outputFile=""

while getopts ":o:h" opt; do
    case $opt in
        o)
            outputFile=$OPTARG
            ;;
        \?)
            printUsage
            exit 1
            ;;
        h)
            printUsage
            exit 0
            ;;
        :)
            printUsage
            exit 1
            ;;
    esac
done

shift $((OPTIND-1))    

if [[ $# -ne 1 ]]; then
    printUsage
    exit 1
fi

inputFile=$1

read -r -d '' scriptVariable << 'EOF'
BEGIN {
    # this never exists and will never match until the real prompt is found
    devicePrompt = "deadbeafdeadbeaf"
    deviceOutput = ""
    cmd = ""
    # collecting not started until collecting is set
    collecting = 0
}

#2017-11-01 23:35:18,094 25345 DEBUG - New prompt set: FGVMUL0000117288 #
/New prompt set:/ {
    # if devicePrompt is already set, skip
    input = $0
    devicePrompt = gensub(/.+New prompt set: (.+)/, "\\1", "g", input)
    gsub(/\[/, "\\[", devicePrompt)
    gsub(/\]/, "\\]", devicePrompt)
}

#2017-11-01 23:35:32,580 39831 DEBUG - 10.10.8.59 (10.10.8.59): Running SSH commmand: fnsysctl ifconfig
/Running SSH commmand:/ {
    collecting = 1
    input = $0
    cmd = gensub(/.+Running SSH commmand: (.+)/, "\\1", "g", input)
}

#2017-11-01 23:35:32,621 39872 DEBUG - Adding to buffer: port1  
/Adding to buffer:/ {
    # wait until after collecting is set
    if (collecting == 0) {
        next
    }
    input = $0
    buf = gensub(/.+Adding to buffer: (.+)/, "\\1", "g", input)
    print buf  
}

$0 ~ devicePrompt {
    # device prompt shows up, this means the current command is done
    collecting = 0
}

END {
    if (length(cmd) == 0) {
        print "Failed to find command. CommandRunner should be run in verbose mode"
    }
}
EOF

# awk print add \r\n at the end of each line, remove them 
collectedStr=$(awk "$scriptVariable" $inputFile | tr -d '\r\n')
# if no outpitFile specified, dump it to stdout
if [ -z $outputFile ]; then
    printf "$collectedStr"
else
    printf "$collectedStr" > $outputFile
fi