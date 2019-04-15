#!/usr/bin/awk -f

BEGIN {

}

/^.*INFO -- Metric Name:/ {
    line = $0
    
    sub("^.*INFO -- Metric Name: ", "", line)
    split(line, metr_tag_val, /\|\|\|/)
    sub("Tags: ", "", metr_tag_val[2])
    sub("Value:", "", metr_tag_val[3])

    if (metr_tag_val[3] ~ /{/) {
        printf "%-40s %-90s\n", metr_tag_val[1], metr_tag_val[2]
        sub(/^\s*/, "", metr_tag_val[3])
        print metr_tag_val[3]
    } else 
        printf "%-40s %-90s %-25s\n", metr_tag_val[1], metr_tag_val[2], metr_tag_val[3]

#    for (k in metr_tag_val)
#        print metr_tag_val[k]

    next
}

$0 !~ /^\d*.*INFO -- / {
    print $0
}